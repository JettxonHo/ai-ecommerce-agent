"""Immutable Durable Dispatch lease ownership value objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .identity import DeliveryAttemptId, DispatchId, FencingToken


@dataclass(frozen=True, slots=True)
class LeaseHolderId:
    """Opaque identity for the worker currently holding a lease."""

    value: str

    def __post_init__(self) -> None:
        if type(self.value) is not str:
            raise TypeError("lease holder value must be a string")
        if not self.value.strip():
            raise ValueError("lease holder value must not be empty")


def _require_instance(
    value: object, expected_type: type[object], field_name: str
) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} must be a {expected_type.__name__}")


@dataclass(frozen=True, slots=True)
class WorkIntentLease:
    """Immutable ownership snapshot for one claimed Work Intent."""

    dispatch_id: DispatchId
    delivery_attempt_id: DeliveryAttemptId
    holder_id: LeaseHolderId
    fencing_token: FencingToken
    lease_expires_at: datetime

    def __post_init__(self) -> None:
        _require_instance(self.dispatch_id, DispatchId, "dispatch_id")
        _require_instance(
            self.delivery_attempt_id,
            DeliveryAttemptId,
            "delivery_attempt_id",
        )
        _require_instance(self.holder_id, LeaseHolderId, "holder_id")
        _require_instance(self.fencing_token, FencingToken, "fencing_token")
        _require_instance(self.lease_expires_at, datetime, "lease_expires_at")
