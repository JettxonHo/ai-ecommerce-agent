"""Contract checks for the private Source Evidence PostgreSQL adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from inspect import getattr_static, getmro
from typing import NoReturn, cast

import pytest
from sqlalchemy import Executable
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import ClauseElement

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceConstraintError,
    SourceEvidenceOwnershipError,
    SourceEvidencePersistenceError,
    SourceEvidenceRevisionConflictError,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceEvidenceUnitOfWork,
    SourceVersionProcessingRepositoryPort,
    SourceVersionRepositoryPort,
    TaskSourceAssociationRepositoryPort,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceVersion,
    SourceVersionProcessing,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.repositories import (
    SourceEvidencePostgresSourceVersionProcessingRepository,
    SourceEvidencePostgresSourceVersionRepository,
    SourceEvidencePostgresTaskSourceAssociationRepository,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.tables import (
    SOURCE_EVIDENCE_SCHEMA_TOKEN,
    SOURCE_VERSION_PROCESSING_TABLE,
    SOURCE_VERSIONS_TABLE,
    SOURCES_TABLE,
    TASK_SOURCE_ASSOCIATIONS_TABLE,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.uow import (
    SourceEvidencePostgresUnitOfWork,
    SourceEvidencePostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceId,
    SourceVersionId,
    VersionNumber,
)

pytestmark = pytest.mark.contract


class _Result:
    def __init__(
        self, *, rowcount: int = 1, row: dict[str, object] | None = None
    ) -> None:
        self.rowcount = rowcount
        self._row = row

    def mappings(self) -> _Result:
        return self

    def one_or_none(self) -> dict[str, object] | None:
        return self._row


class _ExecuteSession:
    def __init__(self, result: _Result | None = None) -> None:
        self.result = result or _Result()
        self.statements: list[ClauseElement] = []

    def execute(self, statement: Executable) -> _Result:
        self.statements.append(cast(ClauseElement, statement))
        return self.result


class _ExecuteFailureSession:
    def __init__(self, error: BaseException) -> None:
        self._error = error

    def execute(self, statement: Executable) -> NoReturn:
        del statement
        raise self._error


class _Diagnostic:
    def __init__(self, constraint_name: str) -> None:
        self.constraint_name = constraint_name


class _DriverIntegrityError(Exception):
    def __init__(self, constraint_name: str) -> None:
        super().__init__("integrity failure")
        self.diag = _Diagnostic(constraint_name)


class _LifecycleSession:
    def __init__(
        self,
        *,
        begin_error: BaseException | None = None,
        commit_error: BaseException | None = None,
    ) -> None:
        self.begin_error = begin_error
        self.commit_error = commit_error
        self.begin_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    def begin(self) -> None:
        self.begin_calls += 1
        if self.begin_error is not None:
            raise self.begin_error

    def commit(self) -> None:
        self.commit_calls += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollback_calls += 1

    def close(self) -> None:
        self.close_calls += 1


def _version(suffix: str = "one") -> SourceVersion:
    return SourceVersion.create(
        SourceVersionId(f"source-version-{suffix}"),
        SourceId(f"source-{suffix}"),
        VersionNumber(1),
    )


def _processing(version: SourceVersion | None = None) -> SourceVersionProcessing:
    version = version or _version()
    return SourceVersionProcessing.create(
        version.source_version_id,
        updated_at=datetime(2026, 8, 9, tzinfo=UTC),
    )


def test_repositories_satisfy_ports_without_lifecycle_methods() -> None:
    repositories = (
        SourceEvidencePostgresSourceVersionRepository,
        SourceEvidencePostgresSourceVersionProcessingRepository,
        SourceEvidencePostgresTaskSourceAssociationRepository,
    )
    ports = (
        SourceVersionRepositoryPort,
        SourceVersionProcessingRepositoryPort,
        TaskSourceAssociationRepositoryPort,
    )
    assert all(isinstance(repository, type) for repository in repositories)
    assert all(
        all(callable(getattr(port, method, None)) for method in ("get", "add"))
        for port in ports
    )
    for repository in repositories:
        assert not any(
            hasattr(repository, method) for method in ("commit", "rollback", "close")
        )


def test_uow_exposes_only_typed_source_repositories() -> None:
    assert UnitOfWork in getmro(SourceEvidenceUnitOfWork)
    assert isinstance(SourceEvidencePostgresUnitOfWork, type)
    assert isinstance(SourceEvidencePostgresUnitOfWorkFactory, type)
    assert isinstance(
        getattr_static(SourceEvidenceUnitOfWork, "source_versions"), property
    )
    assert isinstance(
        getattr_static(SourceEvidenceUnitOfWork, "source_version_processing"), property
    )
    assert isinstance(
        getattr_static(SourceEvidenceUnitOfWork, "source_associations"), property
    )
    assert not any(
        hasattr(SourceEvidencePostgresUnitOfWork, name)
        for name in ("session", "registry", "get_repository", "execute_sql")
    )


def test_source_metadata_uses_existing_schema_token_and_columns() -> None:
    assert all(
        table.schema == SOURCE_EVIDENCE_SCHEMA_TOKEN
        for table in (
            SOURCES_TABLE,
            SOURCE_VERSIONS_TABLE,
            SOURCE_VERSION_PROCESSING_TABLE,
            TASK_SOURCE_ASSOCIATIONS_TABLE,
        )
    )
    assert [column.name for column in SOURCES_TABLE.columns] == ["source_id"]
    assert [column.name for column in SOURCE_VERSIONS_TABLE.columns] == [
        "source_version_id",
        "source_id",
        "version_number",
    ]


def test_source_version_add_uses_private_anchor_on_conflict_and_no_commit() -> None:
    session = _ExecuteSession()
    repository = SourceEvidencePostgresSourceVersionRepository(cast(Session, session))
    repository.add(_version())
    assert len(session.statements) == 2
    sql = str(session.statements[0].compile(dialect=postgresql.dialect()))
    assert "ON CONFLICT (source_id) DO NOTHING" in sql
    assert not any(
        hasattr(session, method) for method in ("commit", "rollback", "close")
    )


def test_cas_save_uses_identity_and_expected_revision_without_prequery() -> None:
    session = _ExecuteSession()
    repository = SourceEvidencePostgresSourceVersionProcessingRepository(
        cast(Session, session)
    )
    value = _processing()
    changed = value.start_processing(
        expected_revision=Revision(0), updated_at=value.updated_at
    )
    repository.save(changed, expected_revision=Revision(0))
    assert len(session.statements) == 1
    sql = str(session.statements[0].compile(dialect=postgresql.dialect()))
    assert "source_version_id" in sql and "revision" in sql
    assert "UPDATE" in sql


def test_cas_zero_rowcount_is_typed_conflict() -> None:
    session = _ExecuteSession(_Result(rowcount=0))
    value = _processing().start_processing(
        expected_revision=Revision(0), updated_at=datetime(2026, 8, 9, tzinfo=UTC)
    )
    with pytest.raises(SourceEvidenceRevisionConflictError) as raised:
        SourceEvidencePostgresSourceVersionProcessingRepository(
            cast(Session, session)
        ).save(value, expected_revision=Revision(0))
    assert raised.value.safe_context == {
        "expected_revision": "0",
        "identity": "source-version-one",
        "resource": "source_version_processing",
    }


def test_integrity_error_translation_is_allowlisted_and_cause_preserved() -> None:
    owner_error = IntegrityError(
        "INSERT",
        {},
        _DriverIntegrityError("fk_source_evidence_source_versions_source_owner"),
    )
    with pytest.raises(SourceEvidenceOwnershipError) as owner:
        SourceEvidencePostgresSourceVersionRepository(
            cast(Session, _ExecuteFailureSession(owner_error))
        ).add(_version())
    assert owner.value.safe_context["constraint"] == (
        "fk_source_evidence_source_versions_source_owner"
    )
    assert owner.value.__cause__ is owner_error

    generic_error = IntegrityError(
        "INSERT", {}, _DriverIntegrityError("pk_source_evidence_source_versions")
    )
    with pytest.raises(SourceEvidenceConstraintError) as generic:
        SourceEvidencePostgresSourceVersionRepository(
            cast(Session, _ExecuteFailureSession(generic_error))
        ).add(_version())
    assert (
        generic.value.safe_context["constraint"] == "pk_source_evidence_source_versions"
    )


def test_non_integrity_sqlalchemy_error_is_typed_and_programming_error_propagates() -> (
    None
):
    sql_error = SQLAlchemyError("read failed")
    with pytest.raises(SourceEvidencePersistenceError) as raised:
        SourceEvidencePostgresSourceVersionRepository(
            cast(Session, _ExecuteFailureSession(sql_error))
        ).get(SourceVersionId("missing"))
    assert raised.value.__cause__ is sql_error

    with pytest.raises(RuntimeError, match="programming failure"):
        SourceEvidencePostgresSourceVersionRepository(
            cast(Session, _ExecuteFailureSession(RuntimeError("programming failure")))
        ).get(SourceVersionId("missing"))


def test_uow_lifecycle_translates_begin_and_commit_sqlalchemy_errors() -> None:
    begin_error = SQLAlchemyError("begin failed")
    begin_session = _LifecycleSession(begin_error=begin_error)
    begin_uow = SourceEvidencePostgresUnitOfWork(lambda: cast(Session, begin_session))
    with pytest.raises(SourceEvidencePersistenceError) as begin:
        begin_uow.__enter__()
    assert begin.value.__cause__ is begin_error
    assert begin_session.close_calls == 1

    commit_error = SQLAlchemyError("commit failed")
    commit_session = _LifecycleSession(commit_error=commit_error)
    commit_uow = SourceEvidencePostgresUnitOfWork(lambda: cast(Session, commit_session))
    with pytest.raises(SourceEvidencePersistenceError) as commit:
        with commit_uow:
            commit_uow.commit()
    assert commit.value.__cause__ is commit_error
    assert commit_session.rollback_calls == 1
    assert commit_session.close_calls == 1


def test_uow_does_not_swallow_programming_or_domain_errors() -> None:
    session = _LifecycleSession()
    uow = SourceEvidencePostgresUnitOfWork(lambda: cast(Session, session))
    with pytest.raises(RuntimeError, match="programming failure"):
        with uow:
            raise RuntimeError("programming failure")
    assert session.rollback_calls == 1 and session.close_calls == 1


def test_uow_factory_creates_fresh_instances() -> None:
    sessions: list[_LifecycleSession] = []

    def make_session() -> Session:
        session = _LifecycleSession()
        sessions.append(session)
        return cast(Session, session)

    factory = SourceEvidencePostgresUnitOfWorkFactory(make_session)
    first, second = factory(), factory()
    assert first is not second
    assert len(sessions) == 2
