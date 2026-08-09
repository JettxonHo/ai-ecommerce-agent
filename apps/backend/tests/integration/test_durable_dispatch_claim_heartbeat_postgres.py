"""Opt-in PostgreSQL acceptance for atomic Durable Dispatch ownership."""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.modules.durable_dispatch.application.lease_commands import (
    ClaimNextWorkIntent,
    HeartbeatWorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.envelope import (
    WorkIntentEnvelope,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.identity import (
    DeliveryAttemptId,
    DispatchId,
    FencingToken,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.ownership import (
    LeaseHolderId,
    WorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import WorkIntentStatus
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure.uow import (
    DurableDispatchPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
)

pytestmark = [pytest.mark.integration, pytest.mark.live]

if os.environ.get("MVP0_RUN_DURABLE_DISPATCH_CLAIM_HEARTBEAT_POSTGRES") != "1":
    pytest.skip(
        "set MVP0_RUN_DURABLE_DISPATCH_CLAIM_HEARTBEAT_POSTGRES=1 for the opt-in "
        "claim/heartbeat PostgreSQL suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_018k_durable_dispatch"
URL_ENV = "MVP0_DURABLE_DISPATCH_DATABASE_URL"
DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)


def _database_url() -> str:
    return os.environ.get(URL_ENV, DEFAULT_URL).strip()


def _alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", SCHEMA)
    config.set_main_option("version_table_schema", SCHEMA)
    return config


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    database_url = _database_url()
    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=database_url,
            pool_size=4,
            max_overflow=0,
            pool_timeout=3,
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))
    try:
        command.upgrade(_alembic_config(database_url), "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        engine.dispose()


def _factory(engine: Engine) -> DurableDispatchPostgresUnitOfWorkFactory:
    return DurableDispatchPostgresUnitOfWorkFactory.from_engine(engine, schema=SCHEMA)


_BASE_TIME = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)


def _snapshot(
    suffix: str,
    *,
    status: WorkIntentStatus = WorkIntentStatus.AVAILABLE,
    revision: int = 0,
    lease: WorkIntentLease | None = None,
    cancellation_requested: bool = False,
    created_at: datetime = _BASE_TIME,
    available_at: datetime = _BASE_TIME,
) -> WorkIntentSnapshot:
    dispatch_id = DispatchId(f"dispatch-{suffix}")
    return WorkIntentSnapshot(
        WorkIntentEnvelope(
            dispatch_id,
            "process_source",
            "source_processing",
            ResourceReference("task", f"task-{suffix}"),
            f"command-{suffix}",
            RunId(f"run-{suffix}"),
            f"fingerprint-{suffix}",
            "schema-1",
            DomainVersionId(f"domain-version-{suffix}"),
            Revision(2),
            ResourceReference("source_version", f"source-version-{suffix}"),
            None,
            f"ordering-{suffix}",
            created_at,
            available_at,
        ),
        status,
        Revision(revision),
        cancellation_requested,
        lease,
    )


def _leased_snapshot(
    suffix: str,
    *,
    token: int,
    status: WorkIntentStatus = WorkIntentStatus.LEASED,
    revision: int = 0,
    expires_at: datetime = _BASE_TIME + timedelta(hours=1),
) -> WorkIntentSnapshot:
    dispatch_id = DispatchId(f"dispatch-{suffix}")
    lease = WorkIntentLease(
        dispatch_id,
        DeliveryAttemptId(f"attempt-{suffix}"),
        LeaseHolderId(f"holder-{suffix}"),
        FencingToken(token),
        expires_at,
    )
    return _snapshot(
        suffix,
        status=status,
        revision=revision,
        lease=lease,
    )


def _claim(
    suffix: str,
    *,
    now: datetime = _BASE_TIME + timedelta(minutes=30),
    expires_at: datetime = _BASE_TIME + timedelta(hours=2),
) -> ClaimNextWorkIntent:
    return ClaimNextWorkIntent(
        LeaseHolderId(f"new-holder-{suffix}"),
        DeliveryAttemptId(f"new-attempt-{suffix}"),
        now,
        expires_at,
    )


def _heartbeat(
    snapshot: WorkIntentSnapshot,
    *,
    now: datetime = _BASE_TIME + timedelta(minutes=30),
    expires_at: datetime = _BASE_TIME + timedelta(hours=2),
    holder_id: LeaseHolderId | None = None,
    delivery_attempt_id: DeliveryAttemptId | None = None,
    fencing_token: FencingToken | None = None,
    expected_revision: Revision | None = None,
) -> HeartbeatWorkIntentLease:
    assert snapshot.current_lease is not None
    lease = snapshot.current_lease
    return HeartbeatWorkIntentLease(
        snapshot.envelope.dispatch_id,
        delivery_attempt_id or lease.delivery_attempt_id,
        holder_id or lease.holder_id,
        fencing_token or lease.fencing_token,
        expected_revision or snapshot.revision,
        now,
        expires_at,
    )


def _raw_row(engine: Engine, dispatch_id: DispatchId) -> dict[str, object]:
    with engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    f'SELECT * FROM "{SCHEMA}"."durable_dispatch_work_intents" '
                    "WHERE dispatch_id = :dispatch_id"
                ),
                {"dispatch_id": dispatch_id.value},
            )
            .mappings()
            .one()
        )
    return dict(row)


