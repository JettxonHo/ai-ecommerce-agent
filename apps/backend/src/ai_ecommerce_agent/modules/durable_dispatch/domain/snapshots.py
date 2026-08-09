"""Immutable current-state projection for a Durable Work Intent."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import Revision

from .envelope import WorkIntentEnvelope
from .identity import DispatchId
from .ownership import WorkIntentLease
from .status import WorkIntentStatus


def _require_instance(
    value: object, expected_type: type[object], field_name: str
) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} must be a {expected_type.__name__}")


@dataclass(frozen=True, slots=True)
class WorkIntentSnapshot:
    """Internal immutable projection, not an HTTP response or Current Truth."""

    envelope: WorkIntentEnvelope
    status: WorkIntentStatus
    revision: Revision
    cancellation_requested: bool
    current_lease: WorkIntentLease | None
    superseded_by: DispatchId | None = None

    def __post_init__(self) -> None:
        _require_instance(self.envelope, WorkIntentEnvelope, "envelope")
        _require_instance(self.status, WorkIntentStatus, "status")
        _require_instance(self.revision, Revision, "revision")
        if type(self.cancellation_requested) is not bool:
            raise TypeError("cancellation_requested must be a bool")
        if self.current_lease is not None:
            _require_instance(self.current_lease, WorkIntentLease, "current_lease")
            if self.current_lease.dispatch_id != self.envelope.dispatch_id:
                raise ValueError(
                    "current_lease dispatch_id must match envelope dispatch_id"
                )
        if self.superseded_by is not None:
            _require_instance(self.superseded_by, DispatchId, "superseded_by")
            if self.superseded_by == self.envelope.dispatch_id:
                raise ValueError("superseded_by must differ from envelope dispatch_id")
