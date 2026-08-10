"""Contract checks for the private Durable Dispatch lease repository."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from sqlalchemy import Executable
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Compiled
from sqlalchemy.orm import Session
from sqlalchemy.sql import ClauseElement

from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchRevisionConflictError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_commands import (
    ClaimNextWorkIntent,
    HeartbeatWorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.ports import (
    WorkIntentLeaseRepositoryPort,
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
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import WorkIntentStatus
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure import lease_repository
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure.mappings import (
    work_intent_snapshot_to_insert_row,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
)

pytestmark = pytest.mark.contract


class _Result:
    def __init__(self, row: dict[str, object] | None = None) -> None:
        self.rowcount = 1
        self._row = row

    def mappings(self) -> _Result:
        return self

    def one_or_none(self) -> dict[str, object] | None:
        return self._row


class _ExecuteSession:
    def __init__(self, *results: _Result) -> None:
        self._results = list(results)
        self.statements: list[ClauseElement] = []

    def execute(self, statement: Executable) -> _Result:
        self.statements.append(cast(ClauseElement, statement))
        if not self._results:
            return _Result()
        return self._results.pop(0)


def _snapshot(
    suffix: str = "one",
    *,
    status: WorkIntentStatus = WorkIntentStatus.AVAILABLE,
    revision: int = 0,
    lease: WorkIntentLease | None = None,
    cancellation_requested: bool = False,
) -> WorkIntentSnapshot:
    dispatch_id = DispatchId(f"dispatch-{suffix}")
    created_at = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
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
        created_at,
        created_at,
    )
    return WorkIntentSnapshot(
        envelope,
        status,
        Revision(revision),
        cancellation_requested,
        lease,
    )


def _leased_snapshot(
    suffix: str = "one",
    *,
    token: int = 3,
    revision: int = 0,
    expires_at: datetime | None = None,
) -> WorkIntentSnapshot:
    dispatch_id = DispatchId(f"dispatch-{suffix}")
    lease = WorkIntentLease(
        dispatch_id,
        DeliveryAttemptId(f"attempt-{suffix}"),
        LeaseHolderId(f"holder-{suffix}"),
        FencingToken(token),
        expires_at or datetime(2026, 8, 10, 13, 0, tzinfo=UTC),
    )
    return _snapshot(
        suffix, status=WorkIntentStatus.LEASED, revision=revision, lease=lease
    )


def _claim_command(
    suffix: str = "one",
    *,
    now: datetime | None = None,
    expires_at: datetime | None = None,
) -> ClaimNextWorkIntent:
    current = now or datetime(2026, 8, 10, 12, 30, tzinfo=UTC)
    return ClaimNextWorkIntent(
        LeaseHolderId(f"new-holder-{suffix}"),
        DeliveryAttemptId(f"new-attempt-{suffix}"),
        current,
        expires_at or current + timedelta(minutes=10),
    )


def _heartbeat_command(
    snapshot: WorkIntentSnapshot,
    *,
    holder_id: LeaseHolderId | None = None,
    delivery_attempt_id: DeliveryAttemptId | None = None,
    fencing_token: FencingToken | None = None,
    expected_revision: Revision | None = None,
    now: datetime | None = None,
    expires_at: datetime | None = None,
) -> HeartbeatWorkIntentLease:
    assert snapshot.current_lease is not None
    lease = snapshot.current_lease
    current = now or datetime(2026, 8, 10, 12, 30, tzinfo=UTC)
    return HeartbeatWorkIntentLease(
        snapshot.envelope.dispatch_id,
        delivery_attempt_id or lease.delivery_attempt_id,
        holder_id or lease.holder_id,
        fencing_token or lease.fencing_token,
        expected_revision or snapshot.revision,
        current,
        expires_at or current + timedelta(hours=2),
    )


def _compile(statement: ClauseElement) -> Compiled:
    return statement.compile(dialect=postgresql.dialect())


def test_lease_repository_satisfies_port_without_lifecycle_methods() -> None:
    repository = lease_repository.DurableDispatchPostgresWorkIntentLeaseRepository(
        cast(Session, _ExecuteSession())
    )
    assert isinstance(repository, WorkIntentLeaseRepositoryPort)
    assert not any(
        hasattr(repository, name) for name in ("commit", "rollback", "close")
    )


def test_claim_selects_one_locked_candidate_and_returns_retained_token_plus_one() -> (
    None
):
    current = _snapshot()
    command = _claim_command()
    lease = WorkIntentLease(
        current.envelope.dispatch_id,
        command.delivery_attempt_id,
        command.holder_id,
        FencingToken(1),
        command.lease_expires_at,
    )
    claimed = replace(
        current,
        status=WorkIntentStatus.LEASED,
        revision=Revision(1),
        current_lease=lease,
    )
    session = _ExecuteSession(
        _Result(work_intent_snapshot_to_insert_row(current)),
        _Result(work_intent_snapshot_to_insert_row(claimed)),
    )

    result = lease_repository.DurableDispatchPostgresWorkIntentLeaseRepository(
        cast(Session, session)
    ).claim_next(command)

    assert result == claimed
    assert result is not None and result.current_lease is not None
    assert result.current_lease.fencing_token == FencingToken(1)
    assert result.current_lease.holder_id == command.holder_id
    assert result.current_lease.delivery_attempt_id == command.delivery_attempt_id
    assert result.current_lease.lease_expires_at == command.lease_expires_at
    assert len(session.statements) == 2
    select_sql = str(_compile(session.statements[0])).upper()
    assert "FOR UPDATE" in select_sql and "SKIP LOCKED" in select_sql
    assert "LIMIT" in select_sql and "ORDER BY" in select_sql
    assert "CANCELLATION_REQUESTED" in select_sql
    assert "SUPERSEDED_BY_DISPATCH_ID IS NULL" in select_sql
    update_sql = str(_compile(session.statements[1])).upper()
    assert update_sql.startswith("UPDATE")
    assert "RETURNING" in update_sql


def test_claim_without_candidate_returns_none_without_write() -> None:
    session = _ExecuteSession(_Result())
    result = lease_repository.DurableDispatchPostgresWorkIntentLeaseRepository(
        cast(Session, session)
    ).claim_next(_claim_command())
    assert result is None
    assert len(session.statements) == 1
    assert str(_compile(session.statements[0])).upper().startswith("SELECT")


def test_claim_update_without_returned_row_is_typed_revision_conflict() -> None:
    current = _snapshot()
    session = _ExecuteSession(
        _Result(work_intent_snapshot_to_insert_row(current)), _Result()
    )
    with pytest.raises(DurableDispatchRevisionConflictError) as raised:
        lease_repository.DurableDispatchPostgresWorkIntentLeaseRepository(
            cast(Session, session)
        ).claim_next(_claim_command())
    assert raised.value.safe_context == {
        "dispatch_id": "dispatch-one",
        "expected_revision": "0",
    }


def test_heartbeat_uses_exact_predicates_and_updates_only_lease() -> None:
    current = _leased_snapshot(token=5)
    command = _heartbeat_command(current)
    assert current.current_lease is not None
    updated_lease = replace(
        current.current_lease,
        lease_expires_at=command.lease_expires_at,
    )
    updated = replace(
        current,
        revision=Revision(1),
        current_lease=updated_lease,
    )
    session = _ExecuteSession(_Result(work_intent_snapshot_to_insert_row(updated)))

    result = lease_repository.DurableDispatchPostgresWorkIntentLeaseRepository(
        cast(Session, session)
    ).heartbeat(command)

    assert result == updated
    assert len(session.statements) == 1
    sql = str(_compile(session.statements[0])).upper()
    assert sql.startswith("UPDATE") and "RETURNING" in sql
    for column in (
        "DISPATCH_ID",
        "REVISION",
        "DELIVERY_ATTEMPT_ID",
        "LEASE_HOLDER_ID",
        "FENCING_TOKEN",
        "LEASE_EXPIRES_AT",
    ):
        assert column in sql
    set_sql = sql.split(" SET ", maxsplit=1)[1].split(" WHERE ", maxsplit=1)[0]
    normalized_set_sql = set_sql.replace(" ", "")
    assert set_sql.count("=") == 2
    assert "REVISION=" in normalized_set_sql
    assert "LEASE_EXPIRES_AT=" in normalized_set_sql
    assert "FENCING_TOKEN" not in normalized_set_sql


def test_heartbeat_without_match_returns_none_without_write() -> None:
    current = _leased_snapshot(token=5)
    session = _ExecuteSession(_Result())
    result = lease_repository.DurableDispatchPostgresWorkIntentLeaseRepository(
        cast(Session, session)
    ).heartbeat(_heartbeat_command(current))
    assert result is None
    assert len(session.statements) == 1
