"""Representative Task/Run/Stage domain invariants for MVP0-009A."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ai_ecommerce_agent.modules.task_management.domain import (
    DomainVersionReference,
    InvalidTransitionError,
    OwnershipError,
    RevisionConflictError,
    Run,
    RunStatus,
    Stage,
    StageReference,
    StageStatus,
    Task,
    TaskStatus,
    require_stage_run,
    require_task_current_run,
    require_task_owns_run,
    require_task_owns_stage,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    Revision,
    RunId,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def _task(task_id: str = "task-01") -> Task:
    return Task.create(
        TaskId(task_id),
        task_name="Commuter backpack launch",
        product_category="backpack",
        promotion_goal="increase qualified traffic",
    )


def test_accepted_catalogs_are_exact() -> None:
    assert [status.value for status in TaskStatus] == [
        "draft",
        "running",
        "waiting_for_input",
        "waiting_for_review",
        "paused",
        "completed",
        "failed",
        "cancelled",
    ]
    assert [status.value for status in RunStatus] == [
        "queued",
        "running",
        "retrying",
        "waiting_for_input",
        "waiting_for_review",
        "paused",
        "cancellation_requested",
        "completed",
        "failed",
        "cancelled",
        "superseded",
    ]
    assert [status.value for status in StageStatus] == [
        "not_started",
        "ready",
        "running",
        "waiting_input",
        "waiting_review",
        "valid",
        "invalid",
        "failed",
        "skipped",
    ]
    assert [stage.value for stage in StageReference] == [
        "product_intake_and_fact_extraction",
        "customer_insight_analysis",
        "product_positioning",
        "human_review",
        "marketing_brief_generation",
        "xiaohongshu_brief_mapping",
    ]


def test_task_start_wait_resume_and_revision_guard_are_immutable() -> None:
    task = _task()
    run_id = RunId("run-01")

    running = task.start(run_id, expected_revision=task.revision)
    assert task.status is TaskStatus.DRAFT
    assert running.status is TaskStatus.RUNNING
    assert running.current_run_id == run_id
    assert running.latest_run_id == run_id
    assert running.revision == Revision(1)

    paused = running.pause(
        "manual recovery requested", expected_revision=running.revision
    )
    assert paused.status is TaskStatus.PAUSED
    assert paused.waiting_reason == "manual recovery requested"
    assert paused.current_run_id is None

    waiting = running.wait_for_input(
        StageReference.PRODUCT_POSITIONING,
        "positioning source is missing",
        expected_revision=running.revision,
    )
    assert waiting.status is TaskStatus.WAITING_FOR_INPUT
    assert waiting.waiting_reason == "positioning source is missing"
    assert waiting.current_run_id is None

    resumed = waiting.resume(RunId("run-02"), expected_revision=waiting.revision)
    assert resumed.status is TaskStatus.RUNNING
    assert resumed.waiting_reason is None
    assert resumed.current_run_id == RunId("run-02")

    with pytest.raises(RevisionConflictError) as caught:
        resumed.complete(expected_revision=Revision(99))
    assert caught.value.code == "revision_conflict"
    assert caught.value.safe_context["resource"] == "task"


def test_task_review_gate_and_terminal_transition_are_narrow() -> None:
    running = _task().start(RunId("run-01"), expected_revision=Revision.initial())

    with pytest.raises(InvalidTransitionError):
        running.wait_for_review(
            StageReference.PRODUCT_POSITIONING,
            "review is required",
            expected_revision=running.revision,
        )

    waiting = running.wait_for_review(
        StageReference.HUMAN_REVIEW,
        "approval is required",
        expected_revision=running.revision,
    )
    assert waiting.status is TaskStatus.WAITING_FOR_REVIEW
    assert waiting.current_stage is StageReference.HUMAN_REVIEW
    assert waiting.waiting_reason == "approval is required"

    resumed = waiting.resume(RunId("run-02"), expected_revision=waiting.revision)
    completed = resumed.complete(expected_revision=resumed.revision)
    assert completed.current_run_id is None
    assert completed.waiting_reason is None
    with pytest.raises(InvalidTransitionError):
        completed.cancel(expected_revision=completed.revision)


def test_run_recovery_and_cooperative_cancellation_are_explicit() -> None:
    run = Run.create(RunId("run-01"), TaskId("task-01"))
    started = run.start(expected_revision=run.revision)

    with pytest.raises(InvalidTransitionError):
        started.wait_for_review(
            StageReference.PRODUCT_POSITIONING,
            expected_revision=started.revision,
        )

    waiting = started.wait_for_review(
        StageReference.HUMAN_REVIEW,
        expected_revision=started.revision,
    )
    requested = waiting.request_cancellation(expected_revision=waiting.revision)
    assert requested.status is RunStatus.CANCELLATION_REQUESTED
    cancelled = requested.cancel(expected_revision=requested.revision)
    assert cancelled.status is RunStatus.CANCELLED

    failed = started.fail("provider timed out", expected_revision=started.revision)
    retry = Run.create_retry(
        RunId("run-02"),
        TaskId("task-01"),
        source_run_id=failed.run_id,
        current_stage=StageReference.HUMAN_REVIEW,
    )
    assert retry.run_id != failed.run_id
    assert retry.source_run_id == failed.run_id
    assert retry.status is RunStatus.RETRYING
    with pytest.raises(ValueError):
        Run.create_retry(
            failed.run_id,
            failed.task_id,
            source_run_id=failed.run_id,
        )

    with pytest.raises(InvalidTransitionError):
        cancelled.cancel(expected_revision=cancelled.revision)


def test_stage_revalidation_keeps_last_valid_version() -> None:
    stage = Stage.create(TaskId("task-01"), StageReference.PRODUCT_POSITIONING)
    version = DomainVersionReference(
        DomainVersionId("version-01"), VersionNumber.initial()
    )
    started = stage.prepare(expected_revision=stage.revision).start(
        RunId("run-01"), expected_revision=Revision(1)
    )
    valid = started.mark_valid(version, expected_revision=started.revision)
    invalid = valid.invalidate(expected_revision=valid.revision)
    assert invalid.status is StageStatus.INVALID
    assert invalid.current_version is None
    assert invalid.last_valid_version == version

    rerun = invalid.prepare_rerun(expected_revision=invalid.revision)
    assert rerun.status is StageStatus.READY
    restarted = rerun.start(RunId("run-02"), expected_revision=rerun.revision)
    assert restarted.status is StageStatus.RUNNING
    assert restarted.last_valid_version == version


def test_stage_review_gate_and_ownership_pointers_are_enforced() -> None:
    task_id = TaskId("task-01")
    run = Run.create(RunId("run-01"), task_id)
    stage = Stage.create(task_id, StageReference.HUMAN_REVIEW).prepare(
        expected_revision=Revision.initial()
    )
    stage_running = stage.start(run.run_id, expected_revision=stage.revision)
    waiting = stage_running.wait_for_review(
        "approval is required", expected_revision=stage_running.revision
    )
    assert waiting.status is StageStatus.WAITING_REVIEW
    assert waiting.waiting_reason == "approval is required"

    task = _task().start(run.run_id, expected_revision=Revision.initial())
    require_task_owns_run(task.task_id, run)
    require_task_current_run(task, run)
    require_stage_run(stage_running, run)
    require_task_owns_stage(task_id, stage_running)

    other_task = TaskId("task-02")
    other_run = Run.create(RunId("run-02"), other_task)
    with pytest.raises(OwnershipError):
        require_task_owns_run(task_id, other_run)
    with pytest.raises(OwnershipError):
        require_task_owns_stage(task_id, Stage.create(other_task, stage_running.stage))
    with pytest.raises(OwnershipError):
        require_task_current_run(task, Run.create(RunId("run-03"), task_id))


def test_public_snapshots_are_frozen_data_only_contracts() -> None:
    from ai_ecommerce_agent.modules.task_management.domain import (
        RunSnapshot,
        StageSnapshot,
        TaskSnapshot,
    )

    task_snapshot = TaskSnapshot(
        task_id=TaskId("task-01"),
        task_name="Commuter backpack launch",
        product_category="backpack",
        promotion_goal="increase qualified traffic",
        status=TaskStatus.RUNNING,
        revision=Revision(1),
        current_stage=StageReference.PRODUCT_POSITIONING,
        current_run_id=RunId("run-01"),
        latest_run_id=RunId("run-01"),
        waiting_reason=None,
        updated_at=None,
    )
    assert task_snapshot.task_status is TaskStatus.RUNNING
    with pytest.raises(FrozenInstanceError):
        task_snapshot.status = TaskStatus.COMPLETED  # type: ignore[misc]

    run_snapshot = RunSnapshot(
        run_id=RunId("run-01"),
        task_id=TaskId("task-01"),
        revision=Revision.initial(),
        source_run_id=None,
        status=RunStatus.QUEUED,
        current_stage=None,
        started_at=None,
        updated_at=None,
        completed_at=None,
        failure_summary=None,
        last_valid_result=None,
    )
    stage_snapshot = StageSnapshot(
        task_id=TaskId("task-01"),
        stage=StageReference.PRODUCT_POSITIONING,
        status=StageStatus.NOT_STARTED,
        revision=Revision.initial(),
        current_version=None,
        last_valid_version=None,
        last_run_id=None,
        waiting_reason=None,
        updated_at=None,
    )
    assert run_snapshot.last_valid_result is None
    assert stage_snapshot.waiting_reason is None
    assert not hasattr(task_snapshot, "start")
    assert not hasattr(run_snapshot, "start")
    assert not hasattr(stage_snapshot, "start")
