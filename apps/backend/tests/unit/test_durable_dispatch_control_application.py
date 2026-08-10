"""Unit evidence for the Durable Dispatch control application seam."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import TracebackType
from typing import Self, cast

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWorkState
from ai_ecommerce_agent.modules.durable_dispatch.application.control_commands import (
    AcknowledgeWorkIntentStop,
    RequestWorkIntentCancellation,
    SupersedeWorkIntent,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_errors import (
    DurableDispatchControlError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_queries import (
    CheckOwnedWorkIntentControl,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_results import (
    WorkIntentControlDisposition,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_services import (
    DurableDispatchControlApplicationService,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchConstraintError,
    DurableDispatchPersistenceError,
    DurableDispatchRevisionConflictError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.ports import (
    DurableDispatchUnitOfWork,
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
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ProjectError,
    ResourceReference,
    Revision,
    RunId,
)

pytestmark = pytest.mark.unit

NOW = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
LATER = NOW + timedelta(hours=1)


def _envelope(
    suffix: str = "old",
    *,
    rerun_of: DispatchId | None = None,
) -> WorkIntentEnvelope:
    return WorkIntentEnvelope(
        DispatchId(f"dispatch-{suffix}"),
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
        rerun_of,
        f"ordering-{suffix}",
        NOW,
        NOW,
    )


def _snapshot(
    suffix: str = "old",
    *,
    status: WorkIntentStatus = WorkIntentStatus.LEASED,
    revision: int = 3,
    cancellation_requested: bool = False,
    lease: WorkIntentLease | None = None,
    with_lease: bool = True,
    superseded_by: DispatchId | None = None,
) -> WorkIntentSnapshot:
    envelope = _envelope(suffix)
    if lease is None and with_lease:
        lease = WorkIntentLease(
            envelope.dispatch_id,
            DeliveryAttemptId(f"attempt-{suffix}"),
            LeaseHolderId(f"holder-{suffix}"),
            FencingToken(4),
            LATER,
        )
    return WorkIntentSnapshot(
        envelope,
        status,
        Revision(revision),
        cancellation_requested,
        lease,
        superseded_by,
    )


def _query(
    snapshot: WorkIntentSnapshot, *, expected: int | None = None
) -> CheckOwnedWorkIntentControl:
    assert snapshot.current_lease is not None
    lease = snapshot.current_lease
    return CheckOwnedWorkIntentControl(
        snapshot.envelope.dispatch_id,
        lease.delivery_attempt_id,
        lease.holder_id,
        lease.fencing_token,
        Revision(snapshot.revision.value if expected is None else expected),
        NOW,
    )


def _cancel(
    snapshot: WorkIntentSnapshot, *, expected: int | None = None
) -> RequestWorkIntentCancellation:
    return RequestWorkIntentCancellation(
        snapshot.envelope.dispatch_id,
        Revision(snapshot.revision.value if expected is None else expected),
        NOW,
    )


def _ack(
    snapshot: WorkIntentSnapshot, *, expected: int | None = None
) -> AcknowledgeWorkIntentStop:
    assert snapshot.current_lease is not None
    lease = snapshot.current_lease
    return AcknowledgeWorkIntentStop(
        snapshot.envelope.dispatch_id,
        lease.delivery_attempt_id,
        lease.holder_id,
        lease.fencing_token,
        Revision(snapshot.revision.value if expected is None else expected),
        NOW,
    )


class _Repository:
    def __init__(self, owner: _FakeUow) -> None:
        self._owner = owner

    def get(self, dispatch_id: DispatchId) -> WorkIntentSnapshot | None:
        self._owner.events.append(("get", dispatch_id))
        if self._owner.get_error is not None:
            raise self._owner.get_error
        return self._owner.working.get(dispatch_id)

    def add(self, snapshot: WorkIntentSnapshot) -> None:
        self._owner.events.append(("add", snapshot))
        if self._owner.add_error is not None:
            raise self._owner.add_error
        if snapshot.envelope.dispatch_id in self._owner.working:
            raise DurableDispatchConstraintError(constraint_name="pk")
        self._owner.working[snapshot.envelope.dispatch_id] = snapshot

    def save(
        self, snapshot: WorkIntentSnapshot, *, expected_revision: Revision
    ) -> None:
        self._owner.events.append(("save", snapshot, expected_revision))
        if self._owner.save_error is not None:
            raise self._owner.save_error
        current = self._owner.working.get(snapshot.envelope.dispatch_id)
        if current is None or current.revision != expected_revision:
            raise DurableDispatchRevisionConflictError(
                dispatch_id=snapshot.envelope.dispatch_id.value,
                expected_revision=expected_revision,
            )
        self._owner.working[snapshot.envelope.dispatch_id] = snapshot


class _FakeUow:
    def __init__(
        self,
        store: dict[DispatchId, WorkIntentSnapshot],
        *,
        get_error: BaseException | None = None,
        add_error: BaseException | None = None,
        save_error: BaseException | None = None,
        commit_error: BaseException | None = None,
    ) -> None:
        self.store = store
        self.working: dict[DispatchId, WorkIntentSnapshot] = {}
        self.events: list[tuple[object, ...]] = []
        self.get_error = get_error
        self.add_error = add_error
        self.save_error = save_error
        self.commit_error = commit_error
        self._state = UnitOfWorkState.NEW
        self.commits = 0
        self.rollbacks = 0
        self.closes = 0
        self._repository = _Repository(self)

    @property
    def state(self) -> UnitOfWorkState:
        return self._state

    @property
    def work_intents(self) -> _Repository:
        return self._repository

    def __enter__(self) -> Self:
        self.events.append(("enter",))
        self.working = dict(self.store)
        self._state = UnitOfWorkState.ACTIVE
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc_value, traceback
        if self._state is UnitOfWorkState.ACTIVE:
            self.rollback()
        self.close()

    def commit(self) -> None:
        self.events.append(("commit",))
        self.commits += 1
        if self.commit_error is not None:
            raise self.commit_error
        self.store.clear()
        self.store.update(self.working)
        self._state = UnitOfWorkState.COMMITTED

    def rollback(self) -> None:
        self.events.append(("rollback",))
        self.rollbacks += 1
        self._state = UnitOfWorkState.ROLLED_BACK

    def close(self) -> None:
        if self._state is UnitOfWorkState.CLOSED:
            return
        self.events.append(("close",))
        self.closes += 1
        self._state = UnitOfWorkState.CLOSED


class _Factory:
    def __init__(
        self,
        *snapshots: WorkIntentSnapshot,
        get_error: BaseException | None = None,
        add_error: BaseException | None = None,
        save_error: BaseException | None = None,
        commit_error: BaseException | None = None,
    ) -> None:
        self.store = {snapshot.envelope.dispatch_id: snapshot for snapshot in snapshots}
        self.options = {
            "get_error": get_error,
            "add_error": add_error,
            "save_error": save_error,
            "commit_error": commit_error,
        }
        self.uows: list[_FakeUow] = []

    def __call__(self) -> DurableDispatchUnitOfWork:
        uow = _FakeUow(self.store, **self.options)
        self.uows.append(uow)
        return cast(DurableDispatchUnitOfWork, uow)


def test_control_query_uses_fresh_uow_without_commit_and_observes_stop() -> None:
    snapshot = _snapshot(cancellation_requested=True)
    factory = _Factory(snapshot)
    result = DurableDispatchControlApplicationService(
        factory
    ).check_owned_work_intent_control(_query(snapshot, expected=2))

    assert result.snapshot is snapshot
    assert result.disposition is WorkIntentControlDisposition.STOP_FOR_CANCELLATION
    uow = factory.uows[0]
    assert uow.commits == 0
    assert uow.rollbacks == 1
    assert uow.closes == 1


def test_query_allows_only_authoritative_newer_stop_revision() -> None:
    snapshot = _snapshot(revision=4, superseded_by=DispatchId("dispatch-next"))
    factory = _Factory(snapshot)
    result = DurableDispatchControlApplicationService(
        factory
    ).check_owned_work_intent_control(_query(snapshot, expected=3))
    assert result.snapshot is snapshot
    assert result.disposition is WorkIntentControlDisposition.STOP_FOR_SUPERSESSION

    older_result = DurableDispatchControlApplicationService(
        _Factory(snapshot)
    ).check_owned_work_intent_control(_query(snapshot, expected=2))
    assert older_result.snapshot is snapshot
    assert (
        older_result.disposition is WorkIntentControlDisposition.STOP_FOR_SUPERSESSION
    )

    no_stop = _snapshot(revision=4)
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(
            _Factory(no_stop)
        ).check_owned_work_intent_control(_query(no_stop, expected=3))
    assert raised.value.error_code == "ownership_lost"


def test_active_cancellation_preserves_lease_and_commits_once() -> None:
    snapshot = _snapshot()
    factory = _Factory(snapshot)
    result = DurableDispatchControlApplicationService(
        factory
    ).request_work_intent_cancellation(_cancel(snapshot))
    assert result.status is WorkIntentStatus.LEASED
    assert result.cancellation_requested is True
    assert result.revision == Revision(4)
    assert result.current_lease is snapshot.current_lease
    uow = factory.uows[0]
    assert uow.commits == 1
    assert [event[0] for event in uow.events] == [
        "enter",
        "get",
        "save",
        "commit",
        "close",
    ]


@pytest.mark.parametrize(
    "status",
    [
        WorkIntentStatus.PENDING,
        WorkIntentStatus.AVAILABLE,
        WorkIntentStatus.FAILED_RETRYABLE,
    ],
)
def test_unowned_cancellation_terminalizes_and_repeated_cancel_is_noop(
    status: WorkIntentStatus,
) -> None:
    snapshot = _snapshot(status=status, with_lease=False)
    factory = _Factory(snapshot)
    result = DurableDispatchControlApplicationService(
        factory
    ).request_work_intent_cancellation(_cancel(snapshot))
    assert result.status is WorkIntentStatus.CANCELLED
    assert result.cancellation_requested is True
    assert result.current_lease is None
    assert result.revision == Revision(4)

    second_factory = _Factory(result)
    repeated = DurableDispatchControlApplicationService(
        second_factory
    ).request_work_intent_cancellation(_cancel(result))
    assert repeated is result
    assert second_factory.uows[0].commits == 1
    assert not any(event[0] == "save" for event in second_factory.uows[0].events)


def test_supersession_adds_successor_before_old_cas_and_preserves_active_owner() -> (
    None
):
    old = _snapshot()
    successor_envelope = _envelope("next", rerun_of=old.envelope.dispatch_id)
    factory = _Factory(old)
    result = DurableDispatchControlApplicationService(factory).supersede_work_intent(
        SupersedeWorkIntent(
            old.envelope.dispatch_id, successor_envelope, old.revision, NOW
        )
    )
    assert result.superseded.status is WorkIntentStatus.LEASED
    assert result.superseded.current_lease is old.current_lease
    assert result.superseded.superseded_by is successor_envelope.dispatch_id
    assert result.successor.status is WorkIntentStatus.AVAILABLE
    assert result.successor.revision == Revision.initial()
    assert [event[0] for event in factory.uows[0].events] == [
        "enter",
        "get",
        "add",
        "save",
        "commit",
        "close",
    ]


@pytest.mark.parametrize(
    ("status", "with_lease", "expected_status"),
    [
        (WorkIntentStatus.LEASED, True, WorkIntentStatus.LEASED),
        (WorkIntentStatus.IN_PROGRESS, True, WorkIntentStatus.IN_PROGRESS),
        (WorkIntentStatus.PENDING, False, WorkIntentStatus.SUPERSEDED),
        (WorkIntentStatus.AVAILABLE, False, WorkIntentStatus.SUPERSEDED),
        (WorkIntentStatus.FAILED_RETRYABLE, False, WorkIntentStatus.SUPERSEDED),
    ],
)
def test_supersession_classifies_each_eligible_status(
    status: WorkIntentStatus,
    with_lease: bool,
    expected_status: WorkIntentStatus,
) -> None:
    old = _snapshot(f"supersede-{status.value}", status=status, with_lease=with_lease)
    successor = _envelope(
        f"supersede-{status.value}-next", rerun_of=old.envelope.dispatch_id
    )
    factory = _Factory(old)
    result = DurableDispatchControlApplicationService(factory).supersede_work_intent(
        SupersedeWorkIntent(old.envelope.dispatch_id, successor, old.revision, NOW)
    )
    assert result.superseded.status is expected_status
    assert result.superseded.revision == old.revision.next()
    assert result.successor.status is WorkIntentStatus.AVAILABLE
    if status in {WorkIntentStatus.LEASED, WorkIntentStatus.IN_PROGRESS}:
        assert result.superseded.current_lease is old.current_lease
    else:
        assert result.superseded.current_lease is None
    assert factory.uows[0].commits == 1


@pytest.mark.parametrize(
    "status",
    [
        WorkIntentStatus.SUCCEEDED,
        WorkIntentStatus.FAILED_TERMINAL,
        WorkIntentStatus.CANCELLED,
        WorkIntentStatus.SUPERSEDED,
    ],
)
def test_supersession_rejects_terminal_history(status: WorkIntentStatus) -> None:
    old = _snapshot(
        f"supersede-terminal-{status.value}", status=status, with_lease=False
    )
    successor = _envelope(
        f"supersede-terminal-{status.value}-next", rerun_of=old.envelope.dispatch_id
    )
    factory = _Factory(old)
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(factory).supersede_work_intent(
            SupersedeWorkIntent(old.envelope.dispatch_id, successor, old.revision, NOW)
        )
    assert raised.value.error_code == "invalid_state"
    assert factory.uows[0].commits == 0
    assert not any(event[0] == "add" for event in factory.uows[0].events)


def test_supersession_constraint_failure_rolls_back_without_orphan() -> None:
    old = _snapshot(status=WorkIntentStatus.AVAILABLE, with_lease=False)
    successor_envelope = _envelope("next", rerun_of=old.envelope.dispatch_id)
    factory = _Factory(
        old,
        add_error=DurableDispatchConstraintError(constraint_name="pk"),
    )
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(factory).supersede_work_intent(
            SupersedeWorkIntent(
                old.envelope.dispatch_id, successor_envelope, old.revision, NOW
            )
        )
    assert raised.value.error_code == "constraint_violation"
    assert set(factory.store) == {old.envelope.dispatch_id}
    assert factory.uows[0].rollbacks == 1


def test_acknowledgement_supersession_wins_and_clears_lease() -> None:
    snapshot = _snapshot(
        cancellation_requested=True,
        superseded_by=DispatchId("dispatch-next"),
    )
    factory = _Factory(snapshot)
    result = DurableDispatchControlApplicationService(
        factory
    ).acknowledge_work_intent_stop(_ack(snapshot))
    assert result.status is WorkIntentStatus.SUPERSEDED
    assert result.cancellation_requested is True
    assert result.superseded_by == snapshot.superseded_by
    assert result.current_lease is None
    assert result.revision == Revision(4)


def test_invalid_time_and_unknown_errors() -> None:
    snapshot = _snapshot()
    assert snapshot.current_lease is not None
    naive_expiry = replace(
        snapshot.current_lease, lease_expires_at=datetime(2026, 8, 10, 13)
    )
    invalid_time_snapshot = _snapshot(lease=naive_expiry)
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(
            _Factory(invalid_time_snapshot)
        ).request_work_intent_cancellation(_cancel(invalid_time_snapshot))
    assert raised.value.error_code == "invalid_time"
    assert raised.value.category == "validation"

    unknown = ProjectError.from_context("other", "unknown")
    with pytest.raises(ProjectError) as propagated:
        DurableDispatchControlApplicationService(
            _Factory(snapshot, get_error=unknown)
        ).request_work_intent_cancellation(_cancel(snapshot))
    assert propagated.value is unknown


def test_error_translation_carries_safe_revision_and_missing_identity() -> None:
    snapshot = _snapshot()
    conflict = DurableDispatchRevisionConflictError(
        dispatch_id=snapshot.envelope.dispatch_id.value,
        expected_revision=snapshot.revision,
    )
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(
            _Factory(snapshot, save_error=conflict)
        ).request_work_intent_cancellation(_cancel(snapshot))
    assert raised.value.error_code == "revision_conflict"
    assert raised.value.relevant_dispatch_id == snapshot.envelope.dispatch_id
    assert raised.value.expected_revision == snapshot.revision

    missing = _snapshot()
    with pytest.raises(DurableDispatchControlError) as not_found:
        DurableDispatchControlApplicationService(
            _Factory()
        ).request_work_intent_cancellation(_cancel(missing))
    assert not_found.value.error_code == "not_found"


def test_acknowledgement_requires_a_stop_request_and_exact_owner() -> None:
    snapshot = _snapshot()
    with pytest.raises(DurableDispatchControlError) as no_stop:
        DurableDispatchControlApplicationService(
            _Factory(snapshot)
        ).acknowledge_work_intent_stop(_ack(snapshot))
    assert no_stop.value.error_code == "invalid_state"

    with pytest.raises(DurableDispatchControlError) as owner_lost:
        DurableDispatchControlApplicationService(
            _Factory(snapshot)
        ).acknowledge_work_intent_stop(
            AcknowledgeWorkIntentStop(
                snapshot.envelope.dispatch_id,
                DeliveryAttemptId("wrong-attempt"),
                snapshot.current_lease.holder_id,  # type: ignore[union-attr]
                snapshot.current_lease.fencing_token,  # type: ignore[union-attr]
                snapshot.revision,
                NOW,
            )
        )
    assert owner_lost.value.error_code == "ownership_lost"
    assert owner_lost.value.delivery_attempt_id == DeliveryAttemptId("wrong-attempt")

    with pytest.raises(DurableDispatchControlError) as stale_revision:
        DurableDispatchControlApplicationService(
            _Factory(snapshot)
        ).acknowledge_work_intent_stop(_ack(snapshot, expected=2))
    assert stale_revision.value.error_code == "ownership_lost"


def test_owned_check_accepts_in_progress_exact_owner() -> None:
    snapshot = _snapshot(status=WorkIntentStatus.IN_PROGRESS)
    factory = _Factory(snapshot)
    result = DurableDispatchControlApplicationService(
        factory
    ).check_owned_work_intent_control(_query(snapshot))
    assert result.snapshot is snapshot
    assert result.disposition is WorkIntentControlDisposition.CONTINUE_EXECUTION
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1


@pytest.mark.parametrize(
    ("status", "expected_status"),
    [
        (WorkIntentStatus.LEASED, WorkIntentStatus.LEASED),
        (WorkIntentStatus.IN_PROGRESS, WorkIntentStatus.IN_PROGRESS),
        (WorkIntentStatus.PENDING, WorkIntentStatus.CANCELLED),
        (WorkIntentStatus.AVAILABLE, WorkIntentStatus.CANCELLED),
        (WorkIntentStatus.FAILED_RETRYABLE, WorkIntentStatus.CANCELLED),
        (WorkIntentStatus.CANCELLED, WorkIntentStatus.CANCELLED),
    ],
)
def test_cancellation_classifies_active_unowned_and_cancelled_statuses(
    status: WorkIntentStatus, expected_status: WorkIntentStatus
) -> None:
    snapshot = _snapshot(
        status=status,
        with_lease=status in {WorkIntentStatus.LEASED, WorkIntentStatus.IN_PROGRESS},
        cancellation_requested=status is WorkIntentStatus.CANCELLED,
    )
    factory = _Factory(snapshot)
    result = DurableDispatchControlApplicationService(
        factory
    ).request_work_intent_cancellation(_cancel(snapshot))
    assert result.status is expected_status
    assert result.cancellation_requested is True
    if status in {WorkIntentStatus.LEASED, WorkIntentStatus.IN_PROGRESS}:
        assert result.current_lease is snapshot.current_lease
    assert factory.uows[0].commits == 1


@pytest.mark.parametrize(
    "status",
    [
        WorkIntentStatus.SUCCEEDED,
        WorkIntentStatus.FAILED_TERMINAL,
        WorkIntentStatus.SUPERSEDED,
    ],
)
def test_cancellation_rejects_terminal_history(status: WorkIntentStatus) -> None:
    snapshot = _snapshot(status=status, with_lease=False)
    factory = _Factory(snapshot)
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(
            factory
        ).request_work_intent_cancellation(_cancel(snapshot))
    assert raised.value.error_code == "invalid_state"
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1


def test_cancellation_rejects_contradictory_non_active_lease() -> None:
    snapshot = _snapshot(status=WorkIntentStatus.AVAILABLE)
    factory = _Factory(snapshot)
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(
            factory
        ).request_work_intent_cancellation(_cancel(snapshot))
    assert raised.value.error_code == "invalid_state"
    assert not any(event[0] == "save" for event in factory.uows[0].events)


@pytest.mark.parametrize(
    "snapshot",
    [
        _snapshot(status=WorkIntentStatus.IN_PROGRESS, with_lease=False),
        _snapshot(
            lease=WorkIntentLease(
                DispatchId("dispatch-old"),
                DeliveryAttemptId("attempt-old"),
                LeaseHolderId("holder-old"),
                FencingToken(4),
                NOW,
            )
        ),
    ],
)
def test_missing_or_expired_active_lease_terminalizes(
    snapshot: WorkIntentSnapshot,
) -> None:
    factory = _Factory(snapshot)
    result = DurableDispatchControlApplicationService(
        factory
    ).request_work_intent_cancellation(_cancel(snapshot))
    assert result.status is WorkIntentStatus.CANCELLED
    assert result.current_lease is None
    assert result.revision == snapshot.revision.next()
    assert factory.uows[0].commits == 1


def test_active_stop_requests_and_second_supersede_are_noop_or_rejected() -> None:
    active_cancel = _snapshot(cancellation_requested=True)
    cancel_factory = _Factory(active_cancel)
    cancelled = DurableDispatchControlApplicationService(
        cancel_factory
    ).request_work_intent_cancellation(_cancel(active_cancel))
    assert cancelled is active_cancel
    assert cancel_factory.uows[0].commits == 1
    assert not any(event[0] == "save" for event in cancel_factory.uows[0].events)

    active_superseded = _snapshot(superseded_by=DispatchId("dispatch-next"))
    sup_factory = _Factory(active_superseded)
    sup_noop = DurableDispatchControlApplicationService(
        sup_factory
    ).request_work_intent_cancellation(_cancel(active_superseded))
    assert sup_noop is active_superseded
    assert sup_factory.uows[0].commits == 1
    assert not any(event[0] == "save" for event in sup_factory.uows[0].events)

    successor = _envelope("second", rerun_of=active_superseded.envelope.dispatch_id)
    reject_factory = _Factory(active_superseded)
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(reject_factory).supersede_work_intent(
            SupersedeWorkIntent(
                active_superseded.envelope.dispatch_id,
                successor,
                active_superseded.revision,
                NOW,
            )
        )
    assert raised.value.error_code == "invalid_state"
    assert not any(event[0] == "add" for event in reject_factory.uows[0].events)


@pytest.mark.parametrize("case", ["lower", "mismatch", "expiry"])
def test_owned_check_rejects_lower_revision_owner_mismatch_and_expiry(
    case: str,
) -> None:
    snapshot = _snapshot()
    if case == "lower":
        query = _query(snapshot, expected=2)
    elif case == "mismatch":
        query = replace(_query(snapshot), holder_id=LeaseHolderId("wrong-holder"))
    else:
        assert snapshot.current_lease is not None
        snapshot = replace(
            snapshot,
            current_lease=replace(snapshot.current_lease, lease_expires_at=NOW),
        )
        query = _query(snapshot)
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(
            _Factory(snapshot)
        ).check_owned_work_intent_control(query)
    assert raised.value.error_code == "ownership_lost"


def test_error_translation_and_identity_preservation() -> None:
    snapshot = _snapshot()
    persistence = DurableDispatchPersistenceError()
    with pytest.raises(DurableDispatchControlError) as translated:
        DurableDispatchControlApplicationService(
            _Factory(snapshot, get_error=persistence)
        ).request_work_intent_cancellation(_cancel(snapshot))
    assert translated.value.error_code == "persistence_error"
    assert translated.value.retryability is True

    existing = DurableDispatchControlError(
        "existing", "control", "existing", False, snapshot.envelope.dispatch_id
    )
    with pytest.raises(DurableDispatchControlError) as same:
        DurableDispatchControlApplicationService(
            _Factory(snapshot, get_error=existing)
        ).request_work_intent_cancellation(_cancel(snapshot))
    assert same.value is existing

    runtime = RuntimeError("runtime")
    with pytest.raises(RuntimeError) as raw:
        DurableDispatchControlApplicationService(
            _Factory(snapshot, get_error=runtime)
        ).request_work_intent_cancellation(_cancel(snapshot))
    assert raw.value is runtime


def test_commit_failure_rolls_back_and_keeps_store_unchanged() -> None:
    snapshot = _snapshot()
    persistence = DurableDispatchPersistenceError()
    factory = _Factory(snapshot, commit_error=persistence)
    with pytest.raises(DurableDispatchControlError) as raised:
        DurableDispatchControlApplicationService(
            factory
        ).request_work_intent_cancellation(_cancel(snapshot))
    assert raised.value.error_code == "persistence_error"
    assert factory.uows[0].rollbacks == 1
    assert factory.store[snapshot.envelope.dispatch_id] is snapshot
