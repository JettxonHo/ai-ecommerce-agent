"""Opt-in real PostgreSQL acceptance for the Source Evidence adapter."""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, event, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceConstraintError,
    SourceEvidenceOwnershipError,
    SourceEvidenceRevisionConflictError,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceVersion,
    SourceVersionProcessing,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.uow import (
    SourceEvidencePostgresUnitOfWorkFactory,
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

if os.environ.get("MVP0_RUN_SOURCE_EVIDENCE_POSTGRES") != "1":
    pytest.skip(
        "set MVP0_RUN_SOURCE_EVIDENCE_POSTGRES=1 for the opt-in Source Evidence suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_010b2c_source_adapter"
URL_ENV = "MVP0_SOURCE_EVIDENCE_DATABASE_URL"
DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)


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
    """Own and clean one schema upgraded through Business Alembic 0003."""

    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=_database_url(), pool_size=4, max_overflow=0, pool_timeout=3
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))
    try:
        command.upgrade(_alembic_config(_database_url()), "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        engine.dispose()


def _factory(engine: Engine) -> SourceEvidencePostgresUnitOfWorkFactory:
    return SourceEvidencePostgresUnitOfWorkFactory.from_engine(engine, schema=SCHEMA)


def _version(
    source_suffix: str = "one", version_suffix: str = "one", number: int = 1
) -> SourceVersion:
    return SourceVersion.create(
        SourceVersionId(f"source-version-{version_suffix}"),
        SourceId(f"source-{source_suffix}"),
        VersionNumber(number),
    )


def _processing(version: SourceVersion) -> SourceVersionProcessing:
    return SourceVersionProcessing.create(
        version.source_version_id,
        updated_at=datetime(2026, 8, 9, 1, 0, tzinfo=UTC),
    )


def _insert_task(engine: Engine, task_id: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                f'INSERT INTO "{SCHEMA}"."task_management_tasks" '
                "(task_id, task_name, product_category, promotion_goal, "
                "task_status, revision, updated_at) "
                "VALUES (:task_id, :name, :category, :goal, 'draft', 0, :updated_at)"
            ),
            {
                "task_id": task_id,
                "name": "City commute pack",
                "category": "backpack",
                "goal": "commute positioning",
                "updated_at": datetime(2026, 8, 9, tzinfo=UTC),
            },
        )


def _count(engine: Engine, table: str, column: str, value: str) -> int:
    with engine.connect() as connection:
        return int(
            connection.scalar(
                text(
                    f'SELECT count(*) FROM "{SCHEMA}"."{table}" '
                    f'WHERE "{column}" = :value'
                ),
                {"value": value},
            )
        )


def test_roundtrip_commit_visibility_and_rollback(postgres_engine: Engine) -> None:
    version = _version()
    processing = _processing(version)
    factory = _factory(postgres_engine)
    with factory() as uow:
        uow.source_versions.add(version)
        uow.source_version_processing.add(processing)
        uow.commit()

    with factory() as uow:
        assert uow.source_versions.get(version.source_version_id) == version
        assert (
            uow.source_version_processing.get(version.source_version_id) == processing
        )
        uow.commit()

    rolled_back = _version(source_suffix="rollback", version_suffix="rollback")
    with factory() as uow:
        uow.source_versions.add(rolled_back)
    with factory() as uow:
        assert uow.source_versions.get(rolled_back.source_version_id) is None
        assert (
            _count(
                postgres_engine,
                "source_evidence_sources",
                "source_id",
                str(rolled_back.source_id),
            )
            == 0
        )
        uow.commit()


def test_source_anchor_and_version_are_atomic_on_version_failure(
    postgres_engine: Engine,
) -> None:
    existing = _version(source_suffix="existing", version_suffix="existing")
    factory = _factory(postgres_engine)
    with factory() as uow:
        uow.source_versions.add(existing)
        uow.commit()

    conflicting = SourceVersion.create(
        existing.source_version_id,
        SourceId("source-anchor-must-rollback"),
        VersionNumber(1),
    )
    with pytest.raises(SourceEvidenceConstraintError):
        with factory() as uow:
            uow.source_versions.add(conflicting)

    assert (
        _count(
            postgres_engine,
            "source_evidence_sources",
            "source_id",
            str(conflicting.source_id),
        )
        == 0
    )


def test_processing_cas_has_one_winner_across_independent_uows(
    postgres_engine: Engine,
) -> None:
    version = _version(source_suffix="processing-cas", version_suffix="processing-cas")
    factory = _factory(postgres_engine)
    with factory() as uow:
        uow.source_versions.add(version)
        uow.source_version_processing.add(_processing(version))
        uow.commit()

    first, second = factory(), factory()
    with first as left, second as right:
        left_value = left.source_version_processing.get(version.source_version_id)
        right_value = right.source_version_processing.get(version.source_version_id)
        assert left_value is not None and right_value is not None
        left_changed = left_value.start_processing(
            expected_revision=Revision(0), updated_at=left_value.updated_at
        )
        right_changed = right_value.start_processing(
            expected_revision=Revision(0), updated_at=right_value.updated_at
        )
        left.source_version_processing.save(left_changed, expected_revision=Revision(0))
        left.commit()
        with pytest.raises(SourceEvidenceRevisionConflictError):
            right.source_version_processing.save(
                right_changed, expected_revision=Revision(0)
            )
        right.rollback()


