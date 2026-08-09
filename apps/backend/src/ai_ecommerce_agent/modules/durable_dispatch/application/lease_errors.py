"""Stable, catchable errors for Durable Dispatch lease application intents."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import Revision

from ..domain.identity import DeliveryAttemptId, DispatchId
from ..domain.status import WorkIntentStatus


def _require_non_empty_builtin_text(value: object, field_name: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be a string")
    if not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_optional_instance(
    value: object, expected_type: type[object], field_name: str
) -> None:
    if value is not None and not isinstance(value, expected_type):
        raise TypeError(f"{field_name} must be a {expected_type.__name__} or None")


@dataclass(slots=True)
class DurableDispatchLeaseError(Exception):
    """Framework-neutral ownership error with no persistence context leak."""

    error_code: str
    category: str
    message: str
    retryability: bool
    relevant_dispatch_id: DispatchId | None
    delivery_attempt_id: DeliveryAttemptId | None = None
    expected_revision: Revision | None = None
    conflicting_state: WorkIntentStatus | None = None
    recovery_hint: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("error_code", "category", "message"):
            _require_non_empty_builtin_text(getattr(self, field_name), field_name)
        if type(self.retryability) is not bool:
            raise TypeError("retryability must be a bool")
        _require_optional_instance(
            self.relevant_dispatch_id, DispatchId, "relevant_dispatch_id"
        )
        _require_optional_instance(
            self.delivery_attempt_id, DeliveryAttemptId, "delivery_attempt_id"
        )
        _require_optional_instance(
            self.expected_revision, Revision, "expected_revision"
        )
        _require_optional_instance(
            self.conflicting_state, WorkIntentStatus, "conflicting_state"
        )
        if self.recovery_hint is not None and type(self.recovery_hint) is not str:
            raise TypeError("recovery_hint must be a string or None")
        Exception.__init__(self, self.message)


__all__ = ["DurableDispatchLeaseError"]
