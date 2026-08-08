"""Typed SQLAlchemy Core repositories with Unit-of-Work-owned transactions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy import CursorResult, Executable, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ai_ecommerce_agent.modules.task_management.application.errors import (
    TaskManagementConstraintError,
    TaskManagementOwnershipError,
    TaskManagementPersistenceError,
    TaskManagementRevisionConflictError,
)
from ai_ecommerce_agent.modules.task_management.domain import (
    Run,
    Stage,
    StageReference,
    Task,
)
from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

from .mappings import (
    run_domain_to_row,
    run_row_to_domain,
    stage_domain_to_row,
    stage_row_to_domain,
    task_domain_to_row,
    task_row_to_domain,
)
from .tables import RUNS_TABLE, STAGES_TABLE, TASKS_TABLE

_OWNER_CONSTRAINTS = frozenset(
    {
        "fk_task_management_runs_task_owner",
        "fk_task_management_runs_source_owner",
        "fk_task_management_runs_current_stage_owner",
        "fk_task_management_stages_task_owner",
        "fk_task_management_stages_last_run_owner",
        "fk_task_management_tasks_current_stage_owner",
        "fk_task_management_tasks_active_run_owner",
        "fk_task_management_tasks_latest_run_owner",
    }
)


def _constraint_name(error: IntegrityError) -> str | None:
    diagnostic = getattr(error.orig, "diag", None)
    name = getattr(diagnostic, "constraint_name", None)
    return name if isinstance(name, str) and name else None


def _translate(
    error: IntegrityError,
) -> TaskManagementConstraintError | TaskManagementOwnershipError:
    name = _constraint_name(error)
    if name in _OWNER_CONSTRAINTS:
        return TaskManagementOwnershipError(
            resource="task_management_relationship", constraint_name=name
        )
    return TaskManagementConstraintError(constraint_name=name)


def _execute(session: Session, statement: Executable) -> CursorResult[Any]:
    """Execute without taking transaction lifecycle ownership.

    This is the single ORM boundary for both reads and writes.  Named
    integrity failures retain their domain-specific mapping; every other
    SQLAlchemy failure becomes the stable module persistence error.
    """

    try:
        return cast(CursorResult[Any], session.execute(statement))
    except IntegrityError as error:
        raise _translate(error) from error
    except SQLAlchemyError as error:
        raise TaskManagementPersistenceError() from error


def _write(session: Session, statement: Executable) -> CursorResult[Any]:
    """Execute a write through the shared adapter error boundary."""

    return _execute(session, statement)


def _mapping(row: object) -> Mapping[str, object]:
    return cast(Mapping[str, object], row)


class TaskManagementPostgresTaskRepository:
    """Typed Task repository bound to one private UoW Session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, task_id: TaskId) -> Task | None:
        row = (
            _execute(
                self._session,
                select(TASKS_TABLE).where(TASKS_TABLE.c.task_id == str(task_id)),
            )
            .mappings()
            .one_or_none()
        )
        return task_row_to_domain(_mapping(row)) if row is not None else None

    def add(self, task: Task) -> None:
        _write(self._session, insert(TASKS_TABLE).values(task_domain_to_row(task)))

    def save(self, task: Task, *, expected_revision: Revision) -> None:
        values = task_domain_to_row(task)
        values.pop("task_id")
        result = _write(
            self._session,
            update(TASKS_TABLE)
            .where(TASKS_TABLE.c.task_id == str(task.task_id))
            .where(TASKS_TABLE.c.revision == expected_revision.value)
            .values(values),
        )
        if result.rowcount != 1:
            raise TaskManagementRevisionConflictError(
                resource="task", expected_revision=expected_revision.value
            )


class TaskManagementPostgresRunRepository:
    """Typed Run repository bound to one private UoW Session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, run_id: RunId) -> Run | None:
        row = (
            _execute(
                self._session,
                select(RUNS_TABLE).where(RUNS_TABLE.c.run_id == str(run_id)),
            )
            .mappings()
            .one_or_none()
        )
        return run_row_to_domain(_mapping(row)) if row is not None else None

    def add(self, run: Run) -> None:
        _write(self._session, insert(RUNS_TABLE).values(run_domain_to_row(run)))

    def save(self, run: Run, *, expected_revision: Revision) -> None:
        values = run_domain_to_row(run)
        values.pop("run_id")
        result = _write(
            self._session,
            update(RUNS_TABLE)
            .where(RUNS_TABLE.c.run_id == str(run.run_id))
            .where(RUNS_TABLE.c.revision == expected_revision.value)
            .values(values),
        )
        if result.rowcount != 1:
            raise TaskManagementRevisionConflictError(
                resource="run", expected_revision=expected_revision.value
            )


class TaskManagementPostgresStageRepository:
    """Typed Stage repository bound to one private UoW Session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, task_id: TaskId, stage: StageReference) -> Stage | None:
        row = (
            _execute(
                self._session,
                select(STAGES_TABLE)
                .where(STAGES_TABLE.c.task_id == str(task_id))
                .where(STAGES_TABLE.c.stage == stage.value),
            )
            .mappings()
            .one_or_none()
        )
        return stage_row_to_domain(_mapping(row)) if row is not None else None

    def add(self, stage: Stage) -> None:
        _write(self._session, insert(STAGES_TABLE).values(stage_domain_to_row(stage)))

    def save(self, stage: Stage, *, expected_revision: Revision) -> None:
        values = stage_domain_to_row(stage)
        values.pop("task_id")
        values.pop("stage")
        result = _write(
            self._session,
            update(STAGES_TABLE)
            .where(STAGES_TABLE.c.task_id == str(stage.task_id))
            .where(STAGES_TABLE.c.stage == stage.stage.value)
            .where(STAGES_TABLE.c.revision == expected_revision.value)
            .values(values),
        )
        if result.rowcount != 1:
            raise TaskManagementRevisionConflictError(
                resource="stage", expected_revision=expected_revision.value
            )


__all__ = [
    "TaskManagementPostgresRunRepository",
    "TaskManagementPostgresStageRepository",
    "TaskManagementPostgresTaskRepository",
]
