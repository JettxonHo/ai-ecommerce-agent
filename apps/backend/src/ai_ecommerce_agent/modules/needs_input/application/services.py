"""Transaction-bounded Needs Input application operations."""

from __future__ import annotations

from datetime import UTC, datetime

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

from ..domain.evidence import InsufficientResultEvidence
from ..domain.snapshots import NeedsInputActionRequestSnapshot, NeedsInputStatus
from .commands import ResolveNeedsInput
from .errors import (
    NeedsInputApplicationError,
    NeedsInputCapabilityConflictError,
    NeedsInputIdempotencyConflictError,
    NeedsInputNotFoundError,
    NeedsInputPersistenceError,
    NeedsInputRevisionConflictError,
    NeedsInputRevisionPersistenceError,
)
from .ports import NeedsInputRequestRepository, NeedsInputUnitOfWorkFactory
from .protocols import NeedsInputApplication
from .results import ResolveNeedsInputResult


def _action_request_id(evidence: InsufficientResultEvidence) -> str:
    """Build a deterministic Task/result identity for safe replay."""

    return (
        f"needs-input-{evidence.task_id.value}-"
        f"{evidence.input_revision.value}-{evidence.result_revision.value}"
    )


def _now() -> datetime:
    return datetime.now(UTC)


class NeedsInputApplicationService(NeedsInputApplication):
    """Publish and read one Task-scoped request through a typed UoW."""

    def __init__(self, uow_factory: NeedsInputUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def publish_from_result(
        self, evidence: InsufficientResultEvidence
    ) -> NeedsInputActionRequestSnapshot:
        try:
            with self._uow_factory() as uow:
                created = self.publish_from_result_in_transaction(
                    uow.needs_input_requests, evidence
                )
                uow.commit()
                return created
        except NeedsInputApplicationError:
            raise
        except NeedsInputRevisionPersistenceError as error:
            raise NeedsInputRevisionConflictError() from error
        except NeedsInputPersistenceError as error:
            raise NeedsInputApplicationError(
                "persistence_error",
                "Needs Input persistence is temporarily unavailable.",
                retryability=True,
            ) from error

    def publish_from_result_in_transaction(
        self,
        requests: NeedsInputRequestRepository,
        evidence: InsufficientResultEvidence,
    ) -> NeedsInputActionRequestSnapshot:
        """Publish through a caller-owned transaction without committing it."""

        action_request_id = _action_request_id(evidence)
        current = requests.get_current(evidence.task_id)
        if (
            current is not None
            and current.status is NeedsInputStatus.OPEN
            and current.action_request_id == action_request_id
        ):
            # A deterministic result replay does not create a second request
            # or mutate Current Truth.
            return current

        now = _now()
        created = NeedsInputActionRequestSnapshot.from_evidence(
            evidence,
            action_request_id=action_request_id,
            now=now,
        )
        if current is not None:
            requests.save(
                current.supersede(action_request_id, now=now),
                expected_revision=current.revision,
            )
        requests.add(created)
        return created

    def supersede_current_for_result_in_transaction(
        self,
        requests: NeedsInputRequestRepository,
        *,
        task_id: TaskId,
        input_revision: Revision,
        result_revision: Revision,
    ) -> NeedsInputActionRequestSnapshot | None:
        """Clear an obsolete blocker inside the result commit transaction.

        A sufficient result has no replacement Needs Input request.  The
        current open request therefore remains durable history as
        ``superseded`` with a null successor; replacement Needs Input
        publication continues to use the non-null same-Task FK path above.
        """

        del input_revision, result_revision
        current = requests.get_current(task_id)
        if current is None:
            return None
        superseded = current.supersede(None, now=_now())
        requests.save(superseded, expected_revision=current.revision)
        return superseded

    def get_current_request(
        self, task_id: TaskId
    ) -> NeedsInputActionRequestSnapshot | None:
        try:
            with self._uow_factory() as uow:
                return uow.needs_input_requests.get_current(task_id)
        except NeedsInputPersistenceError as error:
            raise NeedsInputApplicationError(
                "persistence_error",
                "Needs Input persistence is temporarily unavailable.",
                retryability=True,
            ) from error

    def get_action_request(
        self, action_request_id: str
    ) -> NeedsInputActionRequestSnapshot:
        try:
            with self._uow_factory() as uow:
                request = uow.needs_input_requests.get(action_request_id)
                if request is None:
                    raise NeedsInputNotFoundError()
                return request
        except NeedsInputApplicationError:
            raise
        except NeedsInputPersistenceError as error:
            raise NeedsInputApplicationError(
                "persistence_error",
                "Needs Input persistence is temporarily unavailable.",
                retryability=True,
            ) from error

    def resolve_needs_input(
        self, command: ResolveNeedsInput
    ) -> ResolveNeedsInputResult:
        try:
            with self._uow_factory() as uow:
                requests = uow.needs_input_requests
                current = requests.get(command.action_request_id)
                if current is None:
                    raise NeedsInputNotFoundError()
                if current.status in (
                    NeedsInputStatus.RESOLVED,
                    NeedsInputStatus.CANCELLED,
                ):
                    if current.revision != command.expected_revision.next():
                        raise NeedsInputRevisionConflictError()
                    if (
                        current.resolution_idempotency_key == command.idempotency_key
                        and current.resolution_type == command.resolution_type
                        and current.resolution_payload == command.resolution_payload
                    ):
                        return ResolveNeedsInputResult(
                            action_request=current,
                            task_id=current.task_id,
                            replayed=True,
                        )
                    raise NeedsInputIdempotencyConflictError()
                if current.status is not NeedsInputStatus.OPEN:
                    raise NeedsInputCapabilityConflictError()
                if current.revision != command.expected_revision:
                    raise NeedsInputRevisionConflictError()
                if command.resolution_type not in current.allowed_resolution_types:
                    raise NeedsInputCapabilityConflictError()
                resolved = current.resolved(
                    idempotency_key=command.idempotency_key,
                    resolution_type=command.resolution_type,
                    resolution_payload=command.resolution_payload,
                    now=_now(),
                    cancelled=command.resolution_type == "cancel_path",
                )
                requests.save(resolved, expected_revision=current.revision)
                uow.commit()
                return ResolveNeedsInputResult(
                    action_request=resolved,
                    task_id=resolved.task_id,
                )
        except NeedsInputApplicationError:
            raise
        except NeedsInputRevisionPersistenceError as error:
            raise NeedsInputRevisionConflictError() from error
        except NeedsInputPersistenceError as error:
            raise NeedsInputApplicationError(
                "persistence_error",
                "Needs Input persistence is temporarily unavailable.",
                retryability=True,
            ) from error


__all__ = ["NeedsInputApplicationService"]
