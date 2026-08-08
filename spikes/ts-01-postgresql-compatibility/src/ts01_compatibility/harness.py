"""Small synchronous PostgreSQL harness for TS-01 invariants.

The harness deliberately exposes only test-sized operations. Claim and commit
each use a short database transaction; a caller receives a value object and
performs any simulated external work after the transaction has ended.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import cast

from sqlalchemy import Engine, and_, create_engine, delete, func, insert, or_, select, text, update
from sqlalchemy.engine import Connection, RowMapping
from sqlalchemy.pool import QueuePool

from ts01_compatibility.schema import SCHEMA_NAME, current_truth, work_intents

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://mvp0_business:mvp0_business_local_only@127.0.0.1:55432/ecommerce_business"
)


class FencingRejected(RuntimeError):
    """Raised when a stale holder/token cannot commit Current Truth."""


class CommitInjectedFailure(RuntimeError):
    """Raised by the representative rollback fault window."""


@dataclass(frozen=True, slots=True)
class WorkClaim:
    """Persisted claim identity returned after the claim transaction commits."""

    work_item_id: str
    holder_id: str
    fencing_token: int
    lease_expires_at: datetime


def database_url_from_environment() -> str:
    """Return the configured URL, defaulting to the MVP0 local Business DB."""

    url = os.environ.get("TS01_DATABASE_URL", DEFAULT_DATABASE_URL)
    if not url.startswith("postgresql+psycopg://"):
        raise ValueError("TS01_DATABASE_URL must use the synchronous postgresql+psycopg dialect")
    return url


def create_database_engine(database_url: str | None = None) -> Engine:
    """Create the synchronous SQLAlchemy engine used only by this spike."""

    url = database_url or database_url_from_environment()
    if not url.startswith("postgresql+psycopg://"):
        raise ValueError("TS-01 requires a postgresql+psycopg URL; SQLite is not accepted")
    return create_engine(
        url,
        poolclass=QueuePool,
        pool_pre_ping=True,
        isolation_level="READ COMMITTED",
    )


class PostgresCompatibilityHarness:
    """Test-only claim, fencing and atomic Current Truth operations."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def clear_fixture_rows(self) -> None:
        """Remove only rows owned by this dedicated test schema."""

        with self.engine.begin() as connection:
            connection.execute(delete(current_truth))
            connection.execute(delete(work_intents))

    def claim(
        self,
        holder_id: str,
        *,
        lease_seconds: int = 30,
        before_commit: Callable[[Connection], None] | None = None,
    ) -> WorkClaim | None:
        """Claim one available/expired work item using a short transaction.

        ``before_commit`` is a deterministic test hook used only to hold the
        row lock while a second connection polls. Normal callers leave it
        unset, so the transaction commits before external work begins.
        """

        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        with self.engine.connect() as connection:
            with connection.begin():
                row = (
                    connection.execute(
                        select(
                            work_intents.c.id,
                            work_intents.c.fencing_token,
                        )
                        .where(
                            or_(
                                work_intents.c.status == "available",
                                and_(
                                    work_intents.c.status == "claimed",
                                    work_intents.c.lease_expires_at <= func.now(),
                                ),
                            )
                        )
                        .order_by(work_intents.c.id)
                        .limit(1)
                        .with_for_update(skip_locked=True)
                    )
                    .mappings()
                    .first()
                )
                if row is None:
                    return None

                work_item_id = cast(str, row["id"])
                fencing_token = cast(int, row["fencing_token"]) + 1
                lease_expires_at = datetime.now(UTC) + timedelta(seconds=lease_seconds)
                result = connection.execute(
                    update(work_intents)
                    .where(work_intents.c.id == work_item_id)
                    .values(
                        status="claimed",
                        holder_id=holder_id,
                        lease_expires_at=lease_expires_at,
                        fencing_token=fencing_token,
                    )
                )
                if result.rowcount != 1:
                    raise RuntimeError("TS-01 claim update changed an unexpected number of rows")
                if before_commit is not None:
                    before_commit(connection)

            return WorkClaim(work_item_id, holder_id, fencing_token, lease_expires_at)

    def expire_lease(self, claim: WorkClaim) -> None:
        """Make a claim eligible for deterministic takeover without sleeping."""

        expired_at = datetime.now(UTC) - timedelta(seconds=1)
        with self.engine.begin() as connection:
            result = connection.execute(
                update(work_intents)
                .where(
                    work_intents.c.id == claim.work_item_id,
                    work_intents.c.holder_id == claim.holder_id,
                    work_intents.c.fencing_token == claim.fencing_token,
                )
                .values(lease_expires_at=expired_at)
            )
            if result.rowcount != 1:
                raise FencingRejected("cannot expire a claim that is no longer current")

    def commit_current_truth(
        self,
        claim: WorkClaim,
        value: str,
        *,
        revision: int = 1,
        inject_failure_after_write: bool = False,
    ) -> None:
        """Atomically fence a claim and write one Current Truth row.

        The optional fault injection raises after both SQL writes have been
        issued; the surrounding transaction must roll them back together.
        """

        if revision <= 0:
            raise ValueError("revision must be positive")
        with self.engine.connect() as connection:
            with connection.begin():
                result = connection.execute(
                    update(work_intents)
                    .where(
                        work_intents.c.id == claim.work_item_id,
                        work_intents.c.status == "claimed",
                        work_intents.c.holder_id == claim.holder_id,
                        work_intents.c.fencing_token == claim.fencing_token,
                        work_intents.c.lease_expires_at > func.now(),
                    )
                    .values(status="completed")
                )
                if result.rowcount != 1:
                    raise FencingRejected(f"stale holder/token rejected for {claim.work_item_id}")

                connection.execute(
                    insert(current_truth).values(
                        work_intent_id=claim.work_item_id,
                        value=value,
                        revision=revision,
                        committed_by=claim.holder_id,
                        committed_fencing_token=claim.fencing_token,
                    )
                )
                if inject_failure_after_write:
                    raise CommitInjectedFailure("injected after Current Truth write")

    def read_work_item(self, work_item_id: str) -> RowMapping | None:
        """Read one fixture row after a transaction has completed."""

        with self.engine.connect() as connection:
            row = (
                connection.execute(select(work_intents).where(work_intents.c.id == work_item_id))
                .mappings()
                .first()
            )
            return row

    def read_current_truth(self, work_item_id: str) -> RowMapping | None:
        """Read one Current Truth row after a transaction has completed."""

        with self.engine.connect() as connection:
            row = (
                connection.execute(
                    select(current_truth).where(current_truth.c.work_intent_id == work_item_id)
                )
                .mappings()
                .first()
            )
            return row

    def checked_out_connections(self) -> int:
        """Expose pool state to prove claim/commit return their connections."""

        pool = self.engine.pool
        checkedout = getattr(pool, "checkedout", None)
        if not callable(checkedout):
            raise RuntimeError("TS-01 engine must use a QueuePool")
        return cast(int, checkedout())

    def dedicated_schema_exists(self) -> bool:
        """Check only the dedicated schema; used by migration lifecycle tests."""

        with self.engine.connect() as connection:
            value = connection.execute(
                text("SELECT to_regnamespace(:schema_name)"),
                {"schema_name": SCHEMA_NAME},
            ).scalar_one_or_none()
            return value is not None
