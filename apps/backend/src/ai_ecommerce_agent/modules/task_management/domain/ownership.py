"""Task/Run/Stage ownership and pointer invariants.

The entities remain separate resources; these small checks let an application
command coordinate them without turning ``Task`` into an aggregate containing
Run or Stage objects.
"""

from __future__ import annotations

from ai_ecommerce_agent.shared_kernel import TaskId

from .errors import OwnershipError
from .snapshots import Run, Stage, Task


def require_task_owns_run(task_id: TaskId, run: Run) -> None:
    """Reject a Run whose immutable owner differs from the command Task."""

    if run.task_id != task_id:
        raise OwnershipError(
            {
                "resource": "run",
                "taskId": str(task_id),
                "runTaskId": str(run.task_id),
                "runId": str(run.run_id),
            }
        )


def require_task_owns_stage(task_id: TaskId, stage: Stage) -> None:
    """Reject a Stage row that belongs to another Task."""

    if stage.task_id != task_id:
        raise OwnershipError(
            {
                "resource": "stage",
                "taskId": str(task_id),
                "stageTaskId": str(stage.task_id),
                "stage": stage.stage.value,
            }
        )


def require_task_current_run(task: Task, run: Run) -> None:
    """Require a Run to match both its Task owner and Task current pointer."""

    require_task_owns_run(task.task_id, run)
    if task.current_run_id != run.run_id:
        raise OwnershipError(
            {
                "resource": "task.current_run",
                "taskId": str(task.task_id),
                "currentRunId": str(task.current_run_id)
                if task.current_run_id is not None
                else "none",
                "runId": str(run.run_id),
            }
        )


def require_stage_run(stage: Stage, run: Run) -> None:
    """Require a Run to match a Stage owner and its last-run pointer."""

    require_task_owns_run(stage.task_id, run)
    if stage.last_run_id != run.run_id:
        raise OwnershipError(
            {
                "resource": "stage.last_run",
                "taskId": str(stage.task_id),
                "stage": stage.stage.value,
                "lastRunId": str(stage.last_run_id)
                if stage.last_run_id is not None
                else "none",
                "runId": str(run.run_id),
            }
        )


__all__ = [
    "require_stage_run",
    "require_task_current_run",
    "require_task_owns_run",
    "require_task_owns_stage",
]
