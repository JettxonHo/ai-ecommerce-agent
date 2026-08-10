"""Immutable results for the Durable Dispatch completion participant."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import ResourceReference

from ..domain.snapshots import WorkIntentSnapshot
from ..domain.status import WorkIntentStatus


def _require_exact(value: object, expected: type[object], field_name: str) -> None:
    if type(value) is not expected:
        raise TypeError(f"{field_name} must be a {expected.__name__}")


@dataclass(frozen=True, slots=True)
class WorkIntentCompletionResult:
    """Return the completed snapshot and its generic immutable result reference."""

    completed_work_intent: WorkIntentSnapshot
    result_reference: ResourceReference

    def __post_init__(self) -> None:
        _require_exact(
            self.completed_work_intent,
            WorkIntentSnapshot,
            "completed_work_intent",
        )
        _require_exact(self.result_reference, ResourceReference, "result_reference")
        if self.completed_work_intent.status is not WorkIntentStatus.SUCCEEDED:
            raise ValueError("completed_work_intent must be SUCCEEDED")
        if self.completed_work_intent.current_lease is not None:
            raise ValueError("completed_work_intent cannot retain a Lease")


__all__ = ["WorkIntentCompletionResult"]
