"""Transaction-neutral inputs for Durable Dispatch completion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.shared_kernel import ResourceReference, Revision

from ..domain.identity import DeliveryAttemptId, DispatchId, FencingToken
from ..domain.ownership import LeaseHolderId


def _require_exact(value: object, expected: type[object], field_name: str) -> None:
    if type(value) is not expected:
        raise TypeError(f"{field_name} must be a {expected.__name__}")


def _require_text(value: object, field_name: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be a string")
    if not value.strip():
        raise ValueError(f"{field_name} must be non-empty")


@dataclass(frozen=True, slots=True)
class CompleteOwnedWorkIntent:
    """Describe one caller-owned completion attempt without performing I/O."""

    dispatch_id: DispatchId
    delivery_attempt_id: DeliveryAttemptId
    holder_id: LeaseHolderId
    fencing_token: FencingToken
    expected_work_intent_revision: Revision
    expected_command_id: str
    expected_input_fingerprint: str
    expected_fingerprint_schema_version: str
    result_reference: ResourceReference
    now: datetime

    def __post_init__(self) -> None:
        _require_exact(self.dispatch_id, DispatchId, "dispatch_id")
        _require_exact(
            self.delivery_attempt_id, DeliveryAttemptId, "delivery_attempt_id"
        )
        _require_exact(self.holder_id, LeaseHolderId, "holder_id")
        _require_exact(self.fencing_token, FencingToken, "fencing_token")
        _require_exact(
            self.expected_work_intent_revision,
            Revision,
            "expected_work_intent_revision",
        )
        for field_name in (
            "expected_command_id",
            "expected_input_fingerprint",
            "expected_fingerprint_schema_version",
        ):
            _require_text(getattr(self, field_name), field_name)
        _require_exact(self.result_reference, ResourceReference, "result_reference")
        _require_exact(self.now, datetime, "now")


__all__ = ["CompleteOwnedWorkIntent"]
