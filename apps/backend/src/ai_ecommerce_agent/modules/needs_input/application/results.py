"""Immutable Needs Input command results."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import TaskId

from ..domain.snapshots import NeedsInputActionRequestSnapshot


@dataclass(frozen=True, slots=True)
class ResolveNeedsInputResult:
    """Resolved request plus the narrow owning Task reference."""

    action_request: NeedsInputActionRequestSnapshot
    task_id: TaskId
    replayed: bool = False

    def __post_init__(self) -> None:
        if self.action_request.task_id != self.task_id:
            raise ValueError("result Task owner must match the request owner")


__all__ = ["ResolveNeedsInputResult"]
