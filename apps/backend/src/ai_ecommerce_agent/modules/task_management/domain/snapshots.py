"""Immutable Task, Run and Stage domain entities and snapshot DTOs.

The first Task Management slice deliberately models each concern as a narrow
immutable record.  Entity transition methods return a new entity and therefore
cannot silently mutate a persisted object or form a Task mega aggregate.
Task owns navigation and Run pointers; Run owns execution lifecycle; Stage
owns one Task-scoped stage lifecycle and its version references.  Public
snapshot DTOs below are separate data-only contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from typing import Self, cast, overload

from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    Revision,
    RunId,
    TaskId,
    VersionNumber,
)

from .errors import InvalidTransitionError, RevisionConflictError


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
    """A stable immutable business version reference.

    ``DomainVersionId`` and ``VersionNumber`` remain distinct values.  This
    lightweight reference is owned by Task Management only for Stage current
    and last-valid pointers; the referenced business object's content remains
    owned by its capability module.
    """

    version_id: DomainVersionId
    version_number: VersionNumber


def _require_revision(
    current: Revision,
    expected: Revision,
    *,
    resource: str,
) -> None:
    """Apply the semantic compare-and-swap precondition in the domain."""

    if current != expected:
        raise RevisionConflictError(
            {
                "resource": resource,
                "expectedRevision": str(expected.value),
                "currentRevision": str(current.value),
            }
        )


def _invalid_transition(
    *,
    resource: str,
    current: StrEnum,
    intent: str,
) -> InvalidTransitionError:
    """Build one stable error for a named, non-generic transition intent."""

    return InvalidTransitionError(
        {
            "resource": resource,
            "fromStatus": str(current.value),
            "intent": intent,
        }
    )


@dataclass(frozen=True, slots=True)
class Task:
    """Task navigation plus active and latest Run pointers.

    ``current_run_id`` is the OpenAPI ``activeRun`` pointer and is populated
    only while the Run is queued, running, retrying or cancellation-requested.
    Waiting, paused, failed and terminal states clear it; ``latest_run_id``
    remains the navigation pointer to the most recent Run.
    """

    task_id: TaskId
    task_name: str
    product_category: str
    promotion_goal: str
    status: TaskStatus = TaskStatus.DRAFT
    revision: Revision = Revision.initial()
    current_stage: StageReference | None = None
    current_run_id: RunId | None = None
    latest_run_id: RunId | None = None
    waiting_reason: str | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.task_name, field="task_name")
        _require_non_empty(self.product_category, field="product_category")
        _require_non_empty(self.promotion_goal, field="promotion_goal")
        if self.waiting_reason is not None:
            _require_non_empty(self.waiting_reason, field="waiting_reason")

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        *,
        task_name: str,
        product_category: str,
        promotion_goal: str,
        updated_at: datetime | None = None,
    ) -> Self:
        """Construct a new Task in the accepted ``draft`` state."""

        return cls(
            task_id=task_id,
            task_name=task_name,
            product_category=product_category,
            promotion_goal=promotion_goal,
            updated_at=updated_at,
        )

    def start(self, run_id: RunId, *, expected_revision: Revision) -> Task:
        """Start a draft Task and bind its active/latest Run pointer."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.status is not TaskStatus.DRAFT:
            raise _invalid_transition(
                resource="task", current=self.status, intent="start"
            )
        return _next_revision(
            replace(
                self,
                status=TaskStatus.RUNNING,
                current_run_id=run_id,
                latest_run_id=run_id,
                waiting_reason=None,
            )
        )

    def resume(self, run_id: RunId, *, expected_revision: Revision) -> Task:
        """Resume a blocked Task with a newly-created Run identity."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.status not in {
            TaskStatus.WAITING_FOR_INPUT,
            TaskStatus.WAITING_FOR_REVIEW,
            TaskStatus.PAUSED,
            TaskStatus.FAILED,
        }:
            raise _invalid_transition(
                resource="task", current=self.status, intent="resume"
            )
        return _next_revision(
            replace(
                self,
                status=TaskStatus.RUNNING,
                current_run_id=run_id,
                latest_run_id=run_id,
                waiting_reason=None,
            )
        )

    def wait_for_input(
        self,
        stage: StageReference,
        reason: str,
        *,
        expected_revision: Revision,
    ) -> Task:
        """Pause navigation at a real input block for one stage."""

        return self._wait(
            stage,
            reason,
            expected_revision=expected_revision,
            status=TaskStatus.WAITING_FOR_INPUT,
            intent="wait_for_input",
        )

    def wait_for_review(
        self,
        stage: StageReference,
        reason: str,
        *,
        expected_revision: Revision,
    ) -> Task:
        """Pause navigation at the mandatory Human Review stage."""

        if stage is not StageReference.HUMAN_REVIEW:
            raise InvalidTransitionError(
                {
                    "resource": "task",
                    "fromStatus": self.status.value,
                    "intent": "wait_for_review",
                }
            )
        return self._wait(
            stage,
            reason,
            expected_revision=expected_revision,
            status=TaskStatus.WAITING_FOR_REVIEW,
            intent="wait_for_review",
        )

    def pause(self, reason: str, *, expected_revision: Revision) -> Task:
        """Pause a running Task for explicit recovery handling."""

        _require_revision(self.revision, expected_revision, resource="task")
        _require_non_empty(reason, field="waiting_reason")
        if self.status is not TaskStatus.RUNNING:
            raise _invalid_transition(
                resource="task", current=self.status, intent="pause"
            )
        return _next_revision(
            replace(
                self,
                status=TaskStatus.PAUSED,
                current_run_id=None,
                waiting_reason=reason,
            )
        )

    def complete(self, *, expected_revision: Revision) -> Task:
        """Mark a running Task complete and clear its active Run pointer."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.status is not TaskStatus.RUNNING:
            raise _invalid_transition(
                resource="task", current=self.status, intent="complete"
            )
        return _next_revision(
            replace(
                self,
                status=TaskStatus.COMPLETED,
                current_run_id=None,
                waiting_reason=None,
            )
        )

    def fail(self, reason: str | None = None, *, expected_revision: Revision) -> Task:
        """Record an unrecoverable Task failure and clear its active Run."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.status not in {
            TaskStatus.RUNNING,
            TaskStatus.WAITING_FOR_INPUT,
            TaskStatus.WAITING_FOR_REVIEW,
            TaskStatus.PAUSED,
        }:
            raise _invalid_transition(
                resource="task", current=self.status, intent="fail"
            )
        if reason is not None:
            _require_non_empty(reason, field="waiting_reason")
        return _next_revision(
            replace(
                self,
                status=TaskStatus.FAILED,
                current_run_id=None,
                waiting_reason=reason,
            )
        )

    def cancel(self, *, expected_revision: Revision) -> Task:
        """Cancel a non-terminal Task; terminal results remain immutable."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.status in {TaskStatus.COMPLETED, TaskStatus.CANCELLED}:
            raise _invalid_transition(
                resource="task", current=self.status, intent="cancel"
            )
        return _next_revision(
            replace(
                self,
                status=TaskStatus.CANCELLED,
                current_run_id=None,
                waiting_reason=None,
            )
        )

    def move_to_stage(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
    ) -> Task:
        """Update Task navigation without changing Run or Stage truth."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.status in {TaskStatus.COMPLETED, TaskStatus.CANCELLED}:
            raise _invalid_transition(
                resource="task", current=self.status, intent="move_to_stage"
            )
        return _next_revision(replace(self, current_stage=stage))

    def _wait(
        self,
        stage: StageReference,
        reason: str,
        *,
        expected_revision: Revision,
        status: TaskStatus,
        intent: str,
    ) -> Task:
        _require_non_empty(reason, field="waiting_reason")
        _require_revision(self.revision, expected_revision, resource="task")
        if self.status is not TaskStatus.RUNNING:
            raise _invalid_transition(
                resource="task", current=self.status, intent=intent
            )
        return _next_revision(
            replace(
                self,
                status=status,
                current_stage=stage,
                current_run_id=None,
                waiting_reason=reason,
            )
        )


@dataclass(frozen=True, slots=True)
class Run:
    """One workflow execution monitor scoped to exactly one Task."""

    run_id: RunId
    task_id: TaskId
    source_run_id: RunId | None = None
    status: RunStatus = RunStatus.QUEUED
    revision: Revision = Revision.initial()
    current_stage: StageReference | None = None
    started_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None
    failure_summary: str | None = None
    last_valid_result: DomainVersionReference | None = None

    def __post_init__(self) -> None:
        if self.failure_summary is not None:
            _require_non_empty(self.failure_summary, field="failure_summary")

    @classmethod
    def create(
        cls,
        run_id: RunId,
        task_id: TaskId,
        *,
        source_run_id: RunId | None = None,
        current_stage: StageReference | None = None,
        updated_at: datetime | None = None,
    ) -> Self:
        """Construct a queued Run; recovery callers provide a new RunId."""

        return cls(
            run_id=run_id,
            task_id=task_id,
            source_run_id=source_run_id,
            current_stage=current_stage,
            updated_at=updated_at,
        )

    @classmethod
    def create_retry(
        cls,
        run_id: RunId,
        task_id: TaskId,
        *,
        source_run_id: RunId,
        current_stage: StageReference | None = None,
        updated_at: datetime | None = None,
    ) -> Self:
        """Create a new retry Run while retaining the prior Run as source.

        Retry is a new execution identity.  The prior Run remains immutable
        and can be monitored independently; it is never mutated into a
        retrying attempt.
        """

        if run_id == source_run_id:
            raise ValueError("retry Run identity must differ from source Run")
        return cls(
            run_id=run_id,
            task_id=task_id,
            source_run_id=source_run_id,
            status=RunStatus.RETRYING,
            current_stage=current_stage,
            updated_at=updated_at,
        )

    def start(
        self,
        *,
        expected_revision: Revision,
        started_at: datetime | None = None,
    ) -> Run:
        """Start a queued or explicitly retrying Run."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status not in {RunStatus.QUEUED, RunStatus.RETRYING}:
            raise _invalid_transition(
                resource="run", current=self.status, intent="start"
            )
        return _next_revision(
            replace(
                self,
                status=RunStatus.RUNNING,
                started_at=self.started_at
                if self.started_at is not None
                else started_at,
                completed_at=None,
                failure_summary=None,
            )
        )

    def wait_for_input(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
    ) -> Run:
        """Put a running Run into a user-input wait."""

        return self._wait(
            stage,
            expected_revision=expected_revision,
            status=RunStatus.WAITING_FOR_INPUT,
            intent="wait_for_input",
        )

    def wait_for_review(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
    ) -> Run:
        """Put a running Run into the mandatory review wait."""

        if stage is not StageReference.HUMAN_REVIEW:
            raise InvalidTransitionError(
                {
                    "resource": "run",
                    "fromStatus": self.status.value,
                    "intent": "wait_for_review",
                }
            )
        return self._wait(
            stage,
            expected_revision=expected_revision,
            status=RunStatus.WAITING_FOR_REVIEW,
            intent="wait_for_review",
        )

    def pause(self, *, expected_revision: Revision) -> Run:
        """Pause a running Run for a recoverable blocking condition."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status is not RunStatus.RUNNING:
            raise _invalid_transition(
                resource="run", current=self.status, intent="pause"
            )
        return _next_revision(replace(self, status=RunStatus.PAUSED))

    def complete(
        self, *, expected_revision: Revision, completed_at: datetime | None = None
    ) -> Run:
        """Complete a running Run; completion is not Human Review approval."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status is not RunStatus.RUNNING:
            raise _invalid_transition(
                resource="run", current=self.status, intent="complete"
            )
        return _next_revision(
            replace(self, status=RunStatus.COMPLETED, completed_at=completed_at)
        )

    def fail(
        self,
        failure_summary: str,
        *,
        expected_revision: Revision,
        completed_at: datetime | None = None,
    ) -> Run:
        """Record a safe failure summary from an active Run."""

        _require_non_empty(failure_summary, field="failure_summary")
        _require_revision(self.revision, expected_revision, resource="run")
        if self.status not in {
            RunStatus.RUNNING,
            RunStatus.RETRYING,
            RunStatus.WAITING_FOR_INPUT,
            RunStatus.WAITING_FOR_REVIEW,
            RunStatus.PAUSED,
        }:
            raise _invalid_transition(
                resource="run", current=self.status, intent="fail"
            )
        return _next_revision(
            replace(
                self,
                status=RunStatus.FAILED,
                failure_summary=failure_summary,
                completed_at=completed_at,
            )
        )

    def request_cancellation(self, *, expected_revision: Revision) -> Run:
        """Persist cancellation intent before terminal cancellation."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status not in {
            RunStatus.QUEUED,
            RunStatus.RUNNING,
            RunStatus.RETRYING,
            RunStatus.WAITING_FOR_INPUT,
            RunStatus.WAITING_FOR_REVIEW,
            RunStatus.PAUSED,
        }:
            raise _invalid_transition(
                resource="run", current=self.status, intent="request_cancellation"
            )
        return _next_revision(replace(self, status=RunStatus.CANCELLATION_REQUESTED))

    def cancel(
        self, *, expected_revision: Revision, completed_at: datetime | None = None
    ) -> Run:
        """Finalize cancellation only after the worker has stopped."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status is not RunStatus.CANCELLATION_REQUESTED:
            raise _invalid_transition(
                resource="run", current=self.status, intent="cancel"
            )
        return _next_revision(
            replace(self, status=RunStatus.CANCELLED, completed_at=completed_at)
        )

    def supersede(self, *, expected_revision: Revision) -> Run:
        """Mark an obsolete execution so it cannot commit later results."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status in {
            RunStatus.COMPLETED,
            RunStatus.CANCELLED,
            RunStatus.SUPERSEDED,
        }:
            raise _invalid_transition(
                resource="run", current=self.status, intent="supersede"
            )
        return _next_revision(replace(self, status=RunStatus.SUPERSEDED))

    def move_to_stage(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
    ) -> Run:
        """Update execution navigation without changing business Stage truth."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status in {
            RunStatus.COMPLETED,
            RunStatus.CANCELLED,
            RunStatus.SUPERSEDED,
        }:
            raise _invalid_transition(
                resource="run", current=self.status, intent="move_to_stage"
            )
        return _next_revision(replace(self, current_stage=stage))

    def _wait(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
        status: RunStatus,
        intent: str,
    ) -> Run:
        _require_revision(self.revision, expected_revision, resource="run")
        if self.status is not RunStatus.RUNNING:
            raise _invalid_transition(
                resource="run", current=self.status, intent=intent
            )
        return _next_revision(replace(self, status=status, current_stage=stage))


