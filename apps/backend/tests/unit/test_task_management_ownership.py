"""Representative Task/Run/Stage ownership invariants for #91."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ai_ecommerce_agent.modules.task_management.domain import (
    OwnershipError,
    Run,
    Stage,
    StageReference,
    Task,
    require_stage_run,
    require_task_current_run,
    require_task_owns_run,
    require_task_owns_stage,
)
from ai_ecommerce_agent.shared_kernel import RunId, TaskId

pytestmark = pytest.mark.unit

_UPDATED_AT = datetime(2026, 8, 8, 0, 0, tzinfo=UTC)
_TASK_ID = TaskId("task-01")
_OTHER_TASK_ID = TaskId("task-02")
_RUN_ID = RunId("run-01")


def _task(task_id: TaskId = _TASK_ID) -> Task:
    return Task.create(
        task_id,
        task_name="Commuter backpack launch",
        product_category="backpack",
        promotion_goal="increase qualified traffic",
        updated_at=_UPDATED_AT,
    )


def test_ownership_helpers_reject_foreign_records_and_stale_pointers() -> None:
    run = Run.create(_RUN_ID, _TASK_ID, updated_at=_UPDATED_AT)
    task = _task().start(
        _RUN_ID, expected_revision=_task().revision, updated_at=_UPDATED_AT
    )
    stage = Stage.create(
        _TASK_ID,
        StageReference.PRODUCT_POSITIONING,
        updated_at=_UPDATED_AT,
    )
    stage = stage.prepare(expected_revision=stage.revision, updated_at=_UPDATED_AT)
    stage = stage.start(
        _RUN_ID, expected_revision=stage.revision, updated_at=_UPDATED_AT
    )

    require_task_owns_run(_TASK_ID, run)
    require_task_owns_stage(_TASK_ID, stage)
    require_task_current_run(task, run)
    require_stage_run(stage, run)

    with pytest.raises(OwnershipError):
        require_task_owns_run(_OTHER_TASK_ID, run)
    with pytest.raises(OwnershipError):
        require_task_owns_stage(_OTHER_TASK_ID, stage)
    with pytest.raises(OwnershipError):
        require_task_current_run(
            task, Run.create(RunId("run-02"), _TASK_ID, updated_at=_UPDATED_AT)
        )
    with pytest.raises(OwnershipError):
        require_stage_run(
            stage,
            Run.create(RunId("run-02"), _TASK_ID, updated_at=_UPDATED_AT),
        )
