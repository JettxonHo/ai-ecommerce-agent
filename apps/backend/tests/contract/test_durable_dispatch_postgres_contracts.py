"""Contract checks for the private Durable Dispatch PostgreSQL adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from inspect import getattr_static, getmro
from typing import NoReturn, cast

import pytest
from sqlalchemy import Executable
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Compiled
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import ClauseElement

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchConstraintError,
    DurableDispatchPersistenceError,
    DurableDispatchRevisionConflictError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.ports import (
    DurableDispatchUnitOfWork,
    WorkIntentRepositoryPort,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.envelope import (
    WorkIntentEnvelope,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.identity import (
    DeliveryAttemptId,
    DispatchId,
    FencingToken,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.ownership import (
    LeaseHolderId,
    WorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import (
    WorkIntentStatus,
)
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure.mappings import (
    work_intent_snapshot_to_insert_row,
)
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure.repositories import (
    DurableDispatchPostgresWorkIntentRepository,
)
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure.uow import (
    DurableDispatchPostgresUnitOfWork,
    DurableDispatchPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
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
    def __init__(self, constraint_name: str | None) -> None:
        self.constraint_name = constraint_name


class _DriverIntegrityError(Exception):
    def __init__(self, constraint_name: str | None) -> None:
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


def _snapshot(
    suffix: str = "one",
    *,
    revision: int = 0,
    lease: WorkIntentLease | None = None,
) -> WorkIntentSnapshot:
    dispatch_id = DispatchId(f"dispatch-{suffix}")
    timestamp = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
    envelope = WorkIntentEnvelope(
        dispatch_id,
        "process_source",
        "source_processing",
        ResourceReference("task", f"task-{suffix}"),
        f"command-{suffix}",
        RunId(f"run-{suffix}"),
        f"fingerprint-{suffix}",
        "schema-1",
        DomainVersionId(f"domain-version-{suffix}"),
        Revision(2),
        ResourceReference("source_version", f"source-version-{suffix}"),
        None,
        f"ordering-{suffix}",
        timestamp,
        timestamp,
    )
    return WorkIntentSnapshot(
        envelope,
        WorkIntentStatus.AVAILABLE,
        Revision(revision),
        False,
        lease,
    )


def _leased_snapshot(suffix: str = "one", token: int = 3) -> WorkIntentSnapshot:
    dispatch_id = DispatchId(f"dispatch-{suffix}")
    lease = WorkIntentLease(
        dispatch_id,
        DeliveryAttemptId(f"attempt-{suffix}"),
        LeaseHolderId(f"holder-{suffix}"),
        FencingToken(token),
        datetime(2026, 8, 10, 13, 0, tzinfo=UTC),
    )
    return _snapshot(suffix, lease=lease)


def _compile(statement: ClauseElement) -> Compiled:
    return statement.compile(dialect=postgresql.dialect())


def test_repository_satisfies_port_without_transaction_methods() -> None:
    repository = DurableDispatchPostgresWorkIntentRepository(
        cast(Session, _ExecuteSession())
    )

    assert isinstance(repository, WorkIntentRepositoryPort)
    assert not any(
        hasattr(repository, name) for name in ("commit", "rollback", "close")
    )


def test_get_selects_exact_identity_and_rehydrates_row() -> None:
    snapshot = _snapshot()
    session = _ExecuteSession(_Result(row=work_intent_snapshot_to_insert_row(snapshot)))
    restored = DurableDispatchPostgresWorkIntentRepository(cast(Session, session)).get(
        snapshot.envelope.dispatch_id
    )

    assert restored == snapshot
    assert len(session.statements) == 1
    compiled = _compile(session.statements[0])
    params = dict(compiled.params or {})
    assert any(value == "dispatch-one" for value in params.values())


def test_add_uses_insert_row_and_does_not_own_lifecycle() -> None:
    session = _ExecuteSession()
    DurableDispatchPostgresWorkIntentRepository(cast(Session, session)).add(_snapshot())

    assert len(session.statements) == 1
    sql = str(_compile(session.statements[0])).upper()
    assert sql.startswith("INSERT")
    assert "FENCING_TOKEN" in sql


def test_no_lease_save_passes_partial_mapping_without_fencing_default() -> None:
    session = _ExecuteSession()
    repository = DurableDispatchPostgresWorkIntentRepository(cast(Session, session))
    repository.save(_snapshot(revision=1), expected_revision=Revision(0))

    assert len(session.statements) == 1
    compiled = _compile(session.statements[0])
    params = dict(compiled.params or {})
    assert "fencing_token" not in params
    assert "fencing_token" not in str(compiled).lower()
    assert "delivery_attempt_id" in str(compiled)
    assert "lease_holder_id" in str(compiled)
    assert "lease_expires_at" in str(compiled)


def test_leased_save_includes_active_fencing_token() -> None:
    session = _ExecuteSession()
    repository = DurableDispatchPostgresWorkIntentRepository(cast(Session, session))
    repository.save(_leased_snapshot(token=5), expected_revision=Revision(0))

    compiled = _compile(session.statements[0])
    params = dict(compiled.params or {})
    assert any(value == 5 for value in params.values())
    assert "fencing_token" in str(compiled).lower()


def test_zero_rowcount_is_typed_conflict_with_identity_and_revision() -> None:
    session = _ExecuteSession(_Result(rowcount=0))
    with pytest.raises(DurableDispatchRevisionConflictError) as raised:
        DurableDispatchPostgresWorkIntentRepository(cast(Session, session)).save(
            _snapshot(), expected_revision=Revision(4)
        )

    assert raised.value.safe_context == {
        "dispatch_id": "dispatch-one",
        "expected_revision": "4",
    }


def test_integrity_and_programming_failures_translate() -> None:
    integrity = IntegrityError("INSERT", {}, _DriverIntegrityError("pk_work_intent"))
    with pytest.raises(DurableDispatchConstraintError) as constraint:
        DurableDispatchPostgresWorkIntentRepository(
            cast(Session, _ExecuteFailureSession(integrity))
        ).add(_snapshot())
    assert constraint.value.safe_context == {"constraint": "pk_work_intent"}
    assert constraint.value.__cause__ is integrity

    unnamed = IntegrityError("INSERT", {}, _DriverIntegrityError(None))
    with pytest.raises(DurableDispatchConstraintError) as unnamed_error:
        DurableDispatchPostgresWorkIntentRepository(
            cast(Session, _ExecuteFailureSession(unnamed))
        ).add(_snapshot("unnamed"))
    assert unnamed_error.value.safe_context == {}

    sql_error = SQLAlchemyError("read failed")
    with pytest.raises(DurableDispatchPersistenceError) as persistence:
        DurableDispatchPostgresWorkIntentRepository(
            cast(Session, _ExecuteFailureSession(sql_error))
        ).get(DispatchId("missing"))
    assert persistence.value.__cause__ is sql_error

    with pytest.raises(RuntimeError, match="programming failure"):
        DurableDispatchPostgresWorkIntentRepository(
            cast(Session, _ExecuteFailureSession(RuntimeError("programming failure")))
        ).get(DispatchId("missing"))


def test_private_error_exports_are_exact_and_technology_neutral() -> None:
    from ai_ecommerce_agent.modules.durable_dispatch.application import errors

    assert errors.__all__ == [
        "DurableDispatchConstraintError",
        "DurableDispatchPersistenceError",
        "DurableDispatchRevisionConflictError",
    ]
    assert (
        DurableDispatchConstraintError(constraint_name="constraint").category
        == "durable_dispatch"
    )
    assert DurableDispatchPersistenceError().code == "persistence_error"
    assert getmro(DurableDispatchUnitOfWork)[1] is UnitOfWork
    assert isinstance(
        getattr_static(DurableDispatchUnitOfWork, "work_intents"), property
    )


def test_uow_lifecycle_failures_translate() -> None:
    begin_error = SQLAlchemyError("begin failed")
    begin_session = _LifecycleSession(begin_error=begin_error)
    begin_uow = DurableDispatchPostgresUnitOfWork(lambda: cast(Session, begin_session))
    with pytest.raises(DurableDispatchPersistenceError) as begin:
        begin_uow.__enter__()
    assert begin.value.__cause__ is begin_error
    assert begin_session.close_calls == 1

    commit_error = SQLAlchemyError("commit failed")
    commit_session = _LifecycleSession(commit_error=commit_error)
    commit_uow = DurableDispatchPostgresUnitOfWork(
        lambda: cast(Session, commit_session)
    )
    with pytest.raises(DurableDispatchPersistenceError) as commit:
        with commit_uow:
            commit_uow.commit()
    assert commit.value.__cause__ is commit_error
    assert commit_session.rollback_calls == 1
    assert commit_session.close_calls == 1

    session = _LifecycleSession()
    uow = DurableDispatchPostgresUnitOfWork(lambda: cast(Session, session))
    with pytest.raises(RuntimeError, match="programming failure"):
        with uow:
            raise RuntimeError("programming failure")
    assert session.rollback_calls == 1 and session.close_calls == 1


def test_factory_creates_fresh_uows_and_exposes_private_repositories() -> None:
    sessions: list[_LifecycleSession] = []

    def make_session() -> Session:
        session = _LifecycleSession()
        sessions.append(session)
        return cast(Session, session)

    factory = DurableDispatchPostgresUnitOfWorkFactory(make_session)
    first, second = factory(), factory()
    assert first is not second
    assert len(sessions) == 2
    assert first.work_intents is not second.work_intents
    assert first.work_intent_leases is not second.work_intent_leases
    assert not any(
        hasattr(first, name) for name in ("session", "registry", "execute_sql")
    )
