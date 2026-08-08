"""Representative Task/Run lifecycle and identity invariants for #90."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

import pytest

from ai_ecommerce_agent.modules.task_management.domain import (
    InvalidTransitionError,
    RevisionConflictError,
    Run,
    RunStatus,
    StageReference,
    Task,
    TaskStatus,
)
from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

pytestmark = pytest.mark.unit

_T0 = datetime(2026, 8, 8, 0, 0, tzinfo=UTC)
_T1 = _T0 + timedelta(minutes=1)
_T2 = _T0 + timedelta(minutes=2)
_T3 = _T0 + timedelta(minutes=3)
_TASK_ID = TaskId("task-01")
_RUN_ID = RunId("run-01")


def _draft() -> Task:
    return Task.create(
        _TASK_ID,
        task_name="Commuter backpack launch",
        product_category="backpack",
        promotion_goal="increase qualified traffic",
        updated_at=_T0,
    )


def _queued(run_id: RunId = _RUN_ID) -> Run:
    return Run.create(run_id, _TASK_ID, updated_at=_T0)


def test_task_create_and_start_are_frozen_and_revision_guarded() -> None:
    task = _draft()
    run = _queued()
    started = task.start(run.run_id, expected_revision=task.revision, updated_at=_T1)

    assert task.task_status is TaskStatus.DRAFT
    assert started.task_status is TaskStatus.RUNNING
    assert started.active_run_id == run.run_id
    assert started.latest_run_id == run.run_id
    assert started.revision == Revision(1)
    assert started.updated_at == _T1
    with pytest.raises(FrozenInstanceError):
        started.task_status = TaskStatus.PAUSED  # type: ignore[misc]
    with pytest.raises(RevisionConflictError):
        task.start(run.run_id, expected_revision=Revision(9), updated_at=_T1)
    with pytest.raises(InvalidTransitionError):
        started.start(
            RunId("run-02"), expected_revision=started.revision, updated_at=_T2
        )


def test_task_wait_review_gate_and_active_latest_pointer_invariant() -> None:
    running = _draft().start(
        _RUN_ID, expected_revision=Revision.initial(), updated_at=_T1
    )
    with pytest.raises(InvalidTransitionError):
        running.wait_for_review(
            StageReference.PRODUCT_POSITIONING,
            "review must use the Human Review stage",
            expected_revision=running.revision,
            updated_at=_T2,
        )

    waiting = running.wait_for_review(
        StageReference.HUMAN_REVIEW,
        "approval is required",
        expected_revision=running.revision,
        updated_at=_T2,
    )
    assert waiting.task_status is TaskStatus.WAITING_FOR_REVIEW
    assert waiting.current_stage is StageReference.HUMAN_REVIEW
    assert waiting.active_run_id is None
    assert waiting.latest_run_id == _RUN_ID
    assert waiting.waiting_reason == "approval is required"


def test_task_pause_resume_uses_new_run_and_clears_wait_reason() -> None:
    running = _draft().start(
        _RUN_ID, expected_revision=Revision.initial(), updated_at=_T1
    )
    paused = running.pause(
        "provider result needs operator attention",
        expected_revision=running.revision,
        updated_at=_T2,
    )
    resumed = paused.resume(
        RunId("run-02"), expected_revision=paused.revision, updated_at=_T3
    )

    assert paused.task_status is TaskStatus.PAUSED
    assert paused.active_run_id is None
    assert paused.latest_run_id == _RUN_ID
    assert resumed.task_status is TaskStatus.RUNNING
    assert resumed.active_run_id == RunId("run-02")
    assert resumed.latest_run_id == RunId("run-02")
    assert resumed.waiting_reason is None
    with pytest.raises(ValueError):
        paused.resume(_RUN_ID, expected_revision=paused.revision, updated_at=_T3)


def test_task_terminal_paths_clear_active_pointer_but_keep_latest() -> None:
    running = _draft().start(
        _RUN_ID, expected_revision=Revision.initial(), updated_at=_T1
    )
    completed = running.complete(expected_revision=running.revision, updated_at=_T2)
    assert completed.task_status is TaskStatus.COMPLETED
    assert completed.active_run_id is None
    assert completed.latest_run_id == _RUN_ID
    with pytest.raises(InvalidTransitionError):
        completed.finalize_cancellation(
            expected_revision=completed.revision, updated_at=_T3
        )

    failed = running.fail(
        "generation failed",
        expected_revision=running.revision,
        updated_at=_T2,
    )
    with pytest.raises(InvalidTransitionError):
        failed.finalize_cancellation(expected_revision=failed.revision, updated_at=_T3)
    with pytest.raises(InvalidTransitionError):
        failed.move_to_stage(
            StageReference.PRODUCT_POSITIONING,
            expected_revision=failed.revision,
            updated_at=_T3,
        )
    cancelled = running.finalize_cancellation(
        expected_revision=running.revision, updated_at=_T3
    )
    assert cancelled.task_status is TaskStatus.CANCELLED
    assert cancelled.active_run_id is None
    assert cancelled.latest_run_id == _RUN_ID


def test_run_retry_is_a_new_identity_and_source_run_is_retained() -> None:
    source = _queued()
    retry = Run.create_retry(
        RunId("run-02"),
        _TASK_ID,
        source_run_id=source.run_id,
        updated_at=_T1,
    )
    assert source.status is RunStatus.QUEUED
    assert retry.status is RunStatus.RETRYING
    assert retry.run_id != source.run_id
    assert retry.source_run_id == source.run_id
    with pytest.raises(ValueError):
        Run.create_retry(
            source.run_id,
            _TASK_ID,
            source_run_id=source.run_id,
            updated_at=_T1,
        )


def test_run_resume_is_a_new_queued_identity_distinct_from_retry() -> None:
    source = _queued()
    resumed = Run.create_resume(
        RunId("run-resume"),
        _TASK_ID,
        source_run_id=source.run_id,
        updated_at=_T1,
    )
    assert resumed.status is RunStatus.QUEUED
    assert resumed.run_id != source.run_id
    assert resumed.source_run_id == source.run_id
    with pytest.raises(ValueError):
        Run.create_resume(
            source.run_id,
            _TASK_ID,
            source_run_id=source.run_id,
            updated_at=_T1,
        )


def test_run_start_wait_review_and_completion_do_not_model_approval() -> None:
    run = _queued().start(expected_revision=Revision.initial(), updated_at=_T1)
    with pytest.raises(InvalidTransitionError):
        run.wait_for_review(
            StageReference.PRODUCT_POSITIONING,
            expected_revision=run.revision,
            updated_at=_T2,
        )
    waiting = run.wait_for_review(
        StageReference.HUMAN_REVIEW,
        expected_revision=run.revision,
        updated_at=_T2,
    )
    assert waiting.status is RunStatus.WAITING_FOR_REVIEW
    resumed = (
        waiting  # Review approval is owned by a later module; no field is added here.
    )
    with pytest.raises(InvalidTransitionError):
        resumed.complete(
            expected_revision=resumed.revision,
            updated_at=_T3,
            completed_at=_T3,
        )

    running = _queued(RunId("run-03")).start(
        expected_revision=Revision.initial(), updated_at=_T1
    )
    completed = running.complete(
        expected_revision=running.revision,
        updated_at=_T3,
        completed_at=_T3,
    )
    assert completed.status is RunStatus.COMPLETED
    assert completed.completed_at == _T3


def test_run_cancellation_request_is_distinct_from_terminal_cancel() -> None:
    running = _queued().start(expected_revision=Revision.initial(), updated_at=_T1)
    requested = running.request_cancellation(
        expected_revision=running.revision, updated_at=_T2
    )
    assert requested.status is RunStatus.CANCELLATION_REQUESTED
    assert requested.completed_at is None
    with pytest.raises(InvalidTransitionError):
        requested.move_to_stage(
            StageReference.PRODUCT_POSITIONING,
            expected_revision=requested.revision,
            updated_at=_T3,
        )
    with pytest.raises(InvalidTransitionError):
        running.finalize_cancellation(
            expected_revision=running.revision,
            updated_at=_T3,
            completed_at=_T3,
        )
    cancelled = requested.finalize_cancellation(
        expected_revision=requested.revision,
        updated_at=_T3,
        completed_at=_T3,
    )
    assert cancelled.status is RunStatus.CANCELLED
    assert cancelled.completed_at == _T3


def test_run_supersede_is_terminal_and_cannot_rewrite_terminal_history() -> None:
    running = _queued().start(expected_revision=Revision.initial(), updated_at=_T1)
    superseded = running.supersede(
        expected_revision=running.revision,
        updated_at=_T2,
        completed_at=_T2,
    )
    assert superseded.status is RunStatus.SUPERSEDED
    assert superseded.completed_at == _T2
    with pytest.raises(InvalidTransitionError):
        superseded.supersede(
            expected_revision=superseded.revision,
            updated_at=_T3,
            completed_at=_T3,
        )


def test_run_revision_guard_and_no_runtime_identity() -> None:
    run = _queued()
    assert not hasattr(run, "thread_id")
    with pytest.raises(RevisionConflictError):
        run.start(expected_revision=Revision(2), updated_at=_T1)
    with pytest.raises(FrozenInstanceError):
        run.status = RunStatus.RUNNING  # type: ignore[misc]
