"""SQLAlchemy Core repository for Durable Dispatch Work Intents."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy import CursorResult, Executable, insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchConstraintError,
    DurableDispatchPersistenceError,
    DurableDispatchRevisionConflictError,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.identity import DispatchId
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.shared_kernel import Revision

from .mappings import (
    work_intent_row_to_snapshot,
    work_intent_snapshot_to_insert_row,
    work_intent_snapshot_to_update_values,
)
from .tables import WORK_INTENTS_TABLE


def _constraint_name(error: IntegrityError) -> str | None:
    diagnostic = getattr(error.orig, "diag", None)
    name = getattr(diagnostic, "constraint_name", None)
    return name if isinstance(name, str) and name else None


def _translate_integrity(error: IntegrityError) -> DurableDispatchConstraintError:
    return DurableDispatchConstraintError(constraint_name=_constraint_name(error))


def _execute(session: Session, statement: Executable) -> CursorResult[Any]:
    try:
        return cast(CursorResult[Any], session.execute(statement))
    except IntegrityError as error:
        raise _translate_integrity(error) from error
    except SQLAlchemyError as error:
        raise DurableDispatchPersistenceError() from error


def _fetch_one(session: Session, statement: Executable) -> Mapping[str, object] | None:
    try:
        row = _execute(session, statement).mappings().one_or_none()
    except IntegrityError as error:
        raise _translate_integrity(error) from error
    except SQLAlchemyError as error:
        raise DurableDispatchPersistenceError() from error
    return cast(Mapping[str, object] | None, row)


class DurableDispatchPostgresWorkIntentRepository:
    """Typed Work Intent repository that never owns transaction lifecycle."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, dispatch_id: DispatchId) -> WorkIntentSnapshot | None:
        row = _fetch_one(
            self._session,
            select(WORK_INTENTS_TABLE).where(
                WORK_INTENTS_TABLE.c.dispatch_id == dispatch_id.value
            ),
        )
        return work_intent_row_to_snapshot(row) if row is not None else None

    def add(self, snapshot: WorkIntentSnapshot) -> None:
        _execute(
            self._session,
            insert(WORK_INTENTS_TABLE).values(
                work_intent_snapshot_to_insert_row(snapshot)
            ),
        )

    def save(
        self,
        snapshot: WorkIntentSnapshot,
        *,
        expected_revision: Revision,
    ) -> None:
        result = _execute(
            self._session,
            update(WORK_INTENTS_TABLE)
            .where(
                WORK_INTENTS_TABLE.c.dispatch_id == snapshot.envelope.dispatch_id.value
            )
            .where(WORK_INTENTS_TABLE.c.revision == expected_revision.value)
            .values(work_intent_snapshot_to_update_values(snapshot)),
        )
        if result.rowcount != 1:
            raise DurableDispatchRevisionConflictError(
                dispatch_id=snapshot.envelope.dispatch_id.value,
                expected_revision=expected_revision,
            )


__all__ = ["DurableDispatchPostgresWorkIntentRepository"]
