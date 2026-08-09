"""Stable, catchable errors for Durable Dispatch control requests."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import Revision

from ..domain.identity import DeliveryAttemptId, DispatchId
from ..domain.status import WorkIntentStatus


def _require_text(value: object, name: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_optional(value: object, expected: type[object], name: str) -> None:
    if value is not None and not isinstance(value, expected):
        raise TypeError(f"{name} must be a {expected.__name__} or None")


@dataclass(slots=True)
class DurableDispatchControlError(Exception):
    """Framework-neutral control error without persistence details."""

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
        for name in ("error_code", "category", "message"):
            _require_text(getattr(self, name), name)
        if type(self.retryability) is not bool:
            raise TypeError("retryability must be a bool")
        _require_optional(self.relevant_dispatch_id, DispatchId, "relevant_dispatch_id")
        _require_optional(
            self.delivery_attempt_id, DeliveryAttemptId, "delivery_attempt_id"
        )
        _require_optional(self.expected_revision, Revision, "expected_revision")
        _require_optional(self.conflicting_state, WorkIntentStatus, "conflicting_state")
        if self.recovery_hint is not None and type(self.recovery_hint) is not str:
            raise TypeError("recovery_hint must be a string or None")
        Exception.__init__(self, self.message)


__all__ = ["DurableDispatchControlError"]
