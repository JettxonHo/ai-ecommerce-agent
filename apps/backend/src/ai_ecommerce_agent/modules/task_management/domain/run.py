"""Framework-neutral Run lifecycle entity.

Each Run is one immutable execution identity. Retry and resume callers must
construct a new Run with a new RunId and retain the previous identity through
``source_run_id``; no runtime ``thread_id`` or checkpoint state belongs here.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

from .errors import InvalidTransitionError, RevisionConflictError
from .snapshots import DomainVersionReference, RunStatus, StageReference


def _require_revision(current: Revision, expected: Revision, *, resource: str) -> None:
    if current != expected:
        raise RevisionConflictError(
            resource=resource, expected=expected, current=current
        )


def _require_text(value: str, *, field: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _invalid(run: Run, *, intent: str) -> InvalidTransitionError:
    return InvalidTransitionError(
        resource="run", status=run.status.value, intent=intent
    )


@dataclass(frozen=True, slots=True)
class Run:
    """Immutable monitor state for one Task-scoped workflow execution."""

    run_id: RunId
    task_id: TaskId
    source_run_id: RunId | None
    status: RunStatus
    revision: Revision
    current_stage: StageReference | None
    started_at: datetime | None
    updated_at: datetime
    completed_at: datetime | None
    failure_summary: str | None
    last_valid_result: DomainVersionReference | None

    def __post_init__(self) -> None:
        if self.source_run_id == self.run_id:
            raise ValueError("source Run identity must differ from Run identity")
        if self.failure_summary is not None:
            _require_text(self.failure_summary, field="failure_summary")

    @classmethod
    def create(
        cls,
        run_id: RunId,
        task_id: TaskId,
        *,
        current_stage: StageReference | None = None,
        updated_at: datetime,
    ) -> Self:
        """Create a queued Run with no runtime/thread identity."""

        return cls(
            run_id=run_id,
            task_id=task_id,
            source_run_id=None,
            status=RunStatus.QUEUED,
            revision=Revision.initial(),
            current_stage=current_stage,
            started_at=None,
            updated_at=updated_at,
            completed_at=None,
            failure_summary=None,
            last_valid_result=None,
        )

    @classmethod
    def create_retry(
        cls,
        run_id: RunId,
        task_id: TaskId,
        *,
        source_run_id: RunId,
        current_stage: StageReference | None = None,
        updated_at: datetime,
    ) -> Self:
        """Create a new retry identity while leaving the source Run unchanged."""

        if run_id == source_run_id:
            raise ValueError("retry Run identity must differ from source Run")
        return cls(
            run_id=run_id,
            task_id=task_id,
            source_run_id=source_run_id,
            status=RunStatus.RETRYING,
            revision=Revision.initial(),
            current_stage=current_stage,
            started_at=None,
            updated_at=updated_at,
            completed_at=None,
            failure_summary=None,
            last_valid_result=None,
        )

    @classmethod
    def create_resume(
        cls,
        run_id: RunId,
        task_id: TaskId,
        *,
        source_run_id: RunId,
        current_stage: StageReference | None = None,
        updated_at: datetime,
    ) -> Self:
        """Create a queued Run for an explicit resume of an earlier Run."""

        if run_id == source_run_id:
            raise ValueError("resume Run identity must differ from source Run")
        return cls(
            run_id=run_id,
            task_id=task_id,
            source_run_id=source_run_id,
            status=RunStatus.QUEUED,
            revision=Revision.initial(),
            current_stage=current_stage,
            started_at=None,
            updated_at=updated_at,
            completed_at=None,
            failure_summary=None,
            last_valid_result=None,
        )

    def start(
        self,
        *,
        expected_revision: Revision,
        updated_at: datetime,
        started_at: datetime | None = None,
    ) -> Self:
        """Start a queued or retrying Run with caller-provided timestamps."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status not in {RunStatus.QUEUED, RunStatus.RETRYING}:
            raise _invalid(self, intent="start")
        return replace(
            self,
            status=RunStatus.RUNNING,
            revision=self.revision.next(),
            started_at=self.started_at or started_at or updated_at,
            updated_at=updated_at,
            completed_at=None,
            failure_summary=None,
        )

    def wait_for_input(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Wait for input while preserving this Run identity."""

        return self._wait(
            stage,
            expected_revision=expected_revision,
            updated_at=updated_at,
            status=RunStatus.WAITING_FOR_INPUT,
            intent="wait_for_input",
        )

    def wait_for_review(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Wait at the single mandatory Human Review stage only."""

        if stage is not StageReference.HUMAN_REVIEW:
            raise _invalid(self, intent="wait_for_review")
        return self._wait(
            stage,
            expected_revision=expected_revision,
            updated_at=updated_at,
            status=RunStatus.WAITING_FOR_REVIEW,
            intent="wait_for_review",
        )

    def pause(self, *, expected_revision: Revision, updated_at: datetime) -> Self:
        """Pause a running Run for recoverable manual handling."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status is not RunStatus.RUNNING:
            raise _invalid(self, intent="pause")
        return replace(
            self,
            status=RunStatus.PAUSED,
            revision=self.revision.next(),
            updated_at=updated_at,
        )

    def complete(
        self,
        *,
        expected_revision: Revision,
        updated_at: datetime,
        completed_at: datetime,
        last_valid_result: DomainVersionReference | None = None,
    ) -> Self:
        """Complete execution; completion is never Human Review approval."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status is not RunStatus.RUNNING:
            raise _invalid(self, intent="complete")
        return replace(
            self,
            status=RunStatus.COMPLETED,
            revision=self.revision.next(),
            updated_at=updated_at,
            completed_at=completed_at,
            last_valid_result=(
                self.last_valid_result
                if last_valid_result is None
                else last_valid_result
            ),
        )

    def fail(
        self,
        failure_summary: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
        completed_at: datetime,
    ) -> Self:
        """Record a safe terminal failure summary."""

        _require_revision(self.revision, expected_revision, resource="run")
        _require_text(failure_summary, field="failure_summary")
        if self.status not in {
            RunStatus.RUNNING,
            RunStatus.RETRYING,
            RunStatus.WAITING_FOR_INPUT,
            RunStatus.WAITING_FOR_REVIEW,
            RunStatus.PAUSED,
        }:
            raise _invalid(self, intent="fail")
        return replace(
            self,
            status=RunStatus.FAILED,
            revision=self.revision.next(),
            updated_at=updated_at,
            completed_at=completed_at,
            failure_summary=failure_summary,
        )

    def request_cancellation(
        self, *, expected_revision: Revision, updated_at: datetime
    ) -> Self:
        """Persist cancellation intent without claiming terminal completion."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status not in {
            RunStatus.QUEUED,
            RunStatus.RUNNING,
            RunStatus.RETRYING,
            RunStatus.WAITING_FOR_INPUT,
            RunStatus.WAITING_FOR_REVIEW,
            RunStatus.PAUSED,
        }:
            raise _invalid(self, intent="request_cancellation")
        return replace(
            self,
            status=RunStatus.CANCELLATION_REQUESTED,
            revision=self.revision.next(),
            updated_at=updated_at,
        )

    def finalize_cancellation(
        self,
        *,
        expected_revision: Revision,
        updated_at: datetime,
        completed_at: datetime,
    ) -> Self:
        """Finalize cancellation only after the current owner has stopped."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status is not RunStatus.CANCELLATION_REQUESTED:
            raise _invalid(self, intent="finalize_cancellation")
        return replace(
            self,
            status=RunStatus.CANCELLED,
            revision=self.revision.next(),
            updated_at=updated_at,
            completed_at=completed_at,
        )

    def supersede(
        self,
        *,
        expected_revision: Revision,
        updated_at: datetime,
        completed_at: datetime,
    ) -> Self:
        """Mark a non-terminal obsolete Run so it cannot commit later work."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status in {
            RunStatus.COMPLETED,
            RunStatus.FAILED,
            RunStatus.CANCELLED,
            RunStatus.SUPERSEDED,
        }:
            raise _invalid(self, intent="supersede")
        return replace(
            self,
            status=RunStatus.SUPERSEDED,
            revision=self.revision.next(),
            updated_at=updated_at,
            completed_at=completed_at,
        )

    def move_to_stage(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Update monitor navigation without owning Stage Current Truth."""

        _require_revision(self.revision, expected_revision, resource="run")
        if self.status in {
            RunStatus.COMPLETED,
            RunStatus.FAILED,
            RunStatus.CANCELLED,
            RunStatus.CANCELLATION_REQUESTED,
            RunStatus.SUPERSEDED,
        }:
            raise _invalid(self, intent="move_to_stage")
        return replace(
            self,
            current_stage=stage,
            revision=self.revision.next(),
            updated_at=updated_at,
        )

    def _wait(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
        updated_at: datetime,
        status: RunStatus,
        intent: str,
    ) -> Self:
        _require_revision(self.revision, expected_revision, resource="run")
        if self.status is not RunStatus.RUNNING:
            raise _invalid(self, intent=intent)
        return replace(
            self,
            status=status,
            current_stage=stage,
            revision=self.revision.next(),
            updated_at=updated_at,
        )


__all__ = ["Run"]
