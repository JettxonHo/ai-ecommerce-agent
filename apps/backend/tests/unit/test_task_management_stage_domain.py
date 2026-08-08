"""Representative Task-scoped Stage Current Truth invariants for #91."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

import pytest

from ai_ecommerce_agent.modules.task_management.domain import (
    DomainVersionReference,
    InvalidTransitionError,
    RevisionConflictError,
    Stage,
    StageReference,
    StageStatus,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    Revision,
    RunId,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit

_T0 = datetime(2026, 8, 8, 0, 0, tzinfo=UTC)
_T1 = _T0 + timedelta(minutes=1)
_T2 = _T0 + timedelta(minutes=2)
_T3 = _T0 + timedelta(minutes=3)
_TASK_ID = TaskId("task-01")
_RUN_ID = RunId("run-01")


def _stage(stage: StageReference = StageReference.PRODUCT_POSITIONING) -> Stage:
    return Stage.create(_TASK_ID, stage, updated_at=_T0)


def _running(
    stage: StageReference = StageReference.PRODUCT_POSITIONING,
    run_id: RunId = _RUN_ID,
) -> Stage:
    created = _stage(stage)
    ready = created.prepare(expected_revision=created.revision, updated_at=_T1)
    return ready.start(run_id, expected_revision=ready.revision, updated_at=_T2)


def _version(value: str = "version-01") -> DomainVersionReference:
    return DomainVersionReference(DomainVersionId(value), VersionNumber(1))


def test_stage_create_prepare_start_is_frozen_and_revision_guarded() -> None:
    created = _stage()
    ready = created.prepare(expected_revision=created.revision, updated_at=_T1)
    running = ready.start(_RUN_ID, expected_revision=ready.revision, updated_at=_T2)

    assert created.status is StageStatus.NOT_STARTED
    assert ready.status is StageStatus.READY
    assert running.status is StageStatus.RUNNING
    assert running.last_run_id == _RUN_ID
    assert running.revision == Revision(2)
    with pytest.raises(FrozenInstanceError):
        running.status = StageStatus.VALID  # type: ignore[misc]
    with pytest.raises(RevisionConflictError):
        created.prepare(expected_revision=Revision(9), updated_at=_T1)
    with pytest.raises(InvalidTransitionError):
        created.start(_RUN_ID, expected_revision=created.revision, updated_at=_T1)


def test_stage_wait_input_resume_and_rerun_require_new_run_identity() -> None:
    waiting = _running().wait_for_input(
        "positioning source is missing",
        expected_revision=Revision(2),
        updated_at=_T3,
    )
    resumed = waiting.resume(
        RunId("run-02"), expected_revision=waiting.revision, updated_at=_T3
    )
    assert waiting.status is StageStatus.WAITING_INPUT
    assert waiting.current_version is None
    assert waiting.waiting_reason == "positioning source is missing"
    assert resumed.status is StageStatus.RUNNING
    assert resumed.last_run_id == RunId("run-02")
    assert resumed.waiting_reason is None

    failed = resumed.mark_failed(
        "generation failed", expected_revision=resumed.revision, updated_at=_T3
    )
    ready = failed.prepare_rerun(expected_revision=failed.revision, updated_at=_T3)
    assert ready.status is StageStatus.READY
    with pytest.raises(ValueError):
        ready.start(RunId("run-02"), expected_revision=ready.revision, updated_at=_T3)


def test_human_review_wait_can_be_validated_but_other_stage_cannot_wait_review() -> (
    None
):
    human_review = _running(StageReference.HUMAN_REVIEW)
    waiting = human_review.wait_for_review(
        "approval is required",
        expected_revision=human_review.revision,
        updated_at=_T3,
    )
    valid = waiting.mark_valid(
        _version(), expected_revision=waiting.revision, updated_at=_T3
    )
    assert waiting.status is StageStatus.WAITING_REVIEW
    assert valid.status is StageStatus.VALID
    assert valid.current_version == valid.last_valid_version == _version()
    assert valid.waiting_reason is None

    with pytest.raises(InvalidTransitionError):
        _running().wait_for_review(
            "approval is required",
            expected_revision=Revision(2),
            updated_at=_T3,
        )
    with pytest.raises(InvalidTransitionError):
        waiting.resume(
            RunId("run-02"), expected_revision=waiting.revision, updated_at=_T3
        )


def test_invalidate_preserves_last_valid_history_and_clears_current_truth() -> None:
    valid = _running().mark_valid(
        _version(), expected_revision=Revision(2), updated_at=_T3
    )
    invalid = valid.invalidate(expected_revision=valid.revision, updated_at=_T3)

    assert valid.current_version == valid.last_valid_version
    assert invalid.status is StageStatus.INVALID
    assert invalid.current_version is None
    assert invalid.last_valid_version == valid.last_valid_version


def test_skip_is_only_a_pre_execution_intent() -> None:
    skipped = _stage().skip(expected_revision=Revision.initial(), updated_at=_T1)
    assert skipped.status is StageStatus.SKIPPED
    with pytest.raises(InvalidTransitionError):
        _running().skip(expected_revision=Revision(2), updated_at=_T3)
