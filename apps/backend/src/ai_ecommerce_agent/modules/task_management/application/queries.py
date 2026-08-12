"""Immutable read-only application queries for Task Management."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.modules.task_management.domain import StageReference
from ai_ecommerce_agent.shared_kernel import RunId, TaskId


@dataclass(frozen=True, slots=True)
class GetTask:
    """Read one Task navigation snapshot."""

    task_id: TaskId


@dataclass(frozen=True, slots=True)
class GetRun:
    """Read one Run monitor snapshot."""

    run_id: RunId


@dataclass(frozen=True, slots=True)
class GetStage:
    """Read one Task-scoped Stage snapshot."""

    task_id: TaskId
    stage: StageReference


@dataclass(frozen=True, slots=True)
class ListTasks:
    """Read a bounded recent Task window."""

    limit: int = 20

    def __post_init__(self) -> None:
        if isinstance(self.limit, bool) or not 1 <= self.limit <= 50:
            raise ValueError("Task list limit must be between 1 and 50")


__all__ = [
    "GetRun",
    "GetStage",
    "GetTask",
    "ListTasks",
]
