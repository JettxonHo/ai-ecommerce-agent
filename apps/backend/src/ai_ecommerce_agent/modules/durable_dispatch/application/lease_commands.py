"""Immutable application commands for Durable Dispatch lease operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.shared_kernel import Revision

from ..domain.identity import DeliveryAttemptId, DispatchId, FencingToken
from ..domain.ownership import LeaseHolderId


def _require_instance(
    value: object, expected_type: type[object], field_name: str
) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} must be a {expected_type.__name__}")


def _validate_expiry(now: datetime, lease_expires_at: datetime) -> None:
    try:
        expires_later = lease_expires_at > now
    except TypeError as error:
        raise ValueError("lease datetimes must be comparable") from error
    if not expires_later:
        raise ValueError("lease_expires_at must be later than now")


@dataclass(frozen=True, slots=True)
class ClaimNextWorkIntent:
    """Request at most one eligible Work Intent claim."""

    holder_id: LeaseHolderId
    delivery_attempt_id: DeliveryAttemptId
    now: datetime
    lease_expires_at: datetime

    def __post_init__(self) -> None:
        _require_instance(self.holder_id, LeaseHolderId, "holder_id")
        _require_instance(
            self.delivery_attempt_id, DeliveryAttemptId, "delivery_attempt_id"
        )
        _require_instance(self.now, datetime, "now")
        _require_instance(self.lease_expires_at, datetime, "lease_expires_at")
        _validate_expiry(self.now, self.lease_expires_at)


@dataclass(frozen=True, slots=True)
class HeartbeatWorkIntentLease:
    """Request a heartbeat for one currently-owned Work Intent Lease."""

    dispatch_id: DispatchId
    delivery_attempt_id: DeliveryAttemptId
    holder_id: LeaseHolderId
    fencing_token: FencingToken
    expected_revision: Revision
    now: datetime
    lease_expires_at: datetime

    def __post_init__(self) -> None:
        _require_instance(self.dispatch_id, DispatchId, "dispatch_id")
        _require_instance(
            self.delivery_attempt_id, DeliveryAttemptId, "delivery_attempt_id"
        )
        _require_instance(self.holder_id, LeaseHolderId, "holder_id")
        _require_instance(self.fencing_token, FencingToken, "fencing_token")
        _require_instance(self.expected_revision, Revision, "expected_revision")
        _require_instance(self.now, datetime, "now")
        _require_instance(self.lease_expires_at, datetime, "lease_expires_at")
        if self.fencing_token.value <= 0:
            raise ValueError("fencing token must be greater than zero")
        _validate_expiry(self.now, self.lease_expires_at)


__all__ = ["ClaimNextWorkIntent", "HeartbeatWorkIntentLease"]
