"""Private PostgreSQL claim and heartbeat repository for Work Intent leases."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

from sqlalchemy import Executable, and_, or_, select, update
from sqlalchemy.orm import Session

from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchRevisionConflictError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_commands import (
    ClaimNextWorkIntent,
    HeartbeatWorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.identity import FencingToken
from ai_ecommerce_agent.modules.durable_dispatch.domain.ownership import WorkIntentLease
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import WorkIntentStatus

from .mappings import (
    work_intent_row_to_snapshot,
    work_intent_snapshot_to_update_values,
)
from .repositories import _fetch_one  # pyright: ignore[reportPrivateUsage]
from .tables import WORK_INTENTS_TABLE


class DurableDispatchPostgresWorkIntentLeaseRepository:
    """Claim and heartbeat one Work Intent without owning its transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def claim_next(self, command: ClaimNextWorkIntent) -> WorkIntentSnapshot | None:
        """Claim the first eligible row using a non-blocking row lock."""

        row = _fetch_one(self._session, self._claim_statement(command))
        if row is None:
            return None

        current = work_intent_row_to_snapshot(row)
        raw_token = FencingToken(cast(int, row["fencing_token"]))
        if current.current_lease is None:
            claimed_lease = WorkIntentLease(
                current.envelope.dispatch_id,
                command.delivery_attempt_id,
                command.holder_id,
                raw_token.next(),
                command.lease_expires_at,
            )
        else:
            claimed_lease = replace(
                current.current_lease,
                delivery_attempt_id=command.delivery_attempt_id,
                holder_id=command.holder_id,
                fencing_token=raw_token.next(),
                lease_expires_at=command.lease_expires_at,
            )
        claimed = replace(
            current,
            status=WorkIntentStatus.LEASED,
            revision=current.revision.next(),
            current_lease=claimed_lease,
        )
        updated = _fetch_one(
            self._session,
            update(WORK_INTENTS_TABLE)
            .where(
                WORK_INTENTS_TABLE.c.dispatch_id == current.envelope.dispatch_id.value
            )
            .where(WORK_INTENTS_TABLE.c.revision == current.revision.value)
            .values(work_intent_snapshot_to_update_values(claimed))
            .returning(*WORK_INTENTS_TABLE.c),
        )
        if updated is None:
            raise DurableDispatchRevisionConflictError(
                dispatch_id=current.envelope.dispatch_id.value,
                expected_revision=current.revision,
            )
        return work_intent_row_to_snapshot(updated)

    def heartbeat(self, command: HeartbeatWorkIntentLease) -> WorkIntentSnapshot | None:
        """Extend one currently-owned, unexpired lease by one revision."""

        columns = WORK_INTENTS_TABLE.c
        updated = _fetch_one(
            self._session,
            update(WORK_INTENTS_TABLE)
            .where(columns.dispatch_id == command.dispatch_id.value)
            .where(columns.revision == command.expected_revision.value)
            .where(
                columns.status.in_(
                    (
                        WorkIntentStatus.LEASED.value,
                        WorkIntentStatus.IN_PROGRESS.value,
                    )
                )
            )
            .where(columns.delivery_attempt_id == command.delivery_attempt_id.value)
            .where(columns.lease_holder_id == command.holder_id.value)
            .where(columns.fencing_token == command.fencing_token.value)
            .where(columns.delivery_attempt_id.is_not(None))
            .where(columns.lease_holder_id.is_not(None))
            .where(columns.lease_expires_at.is_not(None))
            .where(columns.lease_expires_at > command.now)
            .where(columns.lease_expires_at < command.lease_expires_at)
            .values(
                revision=command.expected_revision.value + 1,
                lease_expires_at=command.lease_expires_at,
            )
            .returning(*WORK_INTENTS_TABLE.c),
        )
        return work_intent_row_to_snapshot(updated) if updated is not None else None

    def _claim_statement(self, command: ClaimNextWorkIntent) -> Executable:
        columns = WORK_INTENTS_TABLE.c
        fresh = and_(
            columns.status == WorkIntentStatus.AVAILABLE.value,
            columns.available_at <= command.now,
            columns.delivery_attempt_id.is_(None),
            columns.lease_holder_id.is_(None),
            columns.lease_expires_at.is_(None),
        )
        takeover = and_(
            columns.status.in_(
                (
                    WorkIntentStatus.LEASED.value,
                    WorkIntentStatus.IN_PROGRESS.value,
                )
            ),
            columns.delivery_attempt_id.is_not(None),
            columns.lease_holder_id.is_not(None),
            columns.lease_expires_at.is_not(None),
            columns.lease_expires_at <= command.now,
        )
        return (
            select(WORK_INTENTS_TABLE)
            .where(columns.cancellation_requested.is_(False))
            .where(columns.superseded_by_dispatch_id.is_(None))
            .where(or_(fresh, takeover))
            .order_by(
                columns.available_at,
                columns.created_at,
                columns.dispatch_id,
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        )


__all__ = ["DurableDispatchPostgresWorkIntentLeaseRepository"]
