"""Opt-in PostgreSQL acceptance for Source immutable-read queries."""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.modules.source_evidence.application.association_errors import (
    SourceAssociationError,
)
from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceError,
)
from ai_ecommerce_agent.modules.source_evidence.application.query_services import (
    SourceEvidenceQueryApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceAssociationMembershipState,
    SourceProcessingStatus,
    SourceVersion,
    SourceVersionProcessing,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.uow import (
    SourceEvidencePostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.source_evidence.public import (
    GetSourceAssociation,
    GetSourceVersion,
    SourceAssociationSnapshot,
    SourceVersionSnapshot,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceId,
    SourceVersionId,
    TaskId,
    VersionNumber,
)

pytestmark = [pytest.mark.integration, pytest.mark.live]

if os.environ.get("MVP0_RUN_SOURCE_EVIDENCE_QUERY_APPLICATION") != "1":
    pytest.skip(
        "set MVP0_RUN_SOURCE_EVIDENCE_QUERY_APPLICATION=1 for the opt-in "
        "Source Evidence query suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_010c5_source_query_app"
URL_ENV = "MVP0_SOURCE_EVIDENCE_QUERY_APPLICATION_DATABASE_URL"
DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)
NOW = datetime(2026, 8, 9, 1, 0, tzinfo=UTC)


def _database_url() -> str:
    return os.environ.get(URL_ENV, DEFAULT_URL).strip()


def _alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", SCHEMA)
    config.set_main_option("version_table_schema", SCHEMA)
    return config


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    """Own one fixed schema, upgrade it to Alembic head, then clean it."""

    database_url = _database_url()
    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=database_url,
            pool_size=4,
            max_overflow=0,
            pool_timeout=5,
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))
    try:
        command.upgrade(_alembic_config(database_url), "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        with engine.connect() as connection:
            remaining = connection.scalar(
                text("SELECT count(*) FROM pg_namespace WHERE nspname = :schema"),
                {"schema": SCHEMA},
            )
        assert remaining == 0
        engine.dispose()


def _factory(engine: Engine) -> SourceEvidencePostgresUnitOfWorkFactory:
    return SourceEvidencePostgresUnitOfWorkFactory.from_engine(engine, schema=SCHEMA)


def _version(suffix: str) -> SourceVersion:
    return SourceVersion.create(
        SourceVersionId(f"source-version-query-{suffix}"),
        SourceId(f"source-query-{suffix}"),
        VersionNumber(2),
    )


def _processing(version: SourceVersion) -> SourceVersionProcessing:
    return SourceVersionProcessing(
        source_version_id=version.source_version_id,
        status=SourceProcessingStatus.READY,
        revision=Revision(3),
        failure_summary=None,
        updated_at=NOW,
    )


def _association(
    task_id: TaskId, version: SourceVersion, suffix: str
) -> TaskSourceAssociation:
    return TaskSourceAssociation(
        source_association_id=SourceAssociationId(f"association-query-{suffix}"),
        task_id=task_id,
        source_id=version.source_id,
        source_version_id=version.source_version_id,
        membership_state=SourceAssociationMembershipState.REMOVED,
        revision=Revision(4),
        replaced_by_association_id=None,
    )


def _insert_task(engine: Engine, task_id: TaskId) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                f'INSERT INTO "{SCHEMA}"."task_management_tasks" '
                "(task_id, task_name, product_category, promotion_goal, "
                "task_status, revision, updated_at) "
                "VALUES (:task_id, :name, :category, :goal, 'draft', 0, :updated_at)"
            ),
            {
                "task_id": str(task_id),
                "name": "Query task",
                "category": "backpack",
                "goal": "query immutable source",
                "updated_at": NOW,
            },
        )


def _seed_version(
    factory: SourceEvidencePostgresUnitOfWorkFactory, version: SourceVersion
) -> None:
    with factory() as uow:
        uow.source_versions.add(version)
        uow.source_version_processing.add(_processing(version))
        uow.commit()


def _seed_association(
    engine: Engine,
    factory: SourceEvidencePostgresUnitOfWorkFactory,
    task_id: TaskId,
    version: SourceVersion,
    suffix: str,
) -> TaskSourceAssociation:
    _insert_task(engine, task_id)
    association = _association(task_id, version, suffix)
    with factory() as uow:
        uow.source_versions.add(version)
        uow.source_associations.add(association)
        uow.commit()
    return association