@dataclass(frozen=True, slots=True)
class Stage:
    """One Task-scoped stage Current Truth record."""

    task_id: TaskId
    stage: StageReference
    status: StageStatus = StageStatus.NOT_STARTED
    revision: Revision = Revision.initial()
    current_version: DomainVersionReference | None = None
    last_valid_version: DomainVersionReference | None = None
    last_run_id: RunId | None = None
    waiting_reason: str | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.waiting_reason is not None:
            _require_non_empty(self.waiting_reason, field="waiting_reason")

    @classmethod
    def create(cls, task_id: TaskId, stage: StageReference) -> Self:
        """Construct a stage in the accepted ``not_started`` state."""

        return cls(task_id=task_id, stage=stage)

    def prepare(self, *, expected_revision: Revision) -> Stage:
        """Mark an untouched stage ready for its first execution."""

        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status is not StageStatus.NOT_STARTED:
            raise _invalid_transition(
                resource="stage", current=self.status, intent="prepare"
            )
        return _next_revision(replace(self, status=StageStatus.READY))

    def start(
        self,
        run_id: RunId,
        *,
        expected_revision: Revision,
    ) -> Stage:
        """Start a stage only from the explicit ready state."""

        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status is not StageStatus.READY:
            raise _invalid_transition(
                resource="stage", current=self.status, intent="start"
            )
        return _next_revision(
            replace(
                self,
                status=StageStatus.RUNNING,
                last_run_id=run_id,
                current_version=None,
                waiting_reason=None,
            )
        )

    def resume(self, run_id: RunId, *, expected_revision: Revision) -> Stage:
        """Resume a waiting/failed stage after an explicit recovery intent."""

        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status not in {
            StageStatus.WAITING_INPUT,
            StageStatus.WAITING_REVIEW,
            StageStatus.FAILED,
        }:
            raise _invalid_transition(
                resource="stage", current=self.status, intent="resume"
            )
        return _next_revision(
            replace(
                self,
                status=StageStatus.RUNNING,
                last_run_id=run_id,
                current_version=None,
                waiting_reason=None,
            )
        )

    def prepare_rerun(self, *, expected_revision: Revision) -> Stage:
        """Explicitly re-arm an invalid/failed/waiting stage for rerun."""

        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status not in {
            StageStatus.INVALID,
            StageStatus.FAILED,
            StageStatus.WAITING_INPUT,
            StageStatus.WAITING_REVIEW,
        }:
            raise _invalid_transition(
                resource="stage", current=self.status, intent="prepare_rerun"
            )
        return _next_revision(
            replace(
                self,
                status=StageStatus.READY,
                current_version=None,
                waiting_reason=None,
            )
        )

    def wait_for_input(
        self,
        reason: str,
        *,
        expected_revision: Revision,
    ) -> Stage:
        """Record a real user-input block without fabricating a result."""

        return self._wait(
            reason,
            expected_revision=expected_revision,
            status=StageStatus.WAITING_INPUT,
            intent="wait_for_input",
        )

    def wait_for_review(
        self,
        reason: str,
        *,
        expected_revision: Revision,
    ) -> Stage:
        """Record the mandatory Human Review wait."""

        if self.stage is not StageReference.HUMAN_REVIEW:
            raise InvalidTransitionError(
                {
                    "resource": "stage",
                    "fromStatus": self.status.value,
                    "intent": "wait_for_review",
                }
            )
        return self._wait(
            reason,
            expected_revision=expected_revision,
            status=StageStatus.WAITING_REVIEW,
            intent="wait_for_review",
        )

    def mark_valid(
        self,
        version: DomainVersionReference,
        *,
        expected_revision: Revision,
    ) -> Stage:
        """Promote a validated immutable domain version to Stage Current Truth."""

        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status is not StageStatus.RUNNING:
            raise _invalid_transition(
                resource="stage", current=self.status, intent="mark_valid"
            )
        return _next_revision(
            replace(
                self,
                status=StageStatus.VALID,
                current_version=version,
                last_valid_version=version,
                waiting_reason=None,
            )
        )

    def invalidate(self, *, expected_revision: Revision) -> Stage:
        """Invalidate current output while retaining the last valid pointer."""

        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status is not StageStatus.VALID:
            raise _invalid_transition(
                resource="stage", current=self.status, intent="invalidate"
            )
        return _next_revision(
            replace(self, status=StageStatus.INVALID, current_version=None)
        )

    def mark_failed(
        self,
        reason: str,
        *,
        expected_revision: Revision,
    ) -> Stage:
        """Record a failed run without exposing a failed version as current."""

        _require_non_empty(reason, field="waiting_reason")
        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status is not StageStatus.RUNNING:
            raise _invalid_transition(
                resource="stage", current=self.status, intent="mark_failed"
            )
        return _next_revision(
            replace(
                self,
                status=StageStatus.FAILED,
                current_version=None,
                waiting_reason=reason,
            )
        )

    def skip(self, *, expected_revision: Revision) -> Stage:
        """Mark an optional stage skipped only before execution starts."""

        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status not in {StageStatus.NOT_STARTED, StageStatus.READY}:
            raise _invalid_transition(
                resource="stage", current=self.status, intent="skip"
            )
        return _next_revision(replace(self, status=StageStatus.SKIPPED))

    def _wait(
        self,
        reason: str,
        *,
        expected_revision: Revision,
        status: StageStatus,
        intent: str,
    ) -> Stage:
        _require_non_empty(reason, field="waiting_reason")
        _require_revision(self.revision, expected_revision, resource="stage")
        if self.status is not StageStatus.RUNNING:
            raise _invalid_transition(
                resource="stage", current=self.status, intent=intent
            )
        return _next_revision(
            replace(self, status=status, current_version=None, waiting_reason=reason)
        )


