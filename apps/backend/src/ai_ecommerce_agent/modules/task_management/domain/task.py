"""Framework-neutral Task lifecycle entity.

Task is a narrow navigation owner. It stores the Task identity and the
current/latest Run pointers, but never embeds Run or Stage entities. The
application layer coordinates Run and Stage commits around these immutable
state transitions.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

from .errors import InvalidTransitionError, RevisionConflictError
from .snapshots import StageReference, TaskStatus


def _require_revision(current: Revision, expected: Revision, *, resource: str) -> None:
    if current != expected:
        raise RevisionConflictError(
            resource=resource, expected=expected, current=current
        )


def _require_text(value: str, *, field: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _invalid(task: Task, *, intent: str) -> InvalidTransitionError:
    return InvalidTransitionError(
        resource="task", status=task.task_status.value, intent=intent
    )


@dataclass(frozen=True, slots=True)
class Task:
    """Immutable Task navigation state and Run pointers.

    ``active_run_id`` is the domain name for OpenAPI ``activeRun``. This
    Task entity has no queued/retrying/cancellation-requested Task status, so
    the pointer is set while a Task is running and cleared for waiting,
    paused, failed, or terminal navigation states. ``latest_run_id`` keeps
    the most recent Run for navigation after the active pointer is cleared.
    """

    task_id: TaskId
    task_name: str
    product_category: str
    promotion_goal: str
    task_status: TaskStatus
    revision: Revision
    current_stage: StageReference | None
    active_run_id: RunId | None
    latest_run_id: RunId | None
    waiting_reason: str | None
    updated_at: datetime

    def __post_init__(self) -> None:
        _require_text(self.task_name, field="task_name")
        _require_text(self.product_category, field="product_category")
        _require_text(self.promotion_goal, field="promotion_goal")
        if self.waiting_reason is not None:
            _require_text(self.waiting_reason, field="waiting_reason")

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        *,
        task_name: str,
        product_category: str,
        promotion_goal: str,
        updated_at: datetime,
    ) -> Self:
        """Create a stable draft Task without starting a Run."""

        return cls(
            task_id=task_id,
            task_name=task_name,
            product_category=product_category,
            promotion_goal=promotion_goal,
            task_status=TaskStatus.DRAFT,
            revision=Revision.initial(),
            current_stage=None,
            active_run_id=None,
            latest_run_id=None,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def start(
        self,
        run_id: RunId,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Start a draft Task and bind its newly-created Run identity."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.task_status is not TaskStatus.DRAFT:
            raise _invalid(self, intent="start")
        return replace(
            self,
            task_status=TaskStatus.RUNNING,
            revision=self.revision.next(),
            active_run_id=run_id,
            latest_run_id=run_id,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def wait_for_input(
        self,
        stage: StageReference,
        reason: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Enter a real input wait and clear the active Run pointer."""

        return self._wait(
            stage,
            reason,
            expected_revision=expected_revision,
            updated_at=updated_at,
            status=TaskStatus.WAITING_FOR_INPUT,
            intent="wait_for_input",
        )

    def wait_for_review(
        self,
        stage: StageReference,
        reason: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Enter the single mandatory Human Review gate."""

        if stage is not StageReference.HUMAN_REVIEW:
            raise _invalid(self, intent="wait_for_review")
        return self._wait(
            stage,
            reason,
            expected_revision=expected_revision,
            updated_at=updated_at,
            status=TaskStatus.WAITING_FOR_REVIEW,
            intent="wait_for_review",
        )

    def pause(
        self,
        reason: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Pause a running Task for explicit recovery handling."""

        _require_revision(self.revision, expected_revision, resource="task")
        _require_text(reason, field="waiting_reason")
        if self.task_status is not TaskStatus.RUNNING:
            raise _invalid(self, intent="pause")
        return replace(
            self,
            task_status=TaskStatus.PAUSED,
            revision=self.revision.next(),
            active_run_id=None,
            waiting_reason=reason,
            updated_at=updated_at,
        )

    def resume(
        self,
        run_id: RunId,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Resume a blocked Task by binding a different, new Run identity."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.task_status not in {
            TaskStatus.WAITING_FOR_INPUT,
            TaskStatus.WAITING_FOR_REVIEW,
            TaskStatus.PAUSED,
            TaskStatus.FAILED,
        }:
            raise _invalid(self, intent="resume")
        if self.latest_run_id == run_id:
            raise ValueError("resume Run identity must differ from latest Run")
        return replace(
            self,
            task_status=TaskStatus.RUNNING,
            revision=self.revision.next(),
            active_run_id=run_id,
            latest_run_id=run_id,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def complete(self, *, expected_revision: Revision, updated_at: datetime) -> Self:
        """Complete a running Task; this is not Human Review approval."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.task_status is not TaskStatus.RUNNING:
            raise _invalid(self, intent="complete")
        return replace(
            self,
            task_status=TaskStatus.COMPLETED,
            revision=self.revision.next(),
            active_run_id=None,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def fail(
        self,
        reason: str | None = None,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Record a Task failure and clear its active Run pointer."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.task_status not in {
            TaskStatus.RUNNING,
            TaskStatus.WAITING_FOR_INPUT,
            TaskStatus.WAITING_FOR_REVIEW,
            TaskStatus.PAUSED,
        }:
            raise _invalid(self, intent="fail")
        if reason is not None:
            _require_text(reason, field="waiting_reason")
        return replace(
            self,
            task_status=TaskStatus.FAILED,
            revision=self.revision.next(),
            active_run_id=None,
            waiting_reason=reason,
            updated_at=updated_at,
        )

    def finalize_cancellation(
        self, *, expected_revision: Revision, updated_at: datetime
    ) -> Self:
        """Finalize cancellation after the application stops the current Run.

        Task has no ``cancellation_requested`` state. The application command
        first coordinates Run cancellation and then calls this terminal intent
        once the Run is terminal; this entity intentionally does not own that
        cross-entity coordination.
        """

        _require_revision(self.revision, expected_revision, resource="task")
        if self.task_status not in {
            TaskStatus.RUNNING,
            TaskStatus.WAITING_FOR_INPUT,
            TaskStatus.WAITING_FOR_REVIEW,
            TaskStatus.PAUSED,
        }:
            raise _invalid(self, intent="finalize_cancellation")
        return replace(
            self,
            task_status=TaskStatus.CANCELLED,
            revision=self.revision.next(),
            active_run_id=None,
            waiting_reason=None,
            updated_at=updated_at,
        )

    def move_to_stage(
        self,
        stage: StageReference,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Move Task navigation without embedding or mutating a Stage entity."""

        _require_revision(self.revision, expected_revision, resource="task")
        if self.task_status in {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
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
        reason: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
        status: TaskStatus,
        intent: str,
    ) -> Self:
        _require_revision(self.revision, expected_revision, resource="task")
        _require_text(reason, field="waiting_reason")
        if self.task_status is not TaskStatus.RUNNING:
            raise _invalid(self, intent=intent)
        return replace(
            self,
            task_status=status,
            current_stage=stage,
            revision=self.revision.next(),
            active_run_id=None,
            waiting_reason=reason,
            updated_at=updated_at,
        )


__all__ = ["Task"]