def test_association_cas_has_one_winner_across_independent_uows(
    postgres_engine: Engine,
) -> None:
    task_id = "task-association-cas"
    _insert_task(postgres_engine, task_id)
    version = _version(
        source_suffix="association-cas", version_suffix="association-cas"
    )
    association = TaskSourceAssociation.create(
        SourceAssociationId("association-cas"), TaskId(task_id), version
    )
    factory = _factory(postgres_engine)
    with factory() as uow:
        uow.source_versions.add(version)
        uow.source_associations.add(association)
        uow.commit()

    first, second = factory(), factory()
    with first as left, second as right:
        left_value = left.source_associations.get(association.source_association_id)
        right_value = right.source_associations.get(association.source_association_id)
        assert left_value is not None and right_value is not None
        left_changed = left_value.remove(expected_revision=Revision(0))
        right_changed = right_value.remove(expected_revision=Revision(0))
        left.source_associations.save(left_changed, expected_revision=Revision(0))
        left.commit()
        with pytest.raises(SourceEvidenceRevisionConflictError):
            right.source_associations.save(right_changed, expected_revision=Revision(0))
        right.rollback()


def test_legal_replacement_adds_new_then_cas_saves_old_atomically(
    postgres_engine: Engine,
) -> None:
    task_id = "task-replacement"
    _insert_task(postgres_engine, task_id)
    old_version = _version(source_suffix="replacement", version_suffix="old")
    new_version = _version(source_suffix="replacement", version_suffix="new", number=2)
    old_association = TaskSourceAssociation.create(
        SourceAssociationId("association-old"), TaskId(task_id), old_version
    )
    factory = _factory(postgres_engine)
    with factory() as uow:
        uow.source_versions.add(old_version)
        uow.source_versions.add(new_version)
        uow.source_associations.add(old_association)
        uow.commit()

    replacement = old_association.replace(
        SourceAssociationId("association-new"),
        new_version,
        expected_revision=Revision(0),
    )
    with factory() as uow:
        uow.source_associations.add(replacement.active_association)
        uow.source_associations.save(
            replacement.replaced_association, expected_revision=Revision(0)
        )
        uow.commit()

    with factory() as uow:
        current_old = uow.source_associations.get(old_association.source_association_id)
        current_new = uow.source_associations.get(
            replacement.active_association.source_association_id
        )
        assert current_old == replacement.replaced_association
        assert current_new == replacement.active_association
        uow.commit()

    failed_new = TaskSourceAssociation.create(
        SourceAssociationId("association-failed-new"), TaskId(task_id), old_version
    )
    with pytest.raises(SourceEvidenceRevisionConflictError):
        with factory() as uow:
            uow.source_associations.add(failed_new)
            uow.source_associations.save(
                replacement.replaced_association, expected_revision=Revision(0)
            )
    assert (
        _count(
            postgres_engine,
            "source_evidence_task_source_associations",
            "source_association_id",
            str(failed_new.source_association_id),
        )
        == 0
    )


def test_owner_and_generic_integrity_failures_are_typed(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    missing_processing = SourceVersionProcessing.create(
        SourceVersionId("missing-owner-version"),
        updated_at=datetime(2026, 8, 9, tzinfo=UTC),
    )
    with pytest.raises(SourceEvidenceOwnershipError) as owner:
        with factory() as uow:
            uow.source_version_processing.add(missing_processing)
    assert owner.value.safe_context["constraint"] == (
        "fk_source_evidence_source_version_processing_version_owner"
    )

    duplicate = _version(source_suffix="duplicate", version_suffix="duplicate")
    with factory() as uow:
        uow.source_versions.add(duplicate)
        uow.commit()
    with pytest.raises(SourceEvidenceConstraintError):
        with factory() as uow:
            uow.source_versions.add(duplicate)


def test_fresh_uow_sessions_check_in_connections(postgres_engine: Engine) -> None:
    checkins = 0

    def on_checkin(*_: object) -> None:
        nonlocal checkins
        checkins += 1

    event.listen(postgres_engine, "checkin", on_checkin)
    try:
        factory = _factory(postgres_engine)
        first, second = factory(), factory()
        assert first is not second
        with first as uow:
            assert uow.source_versions.get(SourceVersionId("not-present")) is None
            uow.commit()
        first_checkins = checkins
        with second as uow:
            assert uow.source_versions.get(SourceVersionId("still-not-present")) is None
            uow.commit()
        assert first_checkins >= 1
        assert checkins > first_checkins
    finally:
        event.remove(postgres_engine, "checkin", on_checkin)