def _seed(
    factory: DurableDispatchPostgresUnitOfWorkFactory,
    *snapshots: WorkIntentSnapshot,
) -> None:
    with factory() as uow:
        for snapshot in snapshots:
            uow.work_intents.add(snapshot)
        uow.commit()


def test_two_independent_claims_skip_locked_without_double_ownership(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    initial = _snapshot("lock")
    _seed(factory, initial)

    first, second = factory(), factory()
    with first as left:
        claimed = left.work_intent_leases.claim_next(_claim("first"))
        assert claimed is not None
        assert claimed.current_lease is not None
        assert claimed.current_lease.holder_id == LeaseHolderId("new-holder-first")

        with second as right:
            right._session.execute(  # pyright: ignore[reportPrivateUsage]
                text("SET LOCAL lock_timeout = '250ms'")
            )
            assert right.work_intent_leases.claim_next(_claim("second")) is None
            right.commit()
        left.commit()

    with factory() as uow:
        current = uow.work_intents.get(initial.envelope.dispatch_id)
        assert current is not None
        assert current.status is WorkIntentStatus.LEASED
        assert current.current_lease is not None
        assert current.current_lease.holder_id == LeaseHolderId("new-holder-first")
        uow.commit()


def test_independent_claims_follow_available_created_dispatch_order(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    created_first = _snapshot(
        "order-created-first",
        created_at=_BASE_TIME - timedelta(minutes=2),
        available_at=_BASE_TIME,
    )
    created_second = _snapshot(
        "order-created-second",
        created_at=_BASE_TIME - timedelta(minutes=1),
        available_at=_BASE_TIME,
    )
    dispatch_first = _snapshot(
        "order-dispatch-a",
        created_at=_BASE_TIME,
        available_at=_BASE_TIME + timedelta(minutes=1),
    )
    dispatch_second = _snapshot(
        "order-dispatch-b",
        created_at=_BASE_TIME,
        available_at=_BASE_TIME + timedelta(minutes=1),
    )
    _seed(factory, dispatch_second, created_second, dispatch_first, created_first)

    expected = (
        created_first.envelope.dispatch_id,
        created_second.envelope.dispatch_id,
        dispatch_first.envelope.dispatch_id,
        dispatch_second.envelope.dispatch_id,
    )
    for index, dispatch_id in enumerate(expected):
        with factory() as uow:
            claimed = uow.work_intent_leases.claim_next(_claim(f"order-{index}"))
            assert claimed is not None
            assert claimed.envelope.dispatch_id == dispatch_id
            uow.commit()


def test_unexpired_owned_row_is_not_claimable_after_expired_takeovers(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    unexpired = _leased_snapshot(
        "still-owned-only",
        token=9,
        status=WorkIntentStatus.IN_PROGRESS,
        expires_at=_BASE_TIME + timedelta(hours=1),
    )
    _seed(factory, unexpired)

    with factory() as uow:
        assert uow.work_intent_leases.claim_next(_claim("still-owned")) is None
        uow.commit()


def test_fresh_claim_advances_retained_fencing_token_and_uses_caller_ownership(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    leased = _leased_snapshot("retained", token=7)
    _seed(factory, leased)

    with factory() as uow:
        current = uow.work_intents.get(leased.envelope.dispatch_id)
        assert current is not None
        no_lease = replace(
            current,
            status=WorkIntentStatus.AVAILABLE,
            revision=Revision(1),
            current_lease=None,
        )
        uow.work_intents.save(no_lease, expected_revision=Revision(0))
        uow.commit()

    claimed_expected = _claim("retained")
    with factory() as uow:
        claimed = uow.work_intent_leases.claim_next(claimed_expected)
        assert claimed is not None
        assert claimed.revision == Revision(2)
        assert claimed.current_lease is not None
        assert claimed.current_lease.fencing_token == FencingToken(8)
        assert claimed.current_lease.holder_id == claimed_expected.holder_id
        assert (
            claimed.current_lease.delivery_attempt_id
            == claimed_expected.delivery_attempt_id
        )
        assert (
            claimed.current_lease.lease_expires_at == claimed_expected.lease_expires_at
        )
        uow.commit()

    row = _raw_row(postgres_engine, leased.envelope.dispatch_id)
    assert row["fencing_token"] == 8
    assert row["revision"] == 2


def test_expired_leased_and_in_progress_rows_are_taken_over_once(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    expired_leased = _leased_snapshot(
        "expired-leased",
        token=2,
        status=WorkIntentStatus.LEASED,
        expires_at=_BASE_TIME - timedelta(hours=1),
    )
    expired_progress = _leased_snapshot(
        "expired-progress",
        token=4,
        status=WorkIntentStatus.IN_PROGRESS,
        expires_at=_BASE_TIME - timedelta(hours=1),
    )
    current = _leased_snapshot(
        "still-owned",
        token=9,
        status=WorkIntentStatus.LEASED,
        expires_at=_BASE_TIME + timedelta(hours=1),
    )
    _seed(factory, expired_progress, current, expired_leased)

    with factory() as uow:
        first = uow.work_intent_leases.claim_next(_claim("takeover-first"))
        assert first is not None
        assert first.envelope.dispatch_id == expired_leased.envelope.dispatch_id
        assert first.current_lease is not None
        assert first.current_lease.fencing_token == FencingToken(3)
        uow.commit()

    with factory() as uow:
        second = uow.work_intent_leases.claim_next(_claim("takeover-second"))
        assert second is not None
        assert second.envelope.dispatch_id == expired_progress.envelope.dispatch_id
        assert second.current_lease is not None
        assert second.current_lease.fencing_token == FencingToken(5)
        uow.commit()

    with factory() as uow:
        assert uow.work_intent_leases.claim_next(_claim("takeover-third")) is None
        uow.commit()


def test_pending_retryable_terminal_superseded_and_cancelled_rows_are_excluded(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    snapshots = [
        _snapshot("pending", status=WorkIntentStatus.PENDING),
        _snapshot("retryable", status=WorkIntentStatus.FAILED_RETRYABLE),
        _snapshot("terminal", status=WorkIntentStatus.FAILED_TERMINAL),
        _snapshot("succeeded", status=WorkIntentStatus.SUCCEEDED),
        _snapshot("cancelled", status=WorkIntentStatus.CANCELLED),
        _snapshot("superseded", status=WorkIntentStatus.SUPERSEDED),
        _snapshot("cancel-requested", cancellation_requested=True),
        _snapshot(
            "future",
            available_at=_BASE_TIME + timedelta(hours=2),
        ),
        _leased_snapshot(
            "available-with-lease",
            token=2,
            status=WorkIntentStatus.AVAILABLE,
            expires_at=_BASE_TIME - timedelta(hours=1),
        ),
    ]
    _seed(factory, *snapshots)

    with factory() as uow:
        assert uow.work_intent_leases.claim_next(_claim("excluded")) is None
        uow.commit()


def test_heartbeat_extends_only_exactly_owned_unexpired_lease(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    initial = _leased_snapshot("heartbeat", token=5)
    _seed(factory, initial)

    before = _raw_row(postgres_engine, initial.envelope.dispatch_id)
    extension = _heartbeat(initial)
    with factory() as uow:
        updated = uow.work_intent_leases.heartbeat(extension)
        assert updated is not None
        assert updated.revision == Revision(1)
        assert updated.current_lease is not None
        assert updated.current_lease.lease_expires_at == extension.lease_expires_at
        uow.commit()

    baseline = _raw_row(postgres_engine, initial.envelope.dispatch_id)
    expected_after = dict(before)
    expected_after["revision"] = 1
    expected_after["lease_expires_at"] = extension.lease_expires_at
    assert baseline == expected_after
    assert baseline["status"] == WorkIntentStatus.LEASED.value
    assert baseline["fencing_token"] == 5
    assert baseline["delivery_attempt_id"] == "attempt-heartbeat"
    assert baseline["lease_holder_id"] == "holder-heartbeat"

    assert updated is not None
    mismatches = (
        _heartbeat(
            updated,
            holder_id=LeaseHolderId("wrong-holder"),
        ),
        _heartbeat(
            updated,
            delivery_attempt_id=DeliveryAttemptId("wrong-attempt"),
        ),
        _heartbeat(updated, fencing_token=FencingToken(6)),
        _heartbeat(updated, expected_revision=Revision(0)),
        _heartbeat(
            updated,
            now=_BASE_TIME + timedelta(hours=2, minutes=1),
            expires_at=_BASE_TIME + timedelta(hours=3),
        ),
        _heartbeat(
            updated,
            expires_at=_BASE_TIME + timedelta(hours=1, minutes=30),
        ),
    )
    for mismatch in mismatches:
        with factory() as uow:
            assert uow.work_intent_leases.heartbeat(mismatch) is None
            uow.commit()
        assert _raw_row(postgres_engine, initial.envelope.dispatch_id) == baseline


def test_claim_and_heartbeat_rollback_leave_no_partial_ownership_update(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    available = _snapshot("rollback-claim")
    leased = _leased_snapshot("rollback-heartbeat", token=3)
    _seed(factory, available, leased)

    with factory() as uow:
        claimed = uow.work_intent_leases.claim_next(_claim("rollback"))
        assert claimed is not None

    rolled_back_claim = _raw_row(postgres_engine, available.envelope.dispatch_id)
    assert rolled_back_claim["status"] == WorkIntentStatus.AVAILABLE.value
    assert rolled_back_claim["revision"] == 0
    assert rolled_back_claim["fencing_token"] == 0
    assert rolled_back_claim["delivery_attempt_id"] is None
    assert rolled_back_claim["lease_holder_id"] is None
    assert rolled_back_claim["lease_expires_at"] is None

    with factory() as uow:
        updated = uow.work_intent_leases.heartbeat(_heartbeat(leased))
        assert updated is not None

    rolled_back_heartbeat = _raw_row(postgres_engine, leased.envelope.dispatch_id)
    assert rolled_back_heartbeat["revision"] == 0
    assert rolled_back_heartbeat["fencing_token"] == 3
    assert rolled_back_heartbeat["lease_expires_at"] == (
        _BASE_TIME + timedelta(hours=1)
    )
