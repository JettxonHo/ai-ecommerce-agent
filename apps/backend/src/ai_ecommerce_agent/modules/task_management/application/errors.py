"""Stable application errors for Task Management use cases."""

from __future__ import annotations

from collections.abc import Mapping

from ai_ecommerce_agent.shared_kernel import ProjectError, SafeContext


class TaskManagementApplicationError(ProjectError):
    """Base application-boundary error with no adapter details."""

    def __init__(
        self,
        code: str,
        context: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            "task_management.application", code, SafeContext.from_mapping(context)
        )


class TaskNotFoundError(TaskManagementApplicationError):
    """A requested Task identity is not in the fixed application scope."""

    def __init__(self, task_id: str) -> None:
        super().__init__("task_not_found", {"taskId": task_id})


class RunNotFoundError(TaskManagementApplicationError):
    """A requested Run identity is not in the fixed application scope."""

    def __init__(self, run_id: str) -> None:
        super().__init__("run_not_found", {"runId": run_id})


class StageNotFoundError(TaskManagementApplicationError):
    """A requested Task/Stage pair is not in the fixed application scope."""

    def __init__(self, task_id: str, stage: str) -> None:
        super().__init__("stage_not_found", {"taskId": task_id, "stage": stage})


__all__ = [
    "RunNotFoundError",
    "StageNotFoundError",
    "TaskManagementApplicationError",
    "TaskNotFoundError",
]
