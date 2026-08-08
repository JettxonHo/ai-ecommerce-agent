from __future__ import annotations

import pytest

from ts03_checkpoint.business_probe import BusinessTruthProbe
from ts03_checkpoint.compatibility import (
    CHECKPOINT_STORE_SCHEMA_VERSION,
    CHECKPOINTER_PACKAGE_VERSION,
)
from ts03_checkpoint.config import checkpoint_connection
from ts03_checkpoint.reconciliation import (
    CheckpointMetadata,
    CompatibilityTuple,
    CurrentTruth,
    RecoveryRequest,
    classify_recovery,
)

TUPLE = CompatibilityTuple(
    workflow_definition_version="ts03-workflow-v1",
    graph_state_schema_version="ts03-state-v1",
    serializer_profile_version="langgraph-default-v1",
    checkpointer_package_version=CHECKPOINTER_PACKAGE_VERSION,
    store_schema_version=CHECKPOINT_STORE_SCHEMA_VERSION,
)


def checkpoint(**overrides: object) -> CheckpointMetadata:
    values: dict[str, object] = {
        "task_id": "task-a",
        "thread_id": "thread-a",
        "input_version": "input-v1",
        "source_set_version": "sources-v1",
        "stage": "review",
        "review_package_version": "review-v1",
        "compatibility": TUPLE,
    }
    values.update(overrides)
    return CheckpointMetadata(**values)  # type: ignore[arg-type]


def current(**overrides: object) -> CurrentTruth:
    values: dict[str, object] = {
        "task_id": "task-a",
        "thread_id": "thread-a",
        "input_version": "input-v1",
        "source_set_version": "sources-v1",
        "valid_stage": "review",
        "review_package_version": "review-v1",
        "compatibility": TUPLE,
    }
    values.update(overrides)
    return CurrentTruth(**values)  # type: ignore[arg-type]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("name", "checkpoint_value", "current_value", "recovery_request", "expected"),
    [
        (
            "resume_same_thread",
            checkpoint(),
            current(),
            RecoveryRequest(task_id="task-a", thread_id="thread-a"),
            ("resume_same_thread", True),
        ),
        (
            "reconcile_committed_result",
            checkpoint(),
            current(committed_idempotency_key="commit-1"),
            RecoveryRequest(
                task_id="task-a",
                thread_id="thread-a",
                outcome_unknown=True,
                idempotency_key="commit-1",
            ),
            ("reconcile_committed_result", False),
        ),
        (
            "retry_current_stage",
            checkpoint(),
            current(),
            RecoveryRequest(task_id="task-a", thread_id="thread-a", transient_failure=True),
            ("retry_current_stage", False),
        ),
        (
            "rerun_from_earliest_invalid_stage",
            checkpoint(),
            current(input_version="input-v2"),
            RecoveryRequest(task_id="task-a", thread_id="thread-a"),
            ("rerun_from_earliest_invalid_stage", False),
        ),
        (
            "rerun_from_stale_stage",
            checkpoint(),
            current(valid_stage="fact"),
            RecoveryRequest(task_id="task-a", thread_id="thread-a"),
            ("rerun_from_earliest_invalid_stage", False),
        ),
        (
            "restart_from_safe_boundary",
            None,
            current(safe_boundary="fact"),
            RecoveryRequest(task_id="task-a", thread_id="thread-a", requested_action="restart"),
            ("restart_from_safe_boundary", False),
        ),
        (
            "manual_recovery_required",
            checkpoint(
                compatibility=CompatibilityTuple(
                    workflow_definition_version="ts03-workflow-v0",
                    graph_state_schema_version="ts03-state-v0",
                    serializer_profile_version="langgraph-default-v0",
                    checkpointer_package_version="langgraph-checkpoint-postgres-3.0.0",
                    store_schema_version="checkpoint_migrations_v8",
                )
            ),
            current(),
            RecoveryRequest(task_id="task-a", thread_id="thread-a"),
            ("manual_recovery_required", False),
        ),
        (
            "reject_request",
            checkpoint(task_id="task-b", thread_id="thread-b"),
            current(),
            RecoveryRequest(task_id="task-a", thread_id="thread-a"),
            ("reject_request", False),
        ),
    ],
)
def test_each_accepted_action_has_one_representative_path(
    name: str,
    checkpoint_value: CheckpointMetadata | None,
    current_value: CurrentTruth,
    recovery_request: RecoveryRequest,
    expected: tuple[str, bool],
) -> None:
    decision = classify_recovery(checkpoint_value, current_value, recovery_request)
    assert decision.action == expected[0], name
    assert decision.checkpoint_reusable is expected[1], name


@pytest.mark.unit
def test_foreign_checkpoint_rejected_without_business_truth_pollution() -> None:
    probe = BusinessTruthProbe()
    before = probe.snapshot()
    decision = classify_recovery(
        checkpoint(task_id="task-foreign", thread_id="thread-foreign"),
        current(),
        RecoveryRequest(task_id="task-a", thread_id="thread-a"),
    )
    assert decision.action == "reject_request"
    assert decision.checkpoint_reusable is False
    assert probe.snapshot() == before


@pytest.mark.unit
def test_stale_review_and_incompatible_tuple_never_reuse_checkpoint() -> None:
    stale_review = classify_recovery(
        checkpoint(),
        current(review_package_version="review-v2"),
        RecoveryRequest(task_id="task-a", thread_id="thread-a"),
    )
    incompatible = classify_recovery(
        checkpoint(),
        current(
            compatibility=CompatibilityTuple(
                workflow_definition_version="ts03-workflow-v2",
                graph_state_schema_version="ts03-state-v2",
                serializer_profile_version="langgraph-default-v2",
                checkpointer_package_version=CHECKPOINTER_PACKAGE_VERSION,
                store_schema_version=CHECKPOINT_STORE_SCHEMA_VERSION,
            )
        ),
        RecoveryRequest(task_id="task-a", thread_id="thread-a"),
    )
    assert (stale_review.action, stale_review.checkpoint_reusable) == ("reject_request", False)
    assert (incompatible.action, incompatible.checkpoint_reusable) == (
        "manual_recovery_required",
        False,
    )


@pytest.mark.unit
def test_connection_repr_does_not_expose_password() -> None:
    rendered = repr(checkpoint_connection())
    assert "mvp0_checkpoint_local_only" not in rendered
    assert "postgresql://" not in rendered


@pytest.mark.unit
def test_unknown_outcome_without_matching_idempotency_evidence_requires_manual_recovery() -> None:
    decision = classify_recovery(
        checkpoint(),
        current(),
        RecoveryRequest(
            task_id="task-a",
            thread_id="thread-a",
            outcome_unknown=True,
        ),
    )
    assert decision.action == "manual_recovery_required"
    assert decision.checkpoint_reusable is False