@dataclass(frozen=True, slots=True)
class TaskSnapshot:
    """Immutable public Task projection; Stage rows are queried separately.

    Construction is intentionally data-only.  The application query layer
    owns mapping internal ``Task`` entities to this facade DTO; exposing that
    mapper here would couple the public contract to a domain implementation.
    """

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
        """OpenAPI-aligned name without duplicating a second status field."""

        return self.status


@dataclass(frozen=True, slots=True)
class RunSnapshot:
    """Immutable public Run monitor projection.

    The application query layer maps the internal ``Run`` entity; this DTO
    deliberately has no entity conversion method or runtime/thread identity.
    """

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
    """Immutable public projection of one Task/Stage pair.

    Mapping from the internal Stage entity remains an application query
    concern so this public contract stays a pure frozen data object.
    """

    task_id: TaskId
    stage: StageReference
    status: StageStatus
    revision: Revision
    current_version: DomainVersionReference | None
    last_valid_version: DomainVersionReference | None
    last_run_id: RunId | None
    waiting_reason: str | None
    updated_at: datetime | None


@overload
def _next_revision(snapshot: Task) -> Task: ...


@overload
def _next_revision(snapshot: Run) -> Run: ...


@overload
def _next_revision(snapshot: Stage) -> Stage: ...


def _next_revision(snapshot: Task | Run | Stage) -> Task | Run | Stage:
    """Return a copy with the owning mutable resource revision advanced."""

    return replace(snapshot, revision=snapshot.revision.next())


def _require_non_empty(value: str, *, field: str) -> None:
    """Keep domain text values deterministic and meaningful."""

    value_object = cast(object, value)
    if not isinstance(value_object, str):
        raise TypeError(f"{field} must be a string")
    if not value.strip():
        raise ValueError(f"{field} must not be empty")


__all__ = [
    "DomainVersionReference",
    "Run",
    "RunSnapshot",
    "RunStatus",
    "Stage",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "Task",
    "TaskSnapshot",
    "TaskStatus",
]
