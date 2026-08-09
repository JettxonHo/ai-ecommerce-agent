"""Concrete application use cases for Durable Dispatch lease ownership."""

from __future__ import annotations

from typing import NoReturn

from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchConstraintError,
    DurableDispatchPersistenceError,
    DurableDispatchRevisionConflictError,
)
from ai_ecommerce_agent.shared_kernel import ProjectError, Revision

from ..domain.identity import DispatchId
from ..domain.snapshots import WorkIntentSnapshot
from .lease_commands import ClaimNextWorkIntent, HeartbeatWorkIntentLease
from .lease_errors import DurableDispatchLeaseError
from .lease_protocols import DurableDispatchLeaseApplication
from .ports import DurableDispatchUnitOfWorkFactory

_LeaseCommand = ClaimNextWorkIntent | HeartbeatWorkIntentLease


def _command_dispatch_id(command: _LeaseCommand) -> DispatchId | None:
    if isinstance(command, HeartbeatWorkIntentLease):
        return command.dispatch_id
    return None


def _command_revision(command: _LeaseCommand) -> Revision | None:
    if isinstance(command, HeartbeatWorkIntentLease):
        return command.expected_revision
    return None


def _translated_error(
    *,
    error_code: str,
    category: str,
    message: str,
    retryability: bool,
    command: _LeaseCommand,
    recovery_hint: str,
    relevant_dispatch_id: DispatchId | None = None,
    expected_revision: Revision | None = None,
) -> DurableDispatchLeaseError:
    return DurableDispatchLeaseError(
        error_code=error_code,
        category=category,
        message=message,
        retryability=retryability,
        relevant_dispatch_id=relevant_dispatch_id
        if relevant_dispatch_id is not None
        else _command_dispatch_id(command),
        delivery_attempt_id=command.delivery_attempt_id,
        expected_revision=expected_revision
        if expected_revision is not None
        else _command_revision(command),
        conflicting_state=None,
        recovery_hint=recovery_hint,
    )


def _translate_project_error(
    error: ProjectError, command: _LeaseCommand
) -> DurableDispatchLeaseError | None:
    if isinstance(error, DurableDispatchRevisionConflictError):
        context = error.safe_context
        return _translated_error(
            error_code="revision_conflict",
            category="ownership",
            message="The Work Intent changed; reclaim before retrying",
            retryability=False,
            command=command,
            recovery_hint="reclaim",
            relevant_dispatch_id=DispatchId(context["dispatch_id"]),
            expected_revision=Revision(int(context["expected_revision"])),
        )
    if isinstance(error, DurableDispatchConstraintError):
        return _translated_error(
            error_code="constraint_violation",
            category="persistence",
            message=(
                "The Durable Dispatch lease change violates a persistence constraint"
            ),
            retryability=False,
            command=command,
            recovery_hint="manual_recovery",
        )
    if isinstance(error, DurableDispatchPersistenceError):
        return _translated_error(
            error_code="persistence_error",
            category="persistence",
            message="Durable Dispatch persistence is unavailable",
            retryability=True,
            command=command,
            recovery_hint="retry_later",
        )
    return None


def _lease_lost(command: HeartbeatWorkIntentLease) -> NoReturn:
    raise DurableDispatchLeaseError(
        error_code="lease_lost",
        category="ownership",
        message="Lease is no longer current",
        retryability=False,
        relevant_dispatch_id=command.dispatch_id,
        delivery_attempt_id=command.delivery_attempt_id,
        expected_revision=command.expected_revision,
        conflicting_state=None,
        recovery_hint="reclaim",
    )


class DurableDispatchLeaseApplicationService(DurableDispatchLeaseApplication):
    """Execute one claim or heartbeat in one short Durable transaction."""

    def __init__(self, uow_factory: DurableDispatchUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def claim_next_work_intent(
        self, command: ClaimNextWorkIntent
    ) -> WorkIntentSnapshot | None:
        try:
            with self._uow_factory() as uow:
                result = uow.work_intent_leases.claim_next(command)
                uow.commit()
                return result
        except DurableDispatchLeaseError:
            raise
        except ProjectError as error:
            translated = _translate_project_error(error, command)
            if translated is None:
                raise
            raise translated from error

    def heartbeat_work_intent_lease(
        self, command: HeartbeatWorkIntentLease
    ) -> WorkIntentSnapshot:
        try:
            with self._uow_factory() as uow:
                result = uow.work_intent_leases.heartbeat(command)
                if result is None:
                    _lease_lost(command)
                uow.commit()
                return result
        except DurableDispatchLeaseError:
            raise
        except ProjectError as error:
            translated = _translate_project_error(error, command)
            if translated is None:
                raise
            raise translated from error


__all__ = ["DurableDispatchLeaseApplicationService"]