def _count_rows(engine: Engine, table: str) -> int:
    with engine.connect() as connection:
        return int(
            connection.scalar(text(f'SELECT count(*) FROM "{SCHEMA}"."{table}"'))
        )


def _checked_out(engine: Engine) -> int:
    return int(cast(Any, engine.pool).checkedout())


def test_source_version_query_reads_composite_current_truth_and_releases_connection(
    postgres_engine: Engine,
) -> None:
    version = _version("composite")
    factory = _factory(postgres_engine)
    _seed_version(factory, version)

    result = SourceEvidenceQueryApplicationService(factory).get_source_version(
        GetSourceVersion(version.source_version_id)
    )

    assert isinstance(result, SourceVersionSnapshot)
    assert result.source_id == version.source_id
    assert result.source_version_id == version.source_version_id
    assert result.version_number == VersionNumber(2)
    assert result.processing_status.value == "ready"
    assert result.processing_revision == Revision(3)
    assert result.updated_at == NOW
    assert _checked_out(postgres_engine) == 0


def test_source_version_query_missing_identity_is_typed_not_found_and_releases(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    missing = SourceVersionId("source-version-query-missing")

    with pytest.raises(SourceEvidenceError) as raised:
        SourceEvidenceQueryApplicationService(factory).get_source_version(
            GetSourceVersion(missing)
        )

    assert raised.value.error_code == "not_found"
    assert raised.value.relevant_reference == missing
    assert _checked_out(postgres_engine) == 0


def test_source_version_query_missing_processing_is_typed_not_found(
    postgres_engine: Engine,
) -> None:
    version = _version("missing-processing")
    factory = _factory(postgres_engine)
    with factory() as uow:
        uow.source_versions.add(version)
        uow.commit()

    with pytest.raises(SourceEvidenceError) as raised:
        SourceEvidenceQueryApplicationService(factory).get_source_version(
            GetSourceVersion(version.source_version_id)
        )

    assert raised.value.error_code == "not_found"
    assert raised.value.relevant_reference == version.source_version_id
    assert _checked_out(postgres_engine) == 0


def test_association_query_reads_membership_snapshot_without_durable_write(
    postgres_engine: Engine,
) -> None:
    task_id = TaskId("task-query-association")
    version = _version("association")
    factory = _factory(postgres_engine)
    association = _seed_association(
        postgres_engine, factory, task_id, version, "association"
    )
    before = _count_rows(postgres_engine, "source_evidence_task_source_associations")

    result = SourceEvidenceQueryApplicationService(factory).get_source_association(
        GetSourceAssociation(task_id, association.source_association_id)
    )

    assert isinstance(result, SourceAssociationSnapshot)
    assert result.source_association_id == association.source_association_id
    assert result.task_id == task_id
    assert result.membership_state is SourceAssociationMembershipState.REMOVED
    assert result.revision == Revision(4)
    assert (
        _count_rows(postgres_engine, "source_evidence_task_source_associations")
        == before
    )
    assert _checked_out(postgres_engine) == 0


def test_association_query_foreign_task_is_typed_ownership_conflict(
    postgres_engine: Engine,
) -> None:
    task_id = TaskId("task-query-owner")
    version = _version("foreign-task")
    factory = _factory(postgres_engine)
    association = _seed_association(
        postgres_engine, factory, task_id, version, "foreign-task"
    )

    with pytest.raises(SourceAssociationError) as raised:
        SourceEvidenceQueryApplicationService(factory).get_source_association(
            GetSourceAssociation(
                TaskId("task-query-foreign"), association.source_association_id
            )
        )

    assert raised.value.error_code == "ownership_conflict"
    assert raised.value.relevant_reference == association.source_association_id
    assert _checked_out(postgres_engine) == 0


def test_association_query_missing_is_typed_not_found(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    missing = SourceAssociationId("association-query-missing")

    with pytest.raises(SourceAssociationError) as raised:
        SourceEvidenceQueryApplicationService(factory).get_source_association(
            GetSourceAssociation(TaskId("task-query-missing"), missing)
        )

    assert raised.value.error_code == "not_found"
    assert raised.value.relevant_reference == missing
    assert _checked_out(postgres_engine) == 0
