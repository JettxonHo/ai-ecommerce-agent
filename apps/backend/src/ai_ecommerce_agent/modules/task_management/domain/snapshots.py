"""Framework-neutral Task Management catalog and immutable snapshot DTOs.

This A1 slice publishes only the stable state/reference catalog and pure
frozen data contracts.  Lifecycle entities, ownership checks, repositories
and transition commands are intentionally delivered by later slices.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    Revision,
    RunId,
    TaskId,
    VersionNumber,
)


class TaskStatus(StrEnum):
    """Accepted Task lifecycle values from RFC-004/OpenAPI."""

    DRAFT = "draft"
    RUNNING = "running"
    WAITING_FOR_INPUT = "waiting_for_input"
    WAITING_FOR_REVIEW = "waiting_for_review"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunStatus(StrEnum):
    """Accepted Run monitor values from RFC-004/OpenAPI."""

    QUEUED = "queued"
    RUNNING = "running"
    RETRYING = "retrying"
    WAITING_FOR_INPUT = "waiting_for_input"
    WAITING_FOR_REVIEW = "waiting_for_review"
    PAUSED = "paused"
    CANCELLATION_REQUESTED = "cancellation_requested"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"


class StageStatus(StrEnum):
    """Accepted Stage values from RFC-004/OpenAPI."""

    NOT_STARTED = "not_started"
    READY = "ready"
    RUNNING = "running"
    WAITING_INPUT = "waiting_input"
    WAITING_REVIEW = "waiting_review"
    VALID = "valid"
    INVALID = "invalid"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageReference(StrEnum):
    """The exact six public stage references; no additional stage is implied."""

    PRODUCT_INTAKE_AND_FACT_EXTRACTION = "product_intake_and_fact_extraction"
    CUSTOMER_INSIGHT_ANALYSIS = "customer_insight_analysis"
    PRODUCT_POSITIONING = "product_positioning"
    HUMAN_REVIEW = "human_review"
    MARKETING_BRIEF_GENERATION = "marketing_brief_generation"
    XIAOHONGSHU_BRIEF_MAPPING = "xiaohongshu_brief_mapping"


@dataclass(frozen=True, slots=True)
class DomainVersionReference:
    """Immutable reference to a committed domain version."""

    version_id: DomainVersionId
    version_number: VersionNumber


@dataclass(frozen=True, slots=True)
class TaskSnapshot:
    """Immutable Task navigation snapshot; it contains no Stage collection."""

    task_id: TaskId
    task_name: str
    product_category: str
    promotion_goal: str
    status: TaskStatus
    revision: Revision
    current_stage: StageReference | None
    current_run_id: RunId | None
    latest_run_id: RunId | None
    waiting_reason: str | None
    updated_at: datetime | None

    @property
    def task_status(self) -> TaskStatus:
        """Expose the OpenAPI name without storing duplicate state."""

        return self.status


@dataclass(frozen=True, slots=True)
class RunSnapshot:
    """Immutable Run monitor snapshot without runtime/thread identifiers."""

    run_id: RunId
    task_id: TaskId
    revision: Revision
    source_run_id: RunId | None
    status: RunStatus
    current_stage: StageReference | None
    started_at: datetime | None
    updated_at: datetime | None
    completed_at: datetime | None
    failure_summary: str | None
    last_valid_result: DomainVersionReference | None


@dataclass(frozen=True, slots=True)
class StageSnapshot:
    """Immutable projection of one Task-scoped Stage Current Truth row."""

    task_id: TaskId
    stage: StageReference
    status: StageStatus
    revision: Revision
    current_version: DomainVersionReference | None
    last_valid_version: DomainVersionReference | None
    last_run_id: RunId | None
    waiting_reason: str | None
    updated_at: datetime | None


__all__ = [
    "DomainVersionReference",
    "RunSnapshot",
    "RunStatus",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "TaskSnapshot",
    "TaskStatus",
]
