"""Unit contracts for the Durable Dispatch lease application service."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from types import TracebackType
from typing import Self, cast

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWorkState
from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchConstraintError,
    DurableDispatchPersistenceError,
    DurableDispatchRevisionConflictError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_commands import (
    ClaimNextWorkIntent,
    HeartbeatWorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_errors import (
    DurableDispatchLeaseError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_protocols import (
    DurableDispatchLeaseApplication,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.ports import (
    DurableDispatchUnitOfWork,
    DurableDispatchUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.envelope import (
    WorkIntentEnvelope,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.identity import (
    DeliveryAttemptId,
    DispatchId,
    FencingToken,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.ownership import LeaseHolderId
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import WorkIntentStatus
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ProjectError,
    ResourceReference,
    Revision,
    RunId,
)

pytestmark = pytest.mark.unit

NOW = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
CLAIM = ClaimNextWorkIntent(
    holder_id=LeaseHolderId("holder-one"),
    delivery_attempt_id=DeliveryAttemptId("attempt-one"),
    now=NOW,
    lease_expires_at=datetime(2026, 8, 10, 13, 0, tzinfo=UTC),
)
HEARTBEAT = HeartbeatWorkIntentLease(
    dispatch_id=DispatchId("dispatch-one"),
    delivery_attempt_id=DeliveryAttemptId("attempt-one"),
    holder_id=LeaseHolderId("holder-one"),
    fencing_token=FencingToken(1),
    expected_revision=Revision(3),
    now=NOW,
    lease_expires_at=datetime(2026, 8, 10, 13, 0, tzinfo=UTC),
)


def _snapshot() -> WorkIntentSnapshot:
    return WorkIntentSnapshot(
        WorkIntentEnvelope(
            DispatchId("dispatch-one"),
            "process_source",
            "source_processing",
            ResourceReference("task", "task-one"),
            "command-one",
            RunId("run-one"),
            "fingerprint-one",
            "schema-1",
            DomainVersionId("domain-version-one"),
            Revision(2),
            ResourceReference("source_version", "source-version-one"),
            None,
            "ordering-one",
            NOW,
            NOW,
        ),
        WorkIntentStatus.LEASED,
        Revision(4),
        False,
        None,
    )


class _LeaseRepository:
    def __init__(self, owner: _FakeUow) -> None:
        self._owner = owner

    def claim_next(self, command: ClaimNextWorkIntent) -> WorkIntentSnapshot | None:
        self._owner.events.append(("claim_next", command))
        if self._owner.claim_error is not None:
            raise self._owner.claim_error
        return self._owner.claim_result

    def heartbeat(self, command: HeartbeatWorkIntentLease) -> WorkIntentSnapshot | None:
        self._owner.events.append(("heartbeat", command))
        if self._owner.heartbeat_error is not None:
            raise self._owner.heartbeat_error
        return self._owner.heartbeat_result


class _FakeUow:
    def __init__(
        self,
        *,
        claim_result: WorkIntentSnapshot | None = None,
        heartbeat_result: WorkIntentSnapshot | None = None,
        claim_error: BaseException | None = None,
        heartbeat_error: BaseException | None = None,
        enter_error: BaseException | None = None,
        commit_error: BaseException | None = None,
        exit_error: BaseException | None = None,
    ) -> None:
        self.claim_result = claim_result
        self.heartbeat_result = heartbeat_result
        self.claim_error = claim_error
        self.heartbeat_error = heartbeat_error
        self.enter_error = enter_error
        self.commit_error = commit_error
        self.exit_error = exit_error
        self.events: list[tuple[str, object | None]] = []
        self._state = UnitOfWorkState.NEW
        self.commits = 0
        self.rollbacks = 0
        self.close_calls = 0
        self._lease_repository = _LeaseRepository(self)

    @property
    def state(self) -> UnitOfWorkState:
        return self._state

    @property
    def work_intent_leases(self) -> _LeaseRepository:
        return self._lease_repository

    def __enter__(self) -> Self:
        self.events.append(("enter", None))
        if self.enter_error is not None:
            self.close()
            raise self.enter_error
        self._state = UnitOfWorkState.ACTIVE
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc_value, traceback
        self.events.append(("exit", None))
        if self._state is UnitOfWorkState.ACTIVE:
            self.rollback()
        self.close()
        if self.exit_error is not None:
            raise self.exit_error

    def commit(self) -> None:
        self.events.append(("commit", None))
        self.commits += 1
        if self.commit_error is not None:
            self.rollback()
            self.close()
            raise self.commit_error
        self._state = UnitOfWorkState.COMMITTED

    def rollback(self) -> None:
        self.events.append(("rollback", None))
        self.rollbacks += 1
        self._state = UnitOfWorkState.ROLLED_BACK

    def close(self) -> None:
        if self._state is UnitOfWorkState.CLOSED:
            return
        self.events.append(("close", None))
        self.close_calls += 1
        self._state = UnitOfWorkState.CLOSED


class _Factory:
    def __init__(
        self,
        *,
        claim_result: WorkIntentSnapshot | None = None,
        heartbeat_result: WorkIntentSnapshot | None = None,
        claim_error: BaseException | None = None,
        heartbeat_error: BaseException | None = None,
        enter_error: BaseException | None = None,
        commit_error: BaseException | None = None,
        exit_error: BaseException | None = None,
    ) -> None:
        self.options = {
            "claim_result": claim_result,
            "heartbeat_result": heartbeat_result,
            "claim_error": claim_error,
            "heartbeat_error": heartbeat_error,
            "enter_error": enter_error,
            "commit_error": commit_error,
            "exit_error": exit_error,
        }
        self.uows: list[_FakeUow] = []

    def __call__(self) -> DurableDispatchUnitOfWork:
        uow = _FakeUow(
            claim_result=cast(WorkIntentSnapshot | None, self.options["claim_result"]),
            heartbeat_result=cast(
                WorkIntentSnapshot | None, self.options["heartbeat_result"]
            ),
            claim_error=cast(BaseException | None, self.options["claim_error"]),
            heartbeat_error=cast(BaseException | None, self.options["heartbeat_error"]),
            enter_error=cast(BaseException | None, self.options["enter_error"]),
            commit_error=cast(BaseException | None, self.options["commit_error"]),
            exit_error=cast(BaseException | None, self.options["exit_error"]),
        )
        self.uows.append(uow)
        return cast(DurableDispatchUnitOfWork, uow)


def _service(factory: _Factory) -> DurableDispatchLeaseApplication:
    from ai_ecommerce_agent.modules.durable_dispatch.application.lease_services import (
        DurableDispatchLeaseApplicationService,
    )

    return DurableDispatchLeaseApplicationService(
        cast(DurableDispatchUnitOfWorkFactory, factory)
    )


def test_service_implements_the_existing_runtime_protocol() -> None:
    assert isinstance(_service(_Factory()), DurableDispatchLeaseApplication)


def test_claim_commits_result_and_releases_fresh_uow() -> None:
    snapshot = _snapshot()
    factory = _Factory(claim_result=snapshot)
    result = _service(factory).claim_next_work_intent(CLAIM)

    assert result is snapshot
    assert len(factory.uows) == 1
    uow = factory.uows[0]
    assert [name for name, _ in uow.events] == [
        "enter",
        "claim_next",
        "commit",
        "exit",
        "close",
    ]
    assert uow.commits == 1 and uow.rollbacks == 0


def test_claim_commits_normal_none_without_retry() -> None:
    factory = _Factory(claim_result=None)
    assert _service(factory).claim_next_work_intent(CLAIM) is None
    assert len(factory.uows) == 1
    uow = factory.uows[0]
    assert [name for name, _ in uow.events] == [
        "enter",
        "claim_next",
        "commit",
        "exit",
        "close",
    ]
    assert uow.commits == 1 and uow.rollbacks == 0


def test_heartbeat_commits_success_and_returns_exact_snapshot() -> None:
    snapshot = _snapshot()
    factory = _Factory(heartbeat_result=snapshot)
    result = _service(factory).heartbeat_work_intent_lease(HEARTBEAT)

    assert result is snapshot
    assert len(factory.uows) == 1
    uow = factory.uows[0]
    assert [name for name, _ in uow.events] == [
        "enter",
        "heartbeat",
        "commit",
        "exit",
        "close",
    ]


def test_heartbeat_none_is_exact_lease_lost_without_commit() -> None:
    factory = _Factory(heartbeat_result=None)
    with pytest.raises(DurableDispatchLeaseError) as raised:
        _service(factory).heartbeat_work_intent_lease(HEARTBEAT)

    error = raised.value
    assert error.error_code == "lease_lost"
    assert error.category == "ownership"
    assert error.message == "Lease is no longer current"
    assert error.retryability is False
    assert error.relevant_dispatch_id == HEARTBEAT.dispatch_id
    assert error.delivery_attempt_id == HEARTBEAT.delivery_attempt_id
    assert error.expected_revision == HEARTBEAT.expected_revision
    assert error.conflicting_state is None
    assert error.recovery_hint == "reclaim"
    uow = factory.uows[0]
    assert uow.commits == 0 and uow.rollbacks == 1 and uow.close_calls == 1


@pytest.mark.parametrize(
    ("method", "command", "adapter_error", "expected_code", "retryability"),
    [
        (
            "claim_next_work_intent",
            CLAIM,
            DurableDispatchRevisionConflictError(
                dispatch_id="dispatch-adapter",
                expected_revision=Revision(8),
            ),
            "revision_conflict",
            False,
        ),
        (
            "claim_next_work_intent",
            CLAIM,
            DurableDispatchConstraintError(constraint_name="secret_constraint"),
            "constraint_violation",
            False,
        ),
        (
            "claim_next_work_intent",
            CLAIM,
            DurableDispatchPersistenceError(),
            "persistence_error",
            True,
        ),
        (
            "heartbeat_work_intent_lease",
            HEARTBEAT,
            DurableDispatchRevisionConflictError(
                dispatch_id="dispatch-one",
                expected_revision=Revision(8),
            ),
            "revision_conflict",
            False,
        ),
        (
            "heartbeat_work_intent_lease",
            HEARTBEAT,
            DurableDispatchConstraintError(constraint_name="secret_constraint"),
            "constraint_violation",
            False,
        ),
        (
            "heartbeat_work_intent_lease",
            HEARTBEAT,
            DurableDispatchPersistenceError(),
            "persistence_error",
            True,
        ),
    ],
)
def test_known_adapter_errors_map_without_technical_context(
    method: str,
    command: ClaimNextWorkIntent | HeartbeatWorkIntentLease,
    adapter_error: ProjectError,
    expected_code: str,
    retryability: bool,
) -> None:
    if method == "claim_next_work_intent":
        factory = _Factory(claim_error=adapter_error)
    else:
        factory = _Factory(heartbeat_error=adapter_error)
    with pytest.raises(DurableDispatchLeaseError) as raised:
        cast(Callable[[object], object], getattr(_service(factory), method))(command)

    error = raised.value
    assert error.error_code == expected_code
    assert error.retryability is retryability
    assert error.delivery_attempt_id == command.delivery_attempt_id
    assert error.conflicting_state is None
    assert all(secret not in error.message for secret in ("secret_constraint",))
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1

    if expected_code == "revision_conflict":
        assert error.relevant_dispatch_id == DispatchId(
            "dispatch-adapter" if method == "claim_next_work_intent" else "dispatch-one"
        )
        assert error.expected_revision == Revision(8)
    elif method == "heartbeat_work_intent_lease":
        assert error.relevant_dispatch_id == HEARTBEAT.dispatch_id
        assert error.expected_revision == HEARTBEAT.expected_revision
    else:
        assert error.relevant_dispatch_id is None
        assert error.expected_revision is None


@pytest.mark.parametrize(
    "option",
    ["enter_error", "commit_error", "exit_error"],
)
def test_uow_persistence_failures_map_at_every_lifecycle_boundary(option: str) -> None:
    failure = DurableDispatchPersistenceError()
    if option == "enter_error":
        factory = _Factory(enter_error=failure)
    elif option == "commit_error":
        factory = _Factory(commit_error=failure)
    else:
        factory = _Factory(exit_error=failure)
    with pytest.raises(DurableDispatchLeaseError) as raised:
        _service(factory).claim_next_work_intent(CLAIM)
    assert raised.value.error_code == "persistence_error"
    assert raised.value.retryability is True
    assert raised.value.recovery_hint == "retry_later"
    assert len(factory.uows) == 1


@pytest.mark.parametrize(
    "unknown_error",
    [
        DurableDispatchLeaseError(
            "existing", "ownership", "existing", False, DispatchId("dispatch-one")
        ),
        ProjectError("other", "unknown"),
        RuntimeError("programming bug"),
        ValueError("invariant bug"),
    ],
)
def test_existing_public_unknown_project_and_non_project_errors_propagate_identity(
    unknown_error: BaseException,
) -> None:
    factory = _Factory(claim_error=unknown_error)
    with pytest.raises(type(unknown_error)) as raised:
        _service(factory).claim_next_work_intent(CLAIM)
    assert raised.value is unknown_error
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
