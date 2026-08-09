"""Immutable queries for owned Durable Dispatch control checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.shared_kernel import Revision

from ..domain.identity import DeliveryAttemptId, DispatchId, FencingToken
from ..domain.ownership import LeaseHolderId


def _require(value: object, expected: type[object], name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError(f"{name} must be a {expected.__name__}")


@dataclass(frozen=True, slots=True)
class CheckOwnedWorkIntentControl:
    """Caller-supplied identity and generation for an owned-work check."""

    dispatch_id: DispatchId
    delivery_attempt_id: DeliveryAttemptId
    holder_id: LeaseHolderId
    fencing_token: FencingToken
    expected_revision: Revision
    now: datetime

    def __post_init__(self) -> None:
        _require(self.dispatch_id, DispatchId, "dispatch_id")
        _require(self.delivery_attempt_id, DeliveryAttemptId, "delivery_attempt_id")
        _require(self.holder_id, LeaseHolderId, "holder_id")
        _require(self.fencing_token, FencingToken, "fencing_token")
        _require(self.expected_revision, Revision, "expected_revision")
        _require(self.now, datetime, "now")


__all__ = ["CheckOwnedWorkIntentControl"]
