"""SQLAlchemy Core repository for the current Task primary input."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy import CursorResult, Executable, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

from ..application.primary_input_errors import (
    PrimaryInputConstraintError,
    PrimaryInputOwnershipError,
    PrimaryInputPersistenceError,
    PrimaryInputRevisionConflictError,
)
from ..domain import TaskPrimaryInput
from .mappings import primary_input_domain_to_row, primary_input_row_to_domain
from .tables import TASK_PRIMARY_INPUTS_TABLE


def _constraint_name(error: IntegrityError) -> str | None:
    diagnostic = getattr(error.orig, "diag", None)
    name = getattr(diagnostic, "constraint_name", None)
    return name if isinstance(name, str) and name else None


def _execute(session: Session, statement: Executable) -> CursorResult[Any]:
    try:
        return cast(CursorResult[Any], session.execute(statement))
    except IntegrityError as error:
        name = _constraint_name(error)
        if name == "fk_source_evidence_task_primary_inputs_task_owner":
            raise PrimaryInputOwnershipError() from error
        raise PrimaryInputConstraintError() from error
    except SQLAlchemyError as error:
        raise PrimaryInputPersistenceError() from error


def _mapping(row: object) -> Mapping[str, object]:
    return cast(Mapping[str, object], row)


class PrimaryInputPostgresRepository:
    """Repository bound to one private transaction Session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, task_id: TaskId) -> TaskPrimaryInput | None:
        row = (
            _execute(
                self._session,
                select(TASK_PRIMARY_INPUTS_TABLE).where(
                    TASK_PRIMARY_INPUTS_TABLE.c.task_id == str(task_id)
                ),
            )
            .mappings()
            .one_or_none()
        )
        return primary_input_row_to_domain(_mapping(row)) if row is not None else None

    def add(self, value: TaskPrimaryInput) -> None:
        _execute(
            self._session,
            insert(TASK_PRIMARY_INPUTS_TABLE).values(
                primary_input_domain_to_row(value)
            ),
        )

    def save(self, value: TaskPrimaryInput, *, expected_revision: Revision) -> None:
        values = primary_input_domain_to_row(value)
        values.pop("task_id")
        result = _execute(
            self._session,
            update(TASK_PRIMARY_INPUTS_TABLE)
            .where(TASK_PRIMARY_INPUTS_TABLE.c.task_id == str(value.task_id))
            .where(TASK_PRIMARY_INPUTS_TABLE.c.revision == expected_revision.value)
            .values(values),
        )
        if result.rowcount != 1:
            raise PrimaryInputRevisionConflictError(expected_revision=expected_revision)


__all__ = ["PrimaryInputPostgresRepository"]
