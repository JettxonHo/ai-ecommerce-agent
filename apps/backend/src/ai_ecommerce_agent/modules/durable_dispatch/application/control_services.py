"""Concrete, transaction-bounded Durable Dispatch control operations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from typing import NoReturn, cast

from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchConstraintError,
    DurableDispatchPersistenceError,
    DurableDispatchRevisionConflictError,
)
from ai_ecommerce_agent.shared_kernel import ProjectError, Revision

from ..domain.snapshots import WorkIntentSnapshot
from ..domain.status import WorkIntentStatus
from .control_commands import (
    AcknowledgeWorkIntentStop,
    RequestWorkIntentCancellation,
    SupersedeWorkIntent,
)
from .control_errors import DurableDispatchControlError
from .control_protocols import DurableDispatchControlApplication
from .control_queries import CheckOwnedWorkIntentControl
from .control_results import (
    OwnedWorkIntentControlCheck,
    WorkIntentControlDisposition,
    WorkIntentSupersessionResult,
)
from .ports import DurableDispatchUnitOfWork, DurableDispatchUnitOfWorkFactory

_ControlInput = (
    CheckOwnedWorkIntentControl
    | RequestWorkIntentCancellation
    | SupersedeWorkIntent
    | AcknowledgeWorkIntentStop
)
_ACTIVE = (WorkIntentStatus.LEASED, WorkIntentStatus.IN_PROGRESS)
_UNOWNED = (
    WorkIntentStatus.PENDING,
    WorkIntentStatus.AVAILABLE,
    WorkIntentStatus.FAILED_RETRYABLE,
)
_ERRORS = {
    "not_found": ("control", "The Work Intent was not found", False, "refresh"),
    "revision_conflict": (
        "concurrency",
        "The Work Intent revision does not match the command",
        False,
        "refresh",
    ),
    "ownership_lost": (
        "ownership",
        "The Work Intent Lease is no longer current",
        False,
        "reclaim",
    ),
    "invalid_state": (
        "lifecycle",
        "The Work Intent cannot be changed in its current state",
        False,
        "refresh",
    ),
    "invalid_time": (
        "validation",
        "Caller time and Lease expiry are not comparable",
        False,
        "correct_time",
    ),
    "constraint_violation": (
        "persistence",
        "The Work Intent change violates a persistence constraint",
        False,
        "manual_recovery",
    ),
    "persistence_error": (
        "persistence",
        "Durable Dispatch persistence is unavailable",
        True,
        "retry_later",
    ),
}


def _error(
    command: _ControlInput,
    code: str,
    snapshot: WorkIntentSnapshot | None = None,
) -> DurableDispatchControlError:
    category, message, retryability, recovery = _ERRORS[code]
    attempt = getattr(command, "delivery_attempt_id", None)
    return DurableDispatchControlError(
        error_code=code,
        category=category,
        message=message,
        retryability=retryability,
        relevant_dispatch_id=(
            snapshot.envelope.dispatch_id
            if snapshot is not None
            else command.dispatch_id
        ),
        delivery_attempt_id=attempt,
        expected_revision=command.expected_revision,
        conflicting_state=snapshot.status if snapshot is not None else None,
        recovery_hint=recovery,
    )


def _raise(
    command: _ControlInput, code: str, snapshot: WorkIntentSnapshot | None = None
) -> NoReturn:
    raise _error(command, code, snapshot)


def _translate(
    error: ProjectError, command: _ControlInput
) -> DurableDispatchControlError | None:
    if isinstance(error, DurableDispatchRevisionConflictError):
        return _error(command, "revision_conflict")
    if isinstance(error, DurableDispatchConstraintError):
        return _error(command, "constraint_violation")
    if isinstance(error, DurableDispatchPersistenceError):
        return _error(command, "persistence_error")
    return None


def _run(
    factory: DurableDispatchUnitOfWorkFactory,
    command: _ControlInput,
    operation: Callable[[DurableDispatchUnitOfWork], object],
) -> object:
    try:
        with factory() as uow:
            return operation(uow)
    except DurableDispatchControlError:
        raise
    except ProjectError as error:
        translated = _translate(error, command)
        if translated is None:
            raise
        raise translated from error


def _load(uow: DurableDispatchUnitOfWork, command: _ControlInput) -> WorkIntentSnapshot:
    snapshot = uow.work_intents.get(command.dispatch_id)
    if snapshot is None:
        _raise(command, "not_found")
    return snapshot


def _require_revision(
    command: _ControlInput,
    snapshot: WorkIntentSnapshot,
    *,
    code: str = "revision_conflict",
) -> None:
    if snapshot.revision != command.expected_revision:
        _raise(command, code, snapshot)


def _require_state(command: _ControlInput, snapshot: WorkIntentSnapshot) -> None:
    if snapshot.status not in _ACTIVE and snapshot.current_lease is not None:
        _raise(command, "invalid_state", snapshot)


def _current_time(
    command: _ControlInput, snapshot: WorkIntentSnapshot, now: datetime
) -> bool:
    lease = snapshot.current_lease
    if lease is None:
        return False
    try:
        return now < lease.lease_expires_at
    except TypeError as error:
        raise _error(command, "invalid_time", snapshot) from error


def _owner_current(
    command: CheckOwnedWorkIntentControl | AcknowledgeWorkIntentStop,
    snapshot: WorkIntentSnapshot,
) -> bool:
    lease = snapshot.current_lease
    return bool(
        snapshot.status in _ACTIVE
        and lease is not None
        and lease.dispatch_id == command.dispatch_id
        and lease.delivery_attempt_id == command.delivery_attempt_id
        and lease.holder_id == command.holder_id
        and lease.fencing_token == command.fencing_token
        and _current_time(command, snapshot, command.now)
    )


def _disposition(snapshot: WorkIntentSnapshot) -> WorkIntentControlDisposition:
    if snapshot.superseded_by is not None:
        return WorkIntentControlDisposition.STOP_FOR_SUPERSESSION
    if snapshot.cancellation_requested:
        return WorkIntentControlDisposition.STOP_FOR_CANCELLATION
    return WorkIntentControlDisposition.CONTINUE_EXECUTION


def _commit_snapshot(
    uow: DurableDispatchUnitOfWork,
    previous: WorkIntentSnapshot,
    result: WorkIntentSnapshot,
) -> WorkIntentSnapshot:
    if result is not previous:
        uow.work_intents.save(result, expected_revision=previous.revision)
    uow.commit()
    return result


class DurableDispatchControlApplicationService(DurableDispatchControlApplication):
    """Run one Durable Dispatch control operation in one short transaction."""

    def __init__(self, uow_factory: DurableDispatchUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def _check(
        self, uow: DurableDispatchUnitOfWork, query: CheckOwnedWorkIntentControl
    ) -> OwnedWorkIntentControlCheck:
        snapshot = _load(uow, query)
        if not _owner_current(query, snapshot):
            _raise(query, "ownership_lost", snapshot)
        if snapshot.revision < query.expected_revision:
            _raise(query, "ownership_lost", snapshot)
        if snapshot.revision > query.expected_revision and not (
            snapshot.cancellation_requested or snapshot.superseded_by is not None
        ):
            _raise(query, "ownership_lost", snapshot)
        return OwnedWorkIntentControlCheck(snapshot, _disposition(snapshot))

    def check_owned_work_intent_control(
        self, query: CheckOwnedWorkIntentControl
    ) -> OwnedWorkIntentControlCheck:
        return cast(
            OwnedWorkIntentControlCheck,
            _run(self._uow_factory, query, lambda uow: self._check(uow, query)),
        )

    def _cancel(
        self, uow: DurableDispatchUnitOfWork, command: RequestWorkIntentCancellation
    ) -> WorkIntentSnapshot:
        snapshot = _load(uow, command)
        _require_revision(command, snapshot)
        _require_state(command, snapshot)
        if snapshot.status in _ACTIVE:
            if snapshot.superseded_by is not None or snapshot.cancellation_requested:
                result = snapshot
            elif _current_time(command, snapshot, command.now):
                result = replace(
                    snapshot,
                    cancellation_requested=True,
                    revision=snapshot.revision.next(),
                )
            else:
                result = replace(
                    snapshot,
                    status=WorkIntentStatus.CANCELLED,
                    cancellation_requested=True,
                    current_lease=None,
                    revision=snapshot.revision.next(),
                )
        elif snapshot.status in _UNOWNED:
            if snapshot.superseded_by is not None:
                _raise(command, "invalid_state", snapshot)
            result = replace(
                snapshot,
                status=WorkIntentStatus.CANCELLED,
                cancellation_requested=True,
                current_lease=None,
                revision=snapshot.revision.next(),
            )
        elif (
            snapshot.status is WorkIntentStatus.CANCELLED
            and snapshot.cancellation_requested
            and snapshot.superseded_by is None
        ):
            result = snapshot
        else:
            _raise(command, "invalid_state", snapshot)
        return _commit_snapshot(uow, snapshot, result)

    def request_work_intent_cancellation(
        self, command: RequestWorkIntentCancellation
    ) -> WorkIntentSnapshot:
        return cast(
            WorkIntentSnapshot,
            _run(self._uow_factory, command, lambda uow: self._cancel(uow, command)),
        )

    def _supersede(
        self, uow: DurableDispatchUnitOfWork, command: SupersedeWorkIntent
    ) -> WorkIntentSupersessionResult:
        old = _load(uow, command)
        _require_revision(command, old)
        _require_state(command, old)
        if old.status not in (*_ACTIVE, *_UNOWNED) or old.superseded_by is not None:
            _raise(command, "invalid_state", old)
        successor = WorkIntentSnapshot(
            command.successor_envelope,
            WorkIntentStatus.AVAILABLE,
            Revision.initial(),
            False,
            None,
            None,
        )
        if old.status in _ACTIVE and _current_time(command, old, command.now):
            updated = replace(
                old,
                revision=old.revision.next(),
                superseded_by=successor.envelope.dispatch_id,
            )
        else:
            updated = replace(
                old,
                status=WorkIntentStatus.SUPERSEDED,
                revision=old.revision.next(),
                current_lease=None,
                superseded_by=successor.envelope.dispatch_id,
            )
        uow.work_intents.add(successor)
        uow.work_intents.save(updated, expected_revision=old.revision)
        uow.commit()
        return WorkIntentSupersessionResult(updated, successor)

    def supersede_work_intent(
        self, command: SupersedeWorkIntent
    ) -> WorkIntentSupersessionResult:
        return cast(
            WorkIntentSupersessionResult,
            _run(self._uow_factory, command, lambda uow: self._supersede(uow, command)),
        )

    def _acknowledge(
        self, uow: DurableDispatchUnitOfWork, command: AcknowledgeWorkIntentStop
    ) -> WorkIntentSnapshot:
        snapshot = _load(uow, command)
        _require_revision(command, snapshot, code="ownership_lost")
        if not _owner_current(command, snapshot):
            _raise(command, "ownership_lost", snapshot)
        if not snapshot.cancellation_requested and snapshot.superseded_by is None:
            _raise(command, "invalid_state", snapshot)
        result = replace(
            snapshot,
            status=(
                WorkIntentStatus.SUPERSEDED
                if snapshot.superseded_by is not None
                else WorkIntentStatus.CANCELLED
            ),
            current_lease=None,
            revision=snapshot.revision.next(),
        )
        return _commit_snapshot(uow, snapshot, result)

    def acknowledge_work_intent_stop(
        self, command: AcknowledgeWorkIntentStop
    ) -> WorkIntentSnapshot:
        return cast(
            WorkIntentSnapshot,
            _run(
                self._uow_factory,
                command,
                lambda uow: self._acknowledge(uow, command),
            ),
        )


__all__ = ["DurableDispatchControlApplicationService"]
