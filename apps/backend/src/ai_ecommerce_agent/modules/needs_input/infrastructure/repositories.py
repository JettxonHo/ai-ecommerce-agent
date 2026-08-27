"""Parameterized SQL repository for the migration-owned request table."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy import CursorResult, Executable, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

from ..application.errors import (
    NeedsInputPersistenceError,
    NeedsInputRevisionPersistenceError,
)
from ..application.ports import NeedsInputRequestRepository
from ..domain.snapshots import NeedsInputActionRequestSnapshot, NeedsInputStatus
from .mappings import request_row_to_snapshot, request_snapshot_to_row
from .tables import NEEDS_INPUT_REQUESTS_TABLE


def _mapping(row: object) -> Mapping[str, object]:
    return cast(Mapping[str, object], row)


def _execute(session: Session, statement: Executable) -> CursorResult[Any]:
    try:
        return cast(CursorResult[Any], session.execute(statement))
    except (IntegrityError, SQLAlchemyError) as error:
        raise NeedsInputPersistenceError() from error


class NeedsInputPostgresRequestRepository(NeedsInputRequestRepository):
    """Bounded current lookup plus immutable history read by identity."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, action_request_id: str) -> NeedsInputActionRequestSnapshot | None:
        row = (
            _execute(
                self._session,
                select(NEEDS_INPUT_REQUESTS_TABLE).where(
                    NEEDS_INPUT_REQUESTS_TABLE.c.action_request_id == action_request_id
                ),
            )
            .mappings()
            .one_or_none()
        )
        return request_row_to_snapshot(_mapping(row)) if row is not None else None

    def get_current(self, task_id: TaskId) -> NeedsInputActionRequestSnapshot | None:
        row = (
            _execute(
                self._session,
                select(NEEDS_INPUT_REQUESTS_TABLE)
                .where(NEEDS_INPUT_REQUESTS_TABLE.c.task_id == str(task_id))
                .where(
                    NEEDS_INPUT_REQUESTS_TABLE.c.status == NeedsInputStatus.OPEN.value
                )
                .order_by(NEEDS_INPUT_REQUESTS_TABLE.c.updated_at.desc())
                .limit(1),
            )
            .mappings()
            .one_or_none()
        )
        return request_row_to_snapshot(_mapping(row)) if row is not None else None

    def add(self, request: NeedsInputActionRequestSnapshot) -> None:
        _execute(
            self._session,
            insert(NEEDS_INPUT_REQUESTS_TABLE).values(request_snapshot_to_row(request)),
        )

    def save(
        self,
        request: NeedsInputActionRequestSnapshot,
        *,
        expected_revision: Revision,
    ) -> None:
        values = request_snapshot_to_row(request)
        values.pop("action_request_id")
        values.pop("task_id")
        result = _execute(
            self._session,
            update(NEEDS_INPUT_REQUESTS_TABLE)
            .where(
                NEEDS_INPUT_REQUESTS_TABLE.c.action_request_id
                == request.action_request_id
            )
            .where(NEEDS_INPUT_REQUESTS_TABLE.c.revision == expected_revision.value)
            .values(values),
        )
        if result.rowcount != 1:
            raise NeedsInputRevisionPersistenceError()


__all__ = ["NeedsInputPostgresRequestRepository"]
