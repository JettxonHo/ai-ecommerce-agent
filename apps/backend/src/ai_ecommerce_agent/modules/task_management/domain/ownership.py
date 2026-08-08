"""Small ownership and pointer checks for Task Management coordination."""

from __future__ import annotations

from ai_ecommerce_agent.shared_kernel import TaskId

from .errors import OwnershipError
from .run import Run
from .stage import Stage
from .task import Task


def require_task_owns_run(task_id: TaskId, run: Run) -> None:
    """Reject a Run whose immutable Task owner differs from the command Task."""

    if run.task_id != task_id:
        raise OwnershipError(
            resource="run",
            context={
                "task_id": str(task_id),
                "run_task_id": str(run.task_id),
                "run_id": str(run.run_id),
            },
        )


def require_task_owns_stage(task_id: TaskId, stage: Stage) -> None:
    """Reject a Stage record that belongs to another Task."""

    if stage.task_id != task_id:
        raise OwnershipError(
            resource="stage",
            context={
                "task_id": str(task_id),
                "stage_task_id": str(stage.task_id),
                "stage": stage.stage.value,
            },
        )


def require_task_current_run(task: Task, run: Run) -> None:
    """Require Run ownership and the Task's active Run pointer to agree."""

    require_task_owns_run(task.task_id, run)
    if task.active_run_id != run.run_id:
        raise OwnershipError(
            resource="task.active_run",
            context={
                "task_id": str(task.task_id),
                "active_run_id": str(task.active_run_id)
                if task.active_run_id is not None
                else "none",
                "run_id": str(run.run_id),
            },
        )


def require_stage_run(stage: Stage, run: Run) -> None:
    """Require Run ownership and the Stage's last-Run pointer to agree."""

    require_task_owns_run(stage.task_id, run)
    if stage.last_run_id != run.run_id:
        raise OwnershipError(
            resource="stage.last_run",
            context={
                "task_id": str(stage.task_id),
                "stage": stage.stage.value,
                "last_run_id": str(stage.last_run_id)
                if stage.last_run_id is not None
                else "none",
                "run_id": str(run.run_id),
            },
        )


__all__ = [
    "require_stage_run",
    "require_task_current_run",
    "require_task_owns_run",
    "require_task_owns_stage",
]
