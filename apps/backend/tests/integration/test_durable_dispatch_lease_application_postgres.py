"""Opt-in PostgreSQL acceptance for the Durable Dispatch lease application."""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.bootstrap.durable_dispatch_postgres import (
    DurableDispatchPostgresComposition,
    compose_durable_dispatch_postgres,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_commands import (
    ClaimNextWorkIntent,
    HeartbeatWorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_errors import (
    DurableDispatchLeaseError,
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

if os.environ.get("MVP0_RUN_DURABLE_DISPATCH_LEASE_APPLICATION_POSTGRES") != "1":
    pytest.skip(
        "set MVP0_RUN_DURABLE_DISPATCH_LEASE_APPLICATION_POSTGRES=1 for the opt-in "
        "Durable Dispatch lease application PostgreSQL suite",
        allow_module_level=True,
    )

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA = "mvp0_018l_lease_application"
_URL_ENV = "MVP0_DURABLE_DISPATCH_DATABASE_URL"
_DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)
_BASE_TIME = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)


def _database_url() -> str:
    return os.environ.get(_URL_ENV, _DEFAULT_URL).strip()


def _alembic_config(database_url: str) -> Config:
    config = Config(str(_BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", _SCHEMA)
    config.set_main_option("version_table_schema", _SCHEMA)
    return config


@pytest.fixture(scope="module")
def composition() -> Iterator[DurableDispatchPostgresComposition]:
    database_url = _database_url()
    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=database_url,
            pool_size=1,
            max_overflow=0,
            pool_timeout=3,
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{_SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{_SCHEMA}"'))
    durable_dispatch: DurableDispatchPostgresComposition | None = None
    try:
        command.upgrade(_alembic_config(database_url), "head")
        durable_dispatch = compose_durable_dispatch_postgres(
            PostgresEngineConfig(
                database_url=database_url,
                pool_size=1,
                max_overflow=0,
                pool_timeout=3,
            ),
            schema=_SCHEMA,
        )
        yield durable_dispatch
    finally:
        if durable_dispatch is not None:
            durable_dispatch.close()
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{_SCHEMA}" CASCADE'))
        engine.dispose()


def _snapshot(
    suffix: str,
    *,
    status: WorkIntentStatus = WorkIntentStatus.AVAILABLE,
    revision: int = 0,
    lease: WorkIntentLease | None = None,
) -> WorkIntentSnapshot:
    return WorkIntentSnapshot(
        WorkIntentEnvelope(
            DispatchId(f"dispatch-{suffix}"),
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
            _BASE_TIME,
            _BASE_TIME,
        ),
        status,
        Revision(revision),
        False,
        lease,
    )


def _leased_snapshot(suffix: str) -> WorkIntentSnapshot:
    lease = WorkIntentLease(
        DispatchId(f"dispatch-{suffix}"),
        DeliveryAttemptId(f"attempt-{suffix}"),
        LeaseHolderId(f"holder-{suffix}"),
        FencingToken(4),
        _BASE_TIME + timedelta(hours=1),
    )
    return _snapshot(suffix, status=WorkIntentStatus.LEASED, lease=lease)


def _claim(suffix: str) -> ClaimNextWorkIntent:
    return ClaimNextWorkIntent(
        LeaseHolderId(f"new-holder-{suffix}"),
        DeliveryAttemptId(f"new-attempt-{suffix}"),
        _BASE_TIME + timedelta(minutes=10),
        _BASE_TIME + timedelta(hours=2),
    )


def _heartbeat(
    snapshot: WorkIntentSnapshot,
    *,
    holder_id: LeaseHolderId | None = None,
) -> HeartbeatWorkIntentLease:
    assert snapshot.current_lease is not None
    lease = snapshot.current_lease
    return HeartbeatWorkIntentLease(
        snapshot.envelope.dispatch_id,
        lease.delivery_attempt_id,
        holder_id or lease.holder_id,
        lease.fencing_token,
        snapshot.revision,
        _BASE_TIME + timedelta(minutes=10),
        _BASE_TIME + timedelta(hours=2),
    )


def _raw_row(engine: Engine, dispatch_id: DispatchId) -> dict[str, object]:
    with engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    f'SELECT * FROM "{_SCHEMA}"."durable_dispatch_work_intents" '
                    "WHERE dispatch_id = :dispatch_id"
                ),
                {"dispatch_id": dispatch_id.value},
            )
            .mappings()
            .one()
        )
    return dict(row)


def _seed(
    composition: DurableDispatchPostgresComposition,
    *snapshots: WorkIntentSnapshot,
) -> None:
    with composition.uow_factory() as uow:
        for snapshot in snapshots:
            uow.work_intents.add(snapshot)
        uow.commit()


def test_claim_application_commits_before_return_and_releases_connection(
    composition: DurableDispatchPostgresComposition,
) -> None:
    initial = _snapshot("application-claim")
    _seed(composition, initial)

    claimed = composition.lease_application.claim_next_work_intent(_claim("first"))
    assert claimed is not None
    assert claimed.envelope.dispatch_id == initial.envelope.dispatch_id
    assert claimed.current_lease is not None
    assert claimed.current_lease.holder_id == LeaseHolderId("new-holder-first")

    row = _raw_row(composition.engine, initial.envelope.dispatch_id)
    assert row["status"] == WorkIntentStatus.LEASED.value
    assert row["revision"] == 1
    assert row["fencing_token"] == 1
    assert row["delivery_attempt_id"] == "new-attempt-first"

    # A second independent application call observes the committed ownership,
    # proving that the first short transaction released its row lock.
    assert (
        composition.lease_application.claim_next_work_intent(_claim("second")) is None
    )


def test_heartbeat_application_commits_exact_update_and_maps_ownership_loss(
    composition: DurableDispatchPostgresComposition,
) -> None:
    initial = _leased_snapshot("application-heartbeat")
    _seed(composition, initial)
    before = _raw_row(composition.engine, initial.envelope.dispatch_id)

    extension = _heartbeat(initial)
    refreshed = composition.lease_application.heartbeat_work_intent_lease(extension)
    assert refreshed.envelope.dispatch_id == initial.envelope.dispatch_id
    assert refreshed.revision == Revision(1)
    assert refreshed.current_lease is not None
    assert refreshed.current_lease.lease_expires_at == extension.lease_expires_at

    after = _raw_row(composition.engine, initial.envelope.dispatch_id)
    expected = dict(before)
    expected["revision"] = 1
    expected["lease_expires_at"] = extension.lease_expires_at
    assert after == expected

    unchanged = dict(after)
    with pytest.raises(DurableDispatchLeaseError) as raised:
        composition.lease_application.heartbeat_work_intent_lease(
            _heartbeat(refreshed, holder_id=LeaseHolderId("wrong-holder"))
        )
    error = raised.value
    assert error.error_code == "lease_lost"
    assert error.category == "ownership"
    assert error.message == "Lease is no longer current"
    assert error.retryability is False
    assert error.relevant_dispatch_id == initial.envelope.dispatch_id
    assert error.delivery_attempt_id == refreshed.current_lease.delivery_attempt_id
    assert error.expected_revision == refreshed.revision
    assert error.conflicting_state is None
    assert error.recovery_hint == "reclaim"
    assert _raw_row(composition.engine, initial.envelope.dispatch_id) == unchanged
