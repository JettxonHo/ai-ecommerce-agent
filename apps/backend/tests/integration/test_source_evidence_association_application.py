"""Opt-in PostgreSQL acceptance for Source association application use cases."""

from __future__ import annotations

import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier
from types import TracebackType
from typing import Any, Self, cast

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.application.ports import UnitOfWorkState
from ai_ecommerce_agent.modules.source_evidence.application import (
    association_errors,
    association_services,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceEvidenceUnitOfWork,
    SourceVersionProcessingRepositoryPort,
    SourceVersionRepositoryPort,
    TaskSourceAssociationRepositoryPort,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceAssociationMembershipState,
    SourceVersion,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.uow import (
    SourceEvidencePostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.source_evidence.public import (
    RemoveSourceAssociation,
    ReplaceSourceAssociation,
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

if os.environ.get("MVP0_RUN_SOURCE_EVIDENCE_ASSOCIATION_APPLICATION") != "1":
    pytest.skip(
        "set MVP0_RUN_SOURCE_EVIDENCE_ASSOCIATION_APPLICATION=1 for the opt-in "
        "Source association application suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_010c4_source_assoc_app"
URL_ENV = "MVP0_SOURCE_EVIDENCE_ASSOCIATION_DATABASE_URL"
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
            pool_size=6,
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
                "name": "City commute pack",
                "category": "backpack",
                "goal": "commute positioning",
                "updated_at": NOW,
            },
        )


def _version(
    suffix: str, *, source_suffix: str = "same", number: int = 1
) -> SourceVersion:
    return SourceVersion.create(
        SourceVersionId(f"source-version-{suffix}"),
        SourceId(f"source-{source_suffix}"),
        VersionNumber(number),
    )


def _seed(
    engine: Engine,
    task_id: TaskId,
    factory: SourceEvidencePostgresUnitOfWorkFactory,
    versions: tuple[SourceVersion, ...],
    association: TaskSourceAssociation,
) -> None:
    _insert_task(engine, task_id)
    with factory() as uow:
        for version in versions:
            uow.source_versions.add(version)
        uow.source_associations.add(association)
        uow.commit()


def _read_association(
    factory: SourceEvidencePostgresUnitOfWorkFactory,
    association_id: SourceAssociationId,
) -> TaskSourceAssociation | None:
    with factory() as uow:
        value = uow.source_associations.get(association_id)
        uow.commit()
        return value


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


def _checked_out(engine: Engine) -> int:
    return cast(Any, engine.pool).checkedout()


class _BarrierAssociationRepository:
    def __init__(
        self,
        delegate: TaskSourceAssociationRepositoryPort,
        barrier: Barrier,
    ) -> None:
        self._delegate = delegate
        self._barrier = barrier

    def get(
        self, source_association_id: SourceAssociationId
    ) -> TaskSourceAssociation | None:
        value = self._delegate.get(source_association_id)
        self._barrier.wait(timeout=10)
        return value

    def add(self, association: TaskSourceAssociation) -> None:
        self._delegate.add(association)

    def save(
        self,
        association: TaskSourceAssociation,
        *,
        expected_revision: Revision,
    ) -> None:
        self._delegate.save(association, expected_revision=expected_revision)


class _BarrierUow:
    def __init__(self, delegate: SourceEvidenceUnitOfWork, barrier: Barrier) -> None:
        self._delegate = delegate
        self._source_associations = _BarrierAssociationRepository(
            delegate.source_associations, barrier
        )

    @property
    def state(self) -> UnitOfWorkState:
        return self._delegate.state

    def __enter__(self) -> Self:
        self._delegate.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._delegate.__exit__(exc_type, exc_value, traceback)

    def commit(self) -> None:
        self._delegate.commit()

    def rollback(self) -> None:
        self._delegate.rollback()

    def close(self) -> None:
        self._delegate.close()

    @property
    def source_versions(self) -> SourceVersionRepositoryPort:
        return self._delegate.source_versions

    @property
    def source_version_processing(self) -> SourceVersionProcessingRepositoryPort:
        return self._delegate.source_version_processing

    @property
    def source_associations(self) -> TaskSourceAssociationRepositoryPort:
        return self._source_associations


class _BarrierFactory:
    def __init__(
        self,
        factory: SourceEvidencePostgresUnitOfWorkFactory,
        barrier: Barrier,
    ) -> None:
        self._factory = factory
        self._barrier = barrier

    def __call__(self) -> SourceEvidenceUnitOfWork:
        return cast(
            SourceEvidenceUnitOfWork, _BarrierUow(self._factory(), self._barrier)
        )


class _CommitFailureUow:
    def __init__(self, delegate: SourceEvidenceUnitOfWork) -> None:
        self._delegate = delegate

    @property
    def state(self) -> UnitOfWorkState:
        return self._delegate.state

    def __enter__(self) -> Self:
        self._delegate.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._delegate.__exit__(exc_type, exc_value, traceback)

    def commit(self) -> None:
        from ai_ecommerce_agent.modules.source_evidence.application.errors import (
            SourceEvidencePersistenceError,
        )

        raise SourceEvidencePersistenceError()

    def rollback(self) -> None:
        self._delegate.rollback()

    def close(self) -> None:
        self._delegate.close()

    @property
    def source_versions(self) -> SourceVersionRepositoryPort:
        return self._delegate.source_versions

    @property
    def source_version_processing(self) -> SourceVersionProcessingRepositoryPort:
        return self._delegate.source_version_processing

    @property
    def source_associations(self) -> TaskSourceAssociationRepositoryPort:
        return self._delegate.source_associations


class _CommitFailureFactory:
    def __init__(self, factory: SourceEvidencePostgresUnitOfWorkFactory) -> None:
        self._factory = factory

    def __call__(self) -> SourceEvidenceUnitOfWork:
        return cast(SourceEvidenceUnitOfWork, _CommitFailureUow(self._factory()))


def test_remove_commit_roundtrip_preserves_physical_row(
    postgres_engine: Engine,
) -> None:
    task_id = TaskId("task-association-remove")
    version = _version("remove")
    association_id = SourceAssociationId("association-remove")
    association = TaskSourceAssociation.create(association_id, task_id, version)
    factory = _factory(postgres_engine)
    _seed(postgres_engine, task_id, factory, (version,), association)

    result = association_services.SourceAssociationApplicationService(
        factory
    ).remove_source_association(
        RemoveSourceAssociation(task_id, association_id, Revision.initial())
    )

    assert result.membership_state is SourceAssociationMembershipState.REMOVED
    assert result.revision == Revision(1)
    stored = _read_association(factory, association_id)
    assert stored is not None
    assert stored.membership_state is SourceAssociationMembershipState.REMOVED
    assert (
        _count(
            postgres_engine,
            "source_evidence_task_source_associations",
            "source_association_id",
            str(association_id),
        )
        == 1
    )
    assert _checked_out(postgres_engine) == 0


def test_replace_commits_old_replaced_and_new_active_with_ordered_snapshot(
    postgres_engine: Engine,
) -> None:
    task_id = TaskId("task-association-replace")
    old_version = _version("replace-old", source_suffix="replace", number=1)
    new_version = _version("replace-new", source_suffix="replace", number=2)
    old_id = SourceAssociationId("association-replace-old")
    new_id = SourceAssociationId("association-replace-new")
    association = TaskSourceAssociation.create(old_id, task_id, old_version)
    factory = _factory(postgres_engine)
    _seed(postgres_engine, task_id, factory, (old_version, new_version), association)

    result = association_services.SourceAssociationApplicationService(
        factory
    ).replace_source_association(
        ReplaceSourceAssociation(
            task_id,
            old_id,
            new_id,
            new_version.source_version_id,
            Revision.initial(),
        )
    )

    assert result.replaced_association.source_association_id == old_id
    assert result.replaced_association.membership_state is (
        SourceAssociationMembershipState.REPLACED
    )
    assert result.active_association.source_association_id == new_id
    assert result.active_association.membership_state is (
        SourceAssociationMembershipState.ACTIVE
    )
    assert (
        _read_association(factory, old_id)
        == association.replace(
            new_id, new_version, expected_revision=Revision.initial()
        ).replaced_association
    )
    stored_new = _read_association(factory, new_id)
    assert stored_new is not None
    assert (
        stored_new.source_association_id
        == result.active_association.source_association_id
    )
    assert stored_new.source_version_id == result.active_association.source_version_id
    assert stored_new.membership_state is result.active_association.membership_state
    assert _checked_out(postgres_engine) == 0


def test_two_commands_race_and_loser_successor_rolls_back(
    postgres_engine: Engine,
) -> None:
    task_id = TaskId("task-association-race")
    old_version = _version("race-old", source_suffix="race", number=1)
    left_version = _version("race-left", source_suffix="race", number=2)
    right_version = _version("race-right", source_suffix="race", number=3)
    old_id = SourceAssociationId("association-race-old")
    left_id = SourceAssociationId("association-race-left")
    right_id = SourceAssociationId("association-race-right")
    association = TaskSourceAssociation.create(old_id, task_id, old_version)
    factory = _factory(postgres_engine)
    _seed(
        postgres_engine,
        task_id,
        factory,
        (old_version, left_version, right_version),
        association,
    )
    barrier_factory = _BarrierFactory(factory, Barrier(2))

    from ai_ecommerce_agent.modules.source_evidence.public import (
        ReplaceSourceAssociation,
    )

    commands = (
        ReplaceSourceAssociation(
            task_id, old_id, left_id, left_version.source_version_id, Revision.initial()
        ),
        ReplaceSourceAssociation(
            task_id,
            old_id,
            right_id,
            right_version.source_version_id,
            Revision.initial(),
        ),
    )

    def invoke(command: ReplaceSourceAssociation) -> tuple[str, object]:
        try:
            return (
                "success",
                association_services.SourceAssociationApplicationService(
                    barrier_factory
                ).replace_source_association(command),
            )
        except association_errors.SourceAssociationError as error:
            return ("error", error)

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(invoke, commands))

    assert [kind for kind, _ in outcomes].count("success") == 1
    assert [kind for kind, _ in outcomes].count("error") == 1
    loser = next(value for kind, value in outcomes if kind == "error")
    assert isinstance(loser, association_errors.SourceAssociationError)
    assert loser.error_code == "revision_conflict"
    assert loser.relevant_reference is old_id
    assert _read_association(factory, old_id) is not None
    old = _read_association(factory, old_id)
    assert (
        old is not None
        and old.membership_state is SourceAssociationMembershipState.REPLACED
    )
    assert (
        _count(
            postgres_engine,
            "source_evidence_task_source_associations",
            "source_association_id",
            str(left_id),
        )
        + _count(
            postgres_engine,
            "source_evidence_task_source_associations",
            "source_association_id",
            str(right_id),
        )
        == 1
    )
    assert _checked_out(postgres_engine) == 0


def test_foreign_task_and_foreign_source_replacements_are_typed_and_durable_zero_write(
    postgres_engine: Engine,
) -> None:
    task_id = TaskId("task-association-owner")
    foreign_task = TaskId("task-association-owner-foreign")
    old_version = _version("owner-old", source_suffix="owner", number=1)
    foreign_version = _version("owner-foreign", source_suffix="other", number=1)
    old_id = SourceAssociationId("association-owner-old")
    association = TaskSourceAssociation.create(old_id, task_id, old_version)
    factory = _factory(postgres_engine)
    _seed(
        postgres_engine, task_id, factory, (old_version, foreign_version), association
    )
    _insert_task(postgres_engine, foreign_task)

    service = association_services.SourceAssociationApplicationService(factory)
    with pytest.raises(association_errors.SourceAssociationError) as foreign_task_error:
        service.replace_source_association(
            ReplaceSourceAssociation(
                foreign_task,
                old_id,
                SourceAssociationId("association-owner-task-rejected"),
                foreign_version.source_version_id,
                Revision.initial(),
            )
        )
    assert foreign_task_error.value.error_code == "ownership_conflict"
    assert _read_association(factory, old_id) == association

    with pytest.raises(
        association_errors.SourceAssociationError
    ) as foreign_source_error:
        service.replace_source_association(
            ReplaceSourceAssociation(
                task_id,
                old_id,
                SourceAssociationId("association-owner-source-rejected"),
                foreign_version.source_version_id,
                Revision.initial(),
            )
        )
    assert foreign_source_error.value.error_code == "ownership_conflict"
    assert _read_association(factory, old_id) == association
    assert (
        _count(
            postgres_engine,
            "source_evidence_task_source_associations",
            "task_id",
            str(task_id),
        )
        == 1
    )


def test_constraint_and_commit_failures_leave_replacement_atomic(
    postgres_engine: Engine,
) -> None:
    task_id = TaskId("task-association-failure")
    old_version = _version("failure-old", source_suffix="failure", number=1)
    new_version = _version("failure-new", source_suffix="failure", number=2)
    old_id = SourceAssociationId("association-failure-old")
    conflicting_id = SourceAssociationId("association-failure-existing")
    association = TaskSourceAssociation.create(old_id, task_id, old_version)
    existing = TaskSourceAssociation.create(conflicting_id, task_id, old_version)
    factory = _factory(postgres_engine)
    _seed(
        postgres_engine,
        task_id,
        factory,
        (old_version, new_version),
        association,
    )
    with factory() as uow:
        uow.source_associations.add(existing)
        uow.commit()

    with pytest.raises(association_errors.SourceAssociationError) as constraint_error:
        association_services.SourceAssociationApplicationService(
            factory
        ).replace_source_association(
            ReplaceSourceAssociation(
                task_id,
                old_id,
                conflicting_id,
                new_version.source_version_id,
                Revision.initial(),
            )
        )
    assert constraint_error.value.error_code == "constraint_violation"
    assert _read_association(factory, old_id) == association
    assert (
        _count(
            postgres_engine,
            "source_evidence_task_source_associations",
            "source_association_id",
            str(conflicting_id),
        )
        == 1
    )

    commit_factory = _CommitFailureFactory(factory)
    commit_id = SourceAssociationId("association-failure-commit")
    with pytest.raises(association_errors.SourceAssociationError) as commit_error:
        association_services.SourceAssociationApplicationService(
            commit_factory
        ).replace_source_association(
            ReplaceSourceAssociation(
                task_id,
                old_id,
                commit_id,
                new_version.source_version_id,
                Revision.initial(),
            )
        )
    assert commit_error.value.error_code == "persistence_error"
    assert _read_association(factory, old_id) == association
    assert (
        _count(
            postgres_engine,
            "source_evidence_task_source_associations",
            "source_association_id",
            str(commit_id),
        )
        == 0
    )
    assert _checked_out(postgres_engine) == 0


def test_each_service_command_releases_fresh_uow_connection(
    postgres_engine: Engine,
) -> None:
    task_id = TaskId("task-association-connections")
    version = _version("connections", source_suffix="connections")
    association_id = SourceAssociationId("association-connections")
    association = TaskSourceAssociation.create(association_id, task_id, version)
    factory = _factory(postgres_engine)
    _seed(postgres_engine, task_id, factory, (version,), association)

    service = association_services.SourceAssociationApplicationService(factory)
    service.remove_source_association(
        RemoveSourceAssociation(task_id, association_id, Revision.initial())
    )
    assert _checked_out(postgres_engine) == 0
