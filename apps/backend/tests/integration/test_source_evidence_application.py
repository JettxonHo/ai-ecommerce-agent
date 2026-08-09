"""Opt-in PostgreSQL acceptance for Source processing application use cases."""

from __future__ import annotations

import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier
from types import TracebackType
from typing import Self, cast

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.application.ports import UnitOfWorkState
from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceError,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceEvidenceUnitOfWork,
    SourceVersionProcessingRepositoryPort,
    SourceVersionRepositoryPort,
    TaskSourceAssociationRepositoryPort,
)
from ai_ecommerce_agent.modules.source_evidence.application.services import (
    SourceEvidenceApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceProcessingStatus,
    SourceVersion,
    SourceVersionProcessing,
    SourceVersionSnapshot,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.uow import (
    SourceEvidencePostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.source_evidence.public import (
    MarkSourceReady,
    StartSourceProcessing,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceId,
    SourceVersionId,
    VersionNumber,
)

pytestmark = [pytest.mark.integration, pytest.mark.live]

if os.environ.get("MVP0_RUN_SOURCE_EVIDENCE_APPLICATION") != "1":
    pytest.skip(
        "set MVP0_RUN_SOURCE_EVIDENCE_APPLICATION=1 for the opt-in "
        "Source Evidence application suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_010c2_source_application"
URL_ENV = "MVP0_SOURCE_EVIDENCE_APPLICATION_DATABASE_URL"
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
    """Own a fixed schema, upgrade it to head, and verify deterministic teardown."""

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
        SourceVersionId(f"source-version-application-{suffix}"),
        SourceId(f"source-application-{suffix}"),
        VersionNumber(1),
    )


def _insert_processing(
    factory: SourceEvidencePostgresUnitOfWorkFactory,
    version: SourceVersion,
    processing: SourceVersionProcessing,
) -> None:
    with factory() as uow:
        uow.source_versions.add(version)
        uow.source_version_processing.add(processing)
        uow.commit()


def _read_processing(
    factory: SourceEvidencePostgresUnitOfWorkFactory,
    version: SourceVersion,
) -> SourceVersionProcessing:
    with factory() as uow:
        processing = uow.source_version_processing.get(version.source_version_id)
        assert processing is not None
        uow.commit()
        return processing


class _BarrierProcessingRepository:
    def __init__(
        self,
        delegate: SourceVersionProcessingRepositoryPort,
        barrier: Barrier,
    ) -> None:
        self._delegate = delegate
        self._barrier = barrier

    def get(self, source_version_id: SourceVersionId) -> SourceVersionProcessing | None:
        value = self._delegate.get(source_version_id)
        self._barrier.wait(timeout=10)
        return value

    def add(self, processing: SourceVersionProcessing) -> None:
        self._delegate.add(processing)

    def save(
        self,
        processing: SourceVersionProcessing,
        *,
        expected_revision: Revision,
    ) -> None:
        self._delegate.save(processing, expected_revision=expected_revision)


class _BarrierUow:
    def __init__(self, delegate: SourceEvidenceUnitOfWork, barrier: Barrier) -> None:
        self._delegate = delegate
        self._source_version_processing = _BarrierProcessingRepository(
            delegate.source_version_processing, barrier
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
        return self._source_version_processing

    @property
    def source_associations(self) -> TaskSourceAssociationRepositoryPort:
        return self._delegate.source_associations


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


def test_committed_projection_roundtrips_through_real_postgres(
    postgres_engine: Engine,
) -> None:
    version = _version("roundtrip")
    factory = _factory(postgres_engine)
    _insert_processing(
        factory,
        version,
        SourceVersionProcessing.create(version.source_version_id, updated_at=NOW),
    )
    application = SourceEvidenceApplicationService(factory)

    result = application.start_source_processing(
        StartSourceProcessing(version.source_version_id, Revision.initial(), NOW)
    )

    assert isinstance(result, SourceVersionSnapshot)
    assert result.source_version_id == version.source_version_id
    assert result.source_id == version.source_id
    assert result.version_number == version.version_number
    assert result.processing_status is SourceProcessingStatus.PROCESSING
    assert result.processing_revision == Revision(1)
    assert (
        _read_processing(factory, version).status is SourceProcessingStatus.PROCESSING
    )


def test_two_real_transactions_have_one_processing_cas_winner_and_no_loser_write(
    postgres_engine: Engine,
) -> None:
    version = _version("cas")
    factory = _factory(postgres_engine)
    _insert_processing(
        factory,
        version,
        SourceVersionProcessing.create(version.source_version_id, updated_at=NOW),
    )
    barrier_factory = _BarrierFactory(factory, Barrier(2))
    application = SourceEvidenceApplicationService(barrier_factory)

    def invoke() -> tuple[str, SourceEvidenceError | SourceVersionSnapshot]:
        try:
            return (
                "success",
                application.start_source_processing(
                    StartSourceProcessing(
                        version.source_version_id, Revision.initial(), NOW
                    )
                ),
            )
        except SourceEvidenceError as error:
            return ("error", error)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(invoke) for _ in range(2)]
        outcomes = [future.result() for future in futures]

    assert [kind for kind, _ in outcomes].count("success") == 1
    assert [kind for kind, _ in outcomes].count("error") == 1
    loser = next(value for kind, value in outcomes if kind == "error")
    assert isinstance(loser, SourceEvidenceError)
    assert loser.error_code == "revision_conflict"
    current = _read_processing(factory, version)
    assert current.status is SourceProcessingStatus.PROCESSING
    assert current.revision == Revision(1)


def test_terminal_transition_failure_leaves_real_current_truth_unchanged(
    postgres_engine: Engine,
) -> None:
    version = _version("terminal")
    factory = _factory(postgres_engine)
    _insert_processing(
        factory,
        version,
        SourceVersionProcessing(
            source_version_id=version.source_version_id,
            status=SourceProcessingStatus.SUPERSEDED,
            revision=Revision(3),
            failure_summary=None,
            updated_at=NOW,
        ),
    )
    application = SourceEvidenceApplicationService(factory)

    with pytest.raises(SourceEvidenceError) as raised:
        application.mark_source_ready(
            MarkSourceReady(version.source_version_id, Revision(3), NOW)
        )

    assert raised.value.error_code == "invalid_transition"
    current = _read_processing(factory, version)
    assert current.status is SourceProcessingStatus.SUPERSEDED
    assert current.revision == Revision(3)
    assert current.updated_at == NOW
