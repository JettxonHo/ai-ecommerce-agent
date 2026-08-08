"""Framework-neutral Task-scoped Stage Current Truth entity."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

from .errors import InvalidTransitionError, RevisionConflictError
from .snapshots import DomainVersionReference, StageReference, StageStatus


def _require_revision(current: Revision, expected: Revision) -> None:
    if current != expected:
        raise RevisionConflictError(
            resource="stage", expected=expected, current=current
        )


def _require_text(value: str, *, field: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _invalid(stage: Stage, *, intent: str) -> InvalidTransitionError:
    return InvalidTransitionError(
        resource="stage", status=stage.status.value, intent=intent
    )


def _require_new_run(stage: Stage, run_id: RunId) -> None:
    if stage.last_run_id == run_id:
        raise ValueError("stage rerun must use a new Run identity")


@dataclass(frozen=True, slots=True)
class Stage:
    """One independent Task-scoped mutable Stage Current Truth record.

    ``current_version`` is the currently valid result for this Stage, while
    ``last_valid_version`` preserves the latest valid history after an
    invalidation, failed execution, or explicit rerun. A Stage never embeds a
    Task, Run, or collection of other stages.
    """

    task_id: TaskId
    stage: StageReference
    status: StageStatus
    revision: Revision
    current_version: DomainVersionReference | None
    last_valid_version: DomainVersionReference | None
    last_run_id: RunId | None
    waiting_reason: str | None
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.waiting_reason is not None:
            _require_text(self.waiting_reason, field="waiting_reason")

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        stage: StageReference,
        *,
        updated_at: datetime,
    ) -> Self:
        """Create a Task-scoped Stage in the accepted ``not_started`` state."""

        return cls(
            task_id=task_id,
            stage=stage,
            status=StageStatus.NOT_STARTED,
            revision=Revision.initial(),
            current_version=None,
            last_valid_version=None,
            last_run_id=None,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def prepare(self, *, expected_revision: Revision, updated_at: datetime) -> Self:
        """Arm an untouched Stage for its first execution."""

        _require_revision(self.revision, expected_revision)
        if self.status is not StageStatus.NOT_STARTED:
            raise _invalid(self, intent="prepare")
        return replace(
            self,
            status=StageStatus.READY,
            revision=self.revision.next(),
            updated_at=updated_at,
        )

    def start(
        self,
        run_id: RunId,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Start a ready Stage under a concrete Run identity."""

        _require_revision(self.revision, expected_revision)
        if self.status is not StageStatus.READY:
            raise _invalid(self, intent="start")
        _require_new_run(self, run_id)
        return replace(
            self,
            status=StageStatus.RUNNING,
            revision=self.revision.next(),
            last_run_id=run_id,
            current_version=None,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def resume(
        self,
        run_id: RunId,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Resume a waiting or failed Stage with a new Run identity."""

        _require_revision(self.revision, expected_revision)
        if self.status not in {StageStatus.WAITING_INPUT, StageStatus.FAILED}:
            raise _invalid(self, intent="resume")
        _require_new_run(self, run_id)
        return replace(
            self,
            status=StageStatus.RUNNING,
            revision=self.revision.next(),
            last_run_id=run_id,
            current_version=None,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def prepare_rerun(
        self, *, expected_revision: Revision, updated_at: datetime
    ) -> Self:
        """Re-arm invalid, failed, or waiting work for explicit rerun."""

        _require_revision(self.revision, expected_revision)
        if self.status not in {
            StageStatus.INVALID,
            StageStatus.FAILED,
            StageStatus.WAITING_INPUT,
            StageStatus.WAITING_REVIEW,
        }:
            raise _invalid(self, intent="prepare_rerun")
        return replace(
            self,
            status=StageStatus.READY,
            revision=self.revision.next(),
            current_version=None,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def wait_for_input(
        self,
        reason: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Record a real user-input block without fabricating a result."""

        return self._wait(
            reason,
            expected_revision=expected_revision,
            updated_at=updated_at,
            status=StageStatus.WAITING_INPUT,
            intent="wait_for_input",
        )

    def wait_for_review(
        self,
        reason: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Record the mandatory wait only on the Human Review Stage."""

        if self.stage is not StageReference.HUMAN_REVIEW:
            raise _invalid(self, intent="wait_for_review")
        return self._wait(
            reason,
            expected_revision=expected_revision,
            updated_at=updated_at,
            status=StageStatus.WAITING_REVIEW,
            intent="wait_for_review",
        )

    def mark_valid(
        self,
        version: DomainVersionReference,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Promote a validated immutable version to Stage Current Truth."""

        _require_revision(self.revision, expected_revision)
        if self.status is not StageStatus.RUNNING and not (
            self.status is StageStatus.WAITING_REVIEW
            and self.stage is StageReference.HUMAN_REVIEW
        ):
            raise _invalid(self, intent="mark_valid")
        return replace(
            self,
            status=StageStatus.VALID,
            revision=self.revision.next(),
            current_version=version,
            last_valid_version=version,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def invalidate(self, *, expected_revision: Revision, updated_at: datetime) -> Self:
        """Clear current truth while preserving the latest valid version."""

        _require_revision(self.revision, expected_revision)
        if self.status is not StageStatus.VALID:
            raise _invalid(self, intent="invalidate")
        return replace(
            self,
            status=StageStatus.INVALID,
            revision=self.revision.next(),
            current_version=None,
            updated_at=updated_at,
        )

    def mark_failed(
        self,
        reason: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Record a failed execution without making a failed result current."""

        _require_revision(self.revision, expected_revision)
        _require_text(reason, field="waiting_reason")
        if self.status is not StageStatus.RUNNING:
            raise _invalid(self, intent="mark_failed")
        return replace(
            self,
            status=StageStatus.FAILED,
            revision=self.revision.next(),
            current_version=None,
            waiting_reason=reason,
            updated_at=updated_at,
        )

    def skip(self, *, expected_revision: Revision, updated_at: datetime) -> Self:
        """Skip a Stage only before execution starts."""

        _require_revision(self.revision, expected_revision)
        if self.status not in {StageStatus.NOT_STARTED, StageStatus.READY}:
            raise _invalid(self, intent="skip")
        return replace(
            self,
            status=StageStatus.SKIPPED,
            revision=self.revision.next(),
            current_version=None,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def _wait(
        self,
        reason: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
        status: StageStatus,
        intent: str,
    ) -> Self:
        _require_revision(self.revision, expected_revision)
        _require_text(reason, field="waiting_reason")
        if self.status is not StageStatus.RUNNING:
            raise _invalid(self, intent=intent)
        return replace(
            self,
            status=status,
            revision=self.revision.next(),
            current_version=None,
            waiting_reason=reason,
            updated_at=updated_at,
        )


__all__ = ["Stage"]
