"""A tiny, deterministic Current-Truth-first decision classifier.

This module is intentionally a test-only evidence seam, not a production
recovery framework.  It models only the fields needed to demonstrate the
accepted seven-action boundary from DEC-051.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RecoveryAction = Literal[
    "resume_same_thread",
    "reconcile_committed_result",
    "retry_current_stage",
    "rerun_from_earliest_invalid_stage",
    "restart_from_safe_boundary",
    "manual_recovery_required",
    "reject_request",
]


@dataclass(frozen=True, slots=True)
class CompatibilityTuple:
    workflow_definition_version: str
    graph_state_schema_version: str
    serializer_profile_version: str
    checkpointer_package_version: str
    store_schema_version: str


@dataclass(frozen=True, slots=True)
class CheckpointMetadata:
    task_id: str
    thread_id: str
    input_version: str
    source_set_version: str
    stage: str
    review_package_version: str | None
    compatibility: CompatibilityTuple


@dataclass(frozen=True, slots=True)
class CurrentTruth:
    task_id: str
    thread_id: str
    input_version: str
    source_set_version: str
    valid_stage: str
    review_package_version: str | None
    compatibility: CompatibilityTuple
    cancelled: bool = False
    safe_boundary: str | None = None
    committed_idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class RecoveryRequest:
    task_id: str
    thread_id: str
    requested_action: Literal["resume", "retry", "rerun", "restart"] = "resume"
    transient_failure: bool = False
    outcome_unknown: bool = False
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    action: RecoveryAction
    reason: str
    checkpoint_reusable: bool


def classify_recovery(
    checkpoint: CheckpointMetadata | None,
    current: CurrentTruth,
    request: RecoveryRequest,
) -> RecoveryDecision:
    """Classify a request before any graph invocation or business write.

    ``checkpoint_reusable`` is the key boundary: only an exact-compatible,
    current checkpoint may reach LangGraph resume.  A rerun/restart decision
    may still be actionable, but it never resumes the stale checkpoint.
    """

    if request.task_id != current.task_id or request.thread_id != current.thread_id:
        return RecoveryDecision(
            "reject_request", "request does not match Current Truth identity", False
        )
    if current.cancelled:
        return RecoveryDecision("reject_request", "task is cancelled or superseded", False)
    if request.outcome_unknown and current.committed_idempotency_key == request.idempotency_key:
        return RecoveryDecision(
            "reconcile_committed_result",
            "Current Truth already proves the requested idempotent commit",
            False,
        )
    if checkpoint is None:
        if current.safe_boundary is not None:
            return RecoveryDecision(
                "restart_from_safe_boundary",
                f"checkpoint absent; safe boundary is {current.safe_boundary}",
                False,
            )
        return RecoveryDecision(
            "manual_recovery_required", "checkpoint absent with no safe boundary", False
        )
    if checkpoint.task_id != current.task_id or checkpoint.thread_id != current.thread_id:
        return RecoveryDecision(
            "reject_request", "checkpoint belongs to another task or thread", False
        )
    if checkpoint.compatibility != current.compatibility:
        return RecoveryDecision(
            "manual_recovery_required",
            "workflow/state/serializer/checkpointer/store tuple is incompatible",
            False,
        )
    if current.review_package_version != checkpoint.review_package_version:
        return RecoveryDecision("reject_request", "review package is stale or superseded", False)
    if (
        checkpoint.input_version != current.input_version
        or checkpoint.source_set_version != current.source_set_version
        or checkpoint.stage != current.valid_stage
    ):
        return RecoveryDecision(
            "rerun_from_earliest_invalid_stage",
            "checkpoint input, source set, or stage validity is stale",
            False,
        )
    if request.transient_failure or request.requested_action == "retry":
        return RecoveryDecision(
            "retry_current_stage",
            "transient failure with unchanged Current Truth",
            False,
        )
    if request.requested_action == "rerun":
        return RecoveryDecision(
            "rerun_from_earliest_invalid_stage",
            "caller requested a new business computation",
            False,
        )
    if request.requested_action == "restart":
        if current.safe_boundary is not None:
            return RecoveryDecision(
                "restart_from_safe_boundary",
                f"caller requested restart at {current.safe_boundary}",
                False,
            )
        return RecoveryDecision("manual_recovery_required", "restart has no safe boundary", False)
    return RecoveryDecision("resume_same_thread", "exact-compatible current checkpoint", True)
