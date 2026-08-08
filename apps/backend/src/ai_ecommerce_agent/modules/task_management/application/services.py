"""Application use cases for the Task/Run/Stage persistence slice."""

from __future__ import annotations

from collections.abc import Callable
from typing import NoReturn, TypeVar

from ai_ecommerce_agent.modules.task_management.application.errors import (
    TaskManagementConstraintError,
    TaskManagementError,
    TaskManagementOwnershipError,
    TaskManagementPersistenceError,
    TaskManagementResourceKind,
    TaskManagementResourceReference,
    TaskManagementRevisionConflictError,
)
from ai_ecommerce_agent.modules.task_management.application.mappers import (
    run_to_snapshot,
    stage_to_snapshot,
    task_to_snapshot,
)
from ai_ecommerce_agent.modules.task_management.application.ports import (
    TaskManagementUnitOfWork,
    TaskManagementUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.task_management.application.protocols import (
    TaskManagementApplication,
)
from ai_ecommerce_agent.modules.task_management.application.results import (
    PrepareInitialRunResult,
)
from ai_ecommerce_agent.modules.task_management.domain import (
    InvalidTransitionError,
    OwnershipError,
    RevisionConflictError,
    Run,
    RunSnapshot,
    Stage,
    StageReference,
    StageSnapshot,
    Task,
    TaskSnapshot,
)
from ai_ecommerce_agent.shared_kernel import ProjectError, Revision, RunId, TaskId

from .commands import CreateDraftTask, PrepareInitialRun
from .queries import GetRun, GetStage, GetTask

_ResultT = TypeVar("_ResultT")


def _task_reference(task_id: TaskId) -> TaskManagementResourceReference:
    return TaskManagementResourceReference(
        kind=TaskManagementResourceKind.TASK,
        task_id=task_id,
    )


def _run_reference(run_id: RunId) -> TaskManagementResourceReference:
    return TaskManagementResourceReference(
        kind=TaskManagementResourceKind.RUN,
        run_id=run_id,
    )


def _stage_reference(
    task_id: TaskId, stage: StageReference
) -> TaskManagementResourceReference:
    return TaskManagementResourceReference(
        kind=TaskManagementResourceKind.STAGE,
        task_id=task_id,
        stage=stage,
    )


def _not_found(reference: TaskManagementResourceReference, resource: str) -> NoReturn:
    raise _application_error(
        reference,
        error_code="not_found",
        message=f"{resource.capitalize()} was not found",
        recovery_hint="refresh",
    )


def _already_exists(
    reference: TaskManagementResourceReference, resource: str
) -> NoReturn:
    raise _application_error(
        reference,
        error_code="already_exists",
        message=f"{resource.capitalize()} identity is already in use",
        recovery_hint="refresh",
    )


def _application_error(
    reference: TaskManagementResourceReference,
    *,
    error_code: str,
    message: str,
    retryability: bool = False,
    expected_revision: int | None = None,
    actual_revision: int | None = None,
    conflicting_state: str | None = None,
    recovery_hint: str | None = None,
) -> TaskManagementError:
    return TaskManagementError(
        error_code=error_code,
        category="task_management",
        message=message,
        retryability=retryability,
        relevant_reference=reference,
        expected_revision=expected_revision,
        actual_revision=actual_revision,
        conflicting_state=conflicting_state,
        recovery_hint=recovery_hint,
    )


def _translate(
    error: Exception, reference: TaskManagementResourceReference
) -> TaskManagementError:
    """Map domain/adapter failures without exposing their implementation."""

    if isinstance(error, TaskManagementError):
        return error
    if isinstance(error, RevisionConflictError):
        context = error.safe_context
        expected = int(context["expected_revision"])
        current = int(context["current_revision"])
        return _application_error(
            reference,
            error_code="revision_conflict",
            message="The resource changed; refresh before retrying",
            expected_revision=expected,
            actual_revision=current,
            recovery_hint="refresh_and_compare",
        )
    if isinstance(error, TaskManagementRevisionConflictError):
        context = error.safe_context
        return _application_error(
            reference,
            error_code="revision_conflict",
            message="The resource changed; refresh before retrying",
            expected_revision=int(context["expected_revision"]),
            recovery_hint="refresh_and_compare",
        )
    if isinstance(error, InvalidTransitionError):
        context = error.safe_context
        return _application_error(
            reference,
            error_code="invalid_transition",
            message="The requested lifecycle transition is not available",
            conflicting_state=context.get("status"),
            recovery_hint="refresh",
        )
    if isinstance(error, OwnershipError):
        return _application_error(
            reference,
            error_code="ownership_conflict",
            message="The related resource belongs to a different Task",
            recovery_hint="refresh",
        )
    if isinstance(error, TaskManagementOwnershipError):
        return _application_error(
            reference,
            error_code="ownership_conflict",
            message="The related resource belongs to a different Task",
            recovery_hint="refresh",
        )
    if isinstance(error, TaskManagementConstraintError):
        return _application_error(
            reference,
            error_code="constraint_violation",
            message=(
                "The requested Task Management change violates a business constraint"
            ),
            recovery_hint="refresh",
        )
    if isinstance(error, TaskManagementPersistenceError):
        return _application_error(
            reference,
            error_code="persistence_error",
            message="Task Management persistence is unavailable",
            retryability=True,
            recovery_hint="retry_later",
        )
    if isinstance(error, ValueError):
        return _application_error(
            reference,
            error_code="invalid_request",
            message="The Task Management input is invalid",
            recovery_hint="correct_input",
        )
    if isinstance(error, ProjectError):
        return _application_error(
            reference,
            error_code="application_error",
            message="The Task Management operation could not be completed",
            recovery_hint="refresh",
        )
    raise error


class TaskManagementApplicationService(TaskManagementApplication):
    """Concrete application service with one fresh UoW per operation."""

    def __init__(self, uow_factory: TaskManagementUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def _write(
        self,
        reference: TaskManagementResourceReference,
        operation: Callable[[TaskManagementUnitOfWork], _ResultT],
    ) -> _ResultT:
        try:
            with self._uow_factory() as uow:
                result = operation(uow)
                uow.commit()
                return result
        except TaskManagementError:
            raise
        except (
            ProjectError,
            InvalidTransitionError,
            OwnershipError,
            RevisionConflictError,
            ValueError,
        ) as error:
            raise _translate(error, reference) from error

    def _read(
        self,
        reference: TaskManagementResourceReference,
        operation: Callable[[TaskManagementUnitOfWork], _ResultT],
    ) -> _ResultT:
        try:
            with self._uow_factory() as uow:
                # A query intentionally does not commit.  The UoW context
                # rolls back/cleans up its read transaction on exit.
                return operation(uow)
        except TaskManagementError:
            raise
        except (
            ProjectError,
            InvalidTransitionError,
            OwnershipError,
            RevisionConflictError,
            ValueError,
        ) as error:
            raise _translate(error, reference) from error

    def create_draft_task(self, command: CreateDraftTask) -> TaskSnapshot:
        """Persist a draft Task and return its immutable public snapshot."""

        def operation(uow: TaskManagementUnitOfWork) -> TaskSnapshot:
            if uow.tasks.get(command.task_id) is not None:
                _already_exists(_task_reference(command.task_id), "task")
            task = Task.create(
                command.task_id,
                task_name=command.task_name,
                product_category=command.product_category,
                promotion_goal=command.promotion_goal,
                updated_at=command.updated_at,
            )
            uow.tasks.add(task)
            return task_to_snapshot(task)

        return self._write(_task_reference(command.task_id), operation)

    def get_task(self, query: GetTask) -> TaskSnapshot:
        """Read a Task snapshot without creating a business write."""

        def operation(uow: TaskManagementUnitOfWork) -> TaskSnapshot:
            task = uow.tasks.get(query.task_id)
            if task is None:
                _not_found(_task_reference(query.task_id), "task")
            return task_to_snapshot(task)

        return self._read(_task_reference(query.task_id), operation)

    def get_run(self, query: GetRun) -> RunSnapshot:
        """Read a Run snapshot without creating a business write."""

        def operation(uow: TaskManagementUnitOfWork) -> RunSnapshot:
            run = uow.runs.get(query.run_id)
            if run is None:
                _not_found(_run_reference(query.run_id), "run")
            return run_to_snapshot(run)

        return self._read(_run_reference(query.run_id), operation)

    def get_stage(self, query: GetStage) -> StageSnapshot:
        """Read a Task-scoped Stage snapshot without a write."""

        def operation(uow: TaskManagementUnitOfWork) -> StageSnapshot:
            stage = uow.stages.get(query.task_id, query.stage)
            if stage is None:
                _not_found(_stage_reference(query.task_id, query.stage), "stage")
            return stage_to_snapshot(stage)

        return self._read(_stage_reference(query.task_id, query.stage), operation)

    def prepare_initial_run(
        self, command: PrepareInitialRun
    ) -> PrepareInitialRunResult:
        """Prepare Current Truth after input-gate/dispatch coordination.

        The caller owns the accepted Fact Stage input gate and durable
        dispatch work.  This primitive only stores the Task/Run/Stage state;
        it does not validate Source input or create a WorkIntent/Receipt.
        """

        def operation(uow: TaskManagementUnitOfWork) -> PrepareInitialRunResult:
            task = uow.tasks.get(command.task_id)
            if task is None:
                _not_found(_task_reference(command.task_id), "task")

            # Evaluate the protected Task revision before checking identities;
            # a genuinely stale command is always reported as a CAS conflict.
            started_task = task.start(
                command.run_id,
                expected_revision=command.expected_revision,
                updated_at=command.updated_at,
            )
            moved_task = started_task.move_to_stage(
                StageReference.PRODUCT_INTAKE_AND_FACT_EXTRACTION,
                expected_revision=started_task.revision,
                updated_at=command.updated_at,
            )
            if uow.runs.get(command.run_id) is not None:
                _already_exists(_run_reference(command.run_id), "run")
            stage_reference = StageReference.PRODUCT_INTAKE_AND_FACT_EXTRACTION
            if uow.stages.get(command.task_id, stage_reference) is not None:
                _already_exists(
                    _stage_reference(command.task_id, stage_reference), "stage"
                )

            run = Run.create(
                command.run_id,
                command.task_id,
                current_stage=stage_reference,
                updated_at=command.updated_at,
            )
            stage = Stage.create(
                command.task_id,
                stage_reference,
                updated_at=command.updated_at,
            ).prepare(
                expected_revision=Revision.initial(),
                updated_at=command.updated_at,
            )

            # Stage must precede Run because Run.current_stage is an immediate
            # PostgreSQL foreign key. Task's pointers follow both rows; a
            # failed final CAS rolls all three writes back in this UoW.
            uow.stages.add(stage)
            uow.runs.add(run)
            uow.tasks.save(moved_task, expected_revision=command.expected_revision)
            return PrepareInitialRunResult(
                task=task_to_snapshot(moved_task),
                run=run_to_snapshot(run),
                stage=stage_to_snapshot(stage),
            )

        return self._write(_task_reference(command.task_id), operation)


__all__ = ["TaskManagementApplicationService"]
