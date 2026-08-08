"""Module-internal mapping from domain entities to A1 public snapshots."""

from __future__ import annotations

from ai_ecommerce_agent.modules.task_management.domain import (
    Run,
    RunSnapshot,
    Stage,
    StageSnapshot,
    Task,
    TaskSnapshot,
)


def task_to_snapshot(task: Task) -> TaskSnapshot:
    """Project a Task without exposing its mutable domain entity."""

    return TaskSnapshot(
        task_id=task.task_id,
        task_name=task.task_name,
        product_category=task.product_category,
        promotion_goal=task.promotion_goal,
        task_status=task.task_status,
        revision=task.revision,
        current_stage=task.current_stage,
        active_run_id=task.active_run_id,
        latest_run_id=task.latest_run_id,
        waiting_reason=task.waiting_reason,
        updated_at=task.updated_at,
    )


def run_to_snapshot(run: Run) -> RunSnapshot:
    """Project a Run without leaking runtime or persistence types."""

    return RunSnapshot(
        run_id=run.run_id,
        task_id=run.task_id,
        revision=run.revision,
        source_run_id=run.source_run_id,
        status=run.status,
        current_stage=run.current_stage,
        started_at=run.started_at,
        updated_at=run.updated_at,
        completed_at=run.completed_at,
        failure_summary=run.failure_summary,
        last_valid_result=run.last_valid_result,
    )


def stage_to_snapshot(stage: Stage) -> StageSnapshot:
    """Project a Stage Current Truth record into its immutable DTO."""

    return StageSnapshot(
        task_id=stage.task_id,
        stage=stage.stage,
        status=stage.status,
        revision=stage.revision,
        current_version=stage.current_version,
        last_valid_version=stage.last_valid_version,
        last_run_id=stage.last_run_id,
        waiting_reason=stage.waiting_reason,
        updated_at=stage.updated_at,
    )


__all__ = ["run_to_snapshot", "stage_to_snapshot", "task_to_snapshot"]
