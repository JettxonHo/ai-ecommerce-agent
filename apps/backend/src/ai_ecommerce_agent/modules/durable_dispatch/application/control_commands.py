"""Immutable cancellation, supersession and stop-acknowledgement commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.shared_kernel import Revision

from ..domain.envelope import WorkIntentEnvelope
from ..domain.identity import DeliveryAttemptId, DispatchId, FencingToken
from ..domain.ownership import LeaseHolderId


def _require(value: object, expected: type[object], name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError(f"{name} must be a {expected.__name__}")


def _require_control_fields(
    dispatch_id: DispatchId, expected_revision: Revision, now: datetime
) -> None:
    _require(dispatch_id, DispatchId, "dispatch_id")
    _require(expected_revision, Revision, "expected_revision")
    _require(now, datetime, "now")


def _require_owned_fields(
    dispatch_id: DispatchId,
    delivery_attempt_id: DeliveryAttemptId,
    holder_id: LeaseHolderId,
    fencing_token: FencingToken,
    expected_revision: Revision,
    now: datetime,
) -> None:
    _require_control_fields(dispatch_id, expected_revision, now)
    _require(delivery_attempt_id, DeliveryAttemptId, "delivery_attempt_id")
    _require(holder_id, LeaseHolderId, "holder_id")
    _require(fencing_token, FencingToken, "fencing_token")


@dataclass(frozen=True, slots=True)
class RequestWorkIntentCancellation:
    """Request persisted cancellation without performing a transition."""

    dispatch_id: DispatchId
    expected_revision: Revision
    now: datetime

    def __post_init__(self) -> None:
        _require_control_fields(self.dispatch_id, self.expected_revision, self.now)


@dataclass(frozen=True, slots=True)
class SupersedeWorkIntent:
    """Request a successor Work Intent while preserving caller references."""

    dispatch_id: DispatchId
    successor_envelope: WorkIntentEnvelope
    expected_revision: Revision
    now: datetime

    def __post_init__(self) -> None:
        _require_control_fields(self.dispatch_id, self.expected_revision, self.now)
        _require(self.successor_envelope, WorkIntentEnvelope, "successor_envelope")
        if self.successor_envelope.dispatch_id == self.dispatch_id:
            raise ValueError("successor_envelope dispatch_id must differ")
        if self.successor_envelope.rerun_of != self.dispatch_id:
            raise ValueError("successor_envelope rerun_of must match dispatch_id")


@dataclass(frozen=True, slots=True)
class AcknowledgeWorkIntentStop:
    """Acknowledge a stop request for one currently-owned Work Intent."""

    dispatch_id: DispatchId
    delivery_attempt_id: DeliveryAttemptId
    holder_id: LeaseHolderId
    fencing_token: FencingToken
    expected_revision: Revision
    now: datetime

    def __post_init__(self) -> None:
        _require_owned_fields(
            self.dispatch_id,
            self.delivery_attempt_id,
            self.holder_id,
            self.fencing_token,
            self.expected_revision,
            self.now,
        )


__all__ = [
    "AcknowledgeWorkIntentStop",
    "RequestWorkIntentCancellation",
    "SupersedeWorkIntent",
]
