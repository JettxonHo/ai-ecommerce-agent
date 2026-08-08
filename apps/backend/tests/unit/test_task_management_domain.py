"""Focused A1 catalog and immutable snapshot tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ai_ecommerce_agent.modules.task_management.domain import (
    DomainVersionReference,
    RunSnapshot,
    RunStatus,
    StageReference,
    StageSnapshot,
    StageStatus,
    TaskSnapshot,
    TaskStatus,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    Revision,
    RunId,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def test_accepted_state_and_stage_catalogs_are_exact() -> None:
    assert [status.value for status in TaskStatus] == (
        "draft running waiting_for_input waiting_for_review paused completed "
        "failed cancelled"
    ).split()
    assert [status.value for status in RunStatus] == (
        "queued running retrying waiting_for_input waiting_for_review paused "
        "cancellation_requested completed failed cancelled superseded"
    ).split()
    assert [status.value for status in StageStatus] == (
        "not_started ready running waiting_input waiting_review valid invalid "
        "failed skipped"
    ).split()
    assert [stage.value for stage in StageReference] == (
        "product_intake_and_fact_extraction customer_insight_analysis "
        "product_positioning human_review marketing_brief_generation "
        "xiaohongshu_brief_mapping"
    ).split()


def test_domain_version_reference_is_frozen_and_keeps_id_number_distinct() -> None:
    reference = DomainVersionReference(
        DomainVersionId("version-01"), VersionNumber.initial()
    )
    assert reference.version_id == DomainVersionId("version-01")
    assert reference.version_number == VersionNumber(1)
    with pytest.raises(FrozenInstanceError):
        reference.version_number = VersionNumber(2)  # type: ignore[misc]


def test_task_snapshot_is_frozen_and_keeps_active_and_latest_run_pointers() -> None:
    snapshot = TaskSnapshot(
        task_id=TaskId("task-01"),
        task_name="Commuter backpack launch",
        product_category="backpack",
        promotion_goal="increase qualified traffic",
        status=TaskStatus.WAITING_FOR_INPUT,
        revision=Revision(3),
        current_stage=StageReference.PRODUCT_POSITIONING,
        current_run_id=None,
        latest_run_id=RunId("run-01"),
        waiting_reason="positioning source is missing",
        updated_at=None,
    )
    assert snapshot.task_status is TaskStatus.WAITING_FOR_INPUT
    assert snapshot.current_run_id is None
    assert snapshot.latest_run_id == RunId("run-01")
    with pytest.raises(FrozenInstanceError):
        snapshot.status = TaskStatus.RUNNING  # type: ignore[misc]


def test_run_snapshot_contains_nullable_last_valid_result_without_thread_identity() -> (
    None
):
    snapshot = RunSnapshot(
        run_id=RunId("run-01"),
        task_id=TaskId("task-01"),
        revision=Revision.initial(),
        source_run_id=None,
        status=RunStatus.QUEUED,
        current_stage=StageReference.PRODUCT_INTAKE_AND_FACT_EXTRACTION,
        started_at=None,
        updated_at=None,
        completed_at=None,
        failure_summary=None,
        last_valid_result=None,
    )
    assert snapshot.last_valid_result is None
    assert not hasattr(snapshot, "thread_id")
    with pytest.raises(FrozenInstanceError):
        snapshot.status = RunStatus.RUNNING  # type: ignore[misc]


def test_stage_snapshot_is_frozen_task_scoped_and_data_only() -> None:
    snapshot = StageSnapshot(
        task_id=TaskId("task-01"),
        stage=StageReference.HUMAN_REVIEW,
        status=StageStatus.WAITING_REVIEW,
        revision=Revision(2),
        current_version=None,
        last_valid_version=None,
        last_run_id=RunId("run-01"),
        waiting_reason="approval is required",
        updated_at=None,
    )
    assert snapshot.task_id == TaskId("task-01")
    assert snapshot.stage is StageReference.HUMAN_REVIEW
    assert snapshot.waiting_reason == "approval is required"
    with pytest.raises(FrozenInstanceError):
        snapshot.stage = StageReference.PRODUCT_POSITIONING  # type: ignore[misc]
