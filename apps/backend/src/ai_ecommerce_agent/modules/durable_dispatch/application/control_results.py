"""Immutable results for Durable Dispatch control observations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ai_ecommerce_agent.shared_kernel import Revision

from ..domain.snapshots import WorkIntentSnapshot
from ..domain.status import WorkIntentStatus


class WorkIntentControlDisposition(StrEnum):
    CONTINUE_EXECUTION = "continue_execution"
    STOP_FOR_CANCELLATION = "stop_for_cancellation"
    STOP_FOR_SUPERSESSION = "stop_for_supersession"


_ACTIVE_STATUSES = (WorkIntentStatus.LEASED, WorkIntentStatus.IN_PROGRESS)


def _require(value: object, expected: type[object], name: str) -> None:
    if not isinstance(value, expected):
        raise TypeError(f"{name} must be a {expected.__name__}")


@dataclass(frozen=True, slots=True)
class OwnedWorkIntentControlCheck:
    """One authoritative control disposition for an owned Work Intent."""

    snapshot: WorkIntentSnapshot
    disposition: WorkIntentControlDisposition

    def __post_init__(self) -> None:
        _require(self.snapshot, WorkIntentSnapshot, "snapshot")
        _require(self.disposition, WorkIntentControlDisposition, "disposition")
        if self.snapshot.status not in _ACTIVE_STATUSES:
            raise ValueError("control disposition requires an active Work Intent")
        has_cancellation = self.snapshot.cancellation_requested
        has_supersession = self.snapshot.superseded_by is not None
        if self.disposition is WorkIntentControlDisposition.CONTINUE_EXECUTION:
            if has_cancellation or has_supersession:
                raise ValueError("continue disposition contradicts a stop request")
        elif self.disposition is WorkIntentControlDisposition.STOP_FOR_CANCELLATION:
            if not has_cancellation or has_supersession:
                raise ValueError("cancellation disposition is not observable")
        elif not has_supersession:
            raise ValueError("supersession disposition is not observable")


@dataclass(frozen=True, slots=True)
class WorkIntentSupersessionResult:
    """Old and successor snapshots linked by an explicit rerun reference."""

    superseded: WorkIntentSnapshot
    successor: WorkIntentSnapshot

    def __post_init__(self) -> None:
        _require(self.superseded, WorkIntentSnapshot, "superseded")
        _require(self.successor, WorkIntentSnapshot, "successor")
        if self.superseded.superseded_by != self.successor.envelope.dispatch_id:
            raise ValueError("superseded snapshot must reference successor")
        if self.successor.envelope.rerun_of != self.superseded.envelope.dispatch_id:
            raise ValueError("successor must reference superseded dispatch")
        if self.successor.status is not WorkIntentStatus.AVAILABLE:
            raise ValueError("successor must be available")
        if self.successor.revision != Revision.initial():
            raise ValueError("successor revision must be initial")
        if self.successor.cancellation_requested:
            raise ValueError("successor cannot request cancellation")
        if self.successor.current_lease is not None:
            raise ValueError("successor cannot have a Lease")
        if self.successor.superseded_by is not None:
            raise ValueError("successor cannot request supersession")
        if self.superseded.status in (
            WorkIntentStatus.LEASED,
            WorkIntentStatus.IN_PROGRESS,
        ):
            if self.superseded.current_lease is None:
                raise ValueError("active superseded snapshot requires a Lease")
        elif self.superseded.status is WorkIntentStatus.SUPERSEDED:
            if self.superseded.current_lease is not None:
                raise ValueError("terminal superseded snapshot cannot have a Lease")
        else:
            raise ValueError("superseded snapshot has an invalid status")


__all__ = [
    "OwnedWorkIntentControlCheck",
    "WorkIntentControlDisposition",
    "WorkIntentSupersessionResult",
]
