"""Opt-in real PostgreSQL acceptance for the Durable Dispatch adapter."""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, event, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchConstraintError,
    DurableDispatchRevisionConflictError,
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
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import (
    WorkIntentStatus,
)
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

if os.environ.get("MVP0_RUN_DURABLE_DISPATCH_POSTGRES") != "1":
    pytest.skip(
        "set MVP0_RUN_DURABLE_DISPATCH_POSTGRES=1 for the opt-in "
        "Durable Dispatch suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_019b_durable_dispatch"
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
    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=_database_url(), pool_size=4, max_overflow=0, pool_timeout=3
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))
    try:
        command.upgrade(_alembic_config(_database_url()), "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        engine.dispose()


def _factory(engine: Engine) -> DurableDispatchPostgresUnitOfWorkFactory:
    return DurableDispatchPostgresUnitOfWorkFactory.from_engine(engine, schema=SCHEMA)


def _snapshot(
    suffix: str,
    *,
    revision: int = 0,
    lease: WorkIntentLease | None = None,
    status: WorkIntentStatus = WorkIntentStatus.AVAILABLE,
    superseded_by: DispatchId | None = None,
) -> WorkIntentSnapshot:
    dispatch_id = DispatchId(f"dispatch-{suffix}")
    timestamp = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
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
            timestamp,
            timestamp,
        ),
        status,
        Revision(revision),
        False,
        lease,
        superseded_by,
    )


def _leased_snapshot(suffix: str, token: int) -> WorkIntentSnapshot:
    dispatch_id = DispatchId(f"dispatch-{suffix}")
    return _snapshot(
        suffix,
        lease=WorkIntentLease(
            dispatch_id,
            DeliveryAttemptId(f"attempt-{suffix}"),
            LeaseHolderId(f"holder-{suffix}"),
            FencingToken(token),
            datetime(2026, 8, 10, 13, 0, tzinfo=UTC),
        ),
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


def test_add_get_commit_and_uncommitted_rollback(postgres_engine: Engine) -> None:
    factory = _factory(postgres_engine)
    committed = _snapshot("commit")
    with factory() as uow:
        uow.work_intents.add(committed)
        uow.commit()

    with factory() as uow:
        assert uow.work_intents.get(committed.envelope.dispatch_id) == committed
        uow.commit()

    rolled_back = _snapshot("rollback")
    with factory() as uow:
        uow.work_intents.add(rolled_back)
    with factory() as uow:
        assert uow.work_intents.get(rolled_back.envelope.dispatch_id) is None
        uow.commit()


def test_supersession_reference_round_trips_through_repository(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    successor = _snapshot("successor")
    superseded = _snapshot(
        "superseded",
        revision=1,
        status=WorkIntentStatus.SUPERSEDED,
        superseded_by=successor.envelope.dispatch_id,
    )
    with factory() as uow:
        uow.work_intents.add(successor)
        uow.work_intents.add(superseded)
        uow.commit()

    with factory() as uow:
        loaded = uow.work_intents.get(superseded.envelope.dispatch_id)
        assert loaded == superseded
        assert loaded is not None and loaded.superseded_by is not None
        assert loaded.superseded_by == successor.envelope.dispatch_id
        uow.commit()

    row = _raw_row(postgres_engine, superseded.envelope.dispatch_id)
    assert row["superseded_by_dispatch_id"] == successor.envelope.dispatch_id.value

    with factory() as uow:
        loaded = uow.work_intents.get(superseded.envelope.dispatch_id)
        assert loaded is not None
        cleared = replace(loaded, superseded_by=None, revision=Revision(2))
        uow.work_intents.save(cleared, expected_revision=Revision(1))
        uow.commit()

    cleared_row = _raw_row(postgres_engine, superseded.envelope.dispatch_id)
    assert cleared_row["superseded_by_dispatch_id"] is None
    assert cleared_row["dispatch_id"] == superseded.envelope.dispatch_id.value
    assert cleared_row["status"] == WorkIntentStatus.SUPERSEDED.value


def test_two_independent_uows_have_one_exact_revision_cas_winner(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    initial = _snapshot("cas")
    with factory() as uow:
        uow.work_intents.add(initial)
        uow.commit()

    first, second = factory(), factory()
    with first as left, second as right:
        left_value = left.work_intents.get(initial.envelope.dispatch_id)
        right_value = right.work_intents.get(initial.envelope.dispatch_id)
        assert left_value is not None and right_value is not None
        left_changed = replace(left_value, revision=Revision(1))
        right_changed = replace(right_value, revision=Revision(1))
        left.work_intents.save(left_changed, expected_revision=Revision(0))
        left.commit()
        with pytest.raises(DurableDispatchRevisionConflictError):
            right.work_intents.save(right_changed, expected_revision=Revision(0))
        right.rollback()

    with factory() as uow:
        current = uow.work_intents.get(initial.envelope.dispatch_id)
        assert current is not None and current.revision == Revision(1)
        uow.commit()


def test_no_lease_cas_clears_lease_and_retains_fencing_generation(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    leased = _leased_snapshot("retained", token=7)
    with factory() as uow:
        uow.work_intents.add(leased)
        uow.commit()

    with factory() as uow:
        current = uow.work_intents.get(leased.envelope.dispatch_id)
        assert current is not None and current.current_lease is not None
        no_lease = replace(current, current_lease=None, revision=Revision(1))
        uow.work_intents.save(no_lease, expected_revision=Revision(0))
        uow.commit()

    row = _raw_row(postgres_engine, leased.envelope.dispatch_id)
    assert row["fencing_token"] == 7
    assert row["delivery_attempt_id"] is None
    assert row["lease_holder_id"] is None
    assert row["lease_expires_at"] is None


def test_leased_cas_persists_new_active_fencing_token(postgres_engine: Engine) -> None:
    factory = _factory(postgres_engine)
    leased = _leased_snapshot("token", token=2)
    with factory() as uow:
        uow.work_intents.add(leased)
        uow.commit()

    with factory() as uow:
        current = uow.work_intents.get(leased.envelope.dispatch_id)
        assert current is not None and current.current_lease is not None
        previous = current.current_lease
        replacement = WorkIntentLease(
            previous.dispatch_id,
            previous.delivery_attempt_id,
            previous.holder_id,
            FencingToken(3),
            previous.lease_expires_at,
        )
        uow.work_intents.save(
            replace(current, current_lease=replacement, revision=Revision(1)),
            expected_revision=Revision(0),
        )
        uow.commit()

    row = _raw_row(postgres_engine, leased.envelope.dispatch_id)
    assert row["fencing_token"] == 3
    assert row["delivery_attempt_id"] == "attempt-token"


def test_missing_identity_conflicts_and_duplicate_integrity_is_typed(
    postgres_engine: Engine,
) -> None:
    factory = _factory(postgres_engine)
    missing = _snapshot("missing")
    with pytest.raises(DurableDispatchRevisionConflictError):
        with factory() as uow:
            uow.work_intents.save(missing, expected_revision=Revision(0))

    duplicate = _snapshot("duplicate")
    with factory() as uow:
        uow.work_intents.add(duplicate)
        uow.commit()
    with pytest.raises(DurableDispatchConstraintError) as raised:
        with factory() as uow:
            uow.work_intents.add(duplicate)
    assert raised.value.safe_context["constraint"] == (
        "pk_durable_dispatch_work_intents"
    )


def test_fresh_uow_sessions_return_connections(postgres_engine: Engine) -> None:
    checkins = 0

    def on_checkin(*_: object) -> None:
        nonlocal checkins
        checkins += 1

    event.listen(postgres_engine, "checkin", on_checkin)
    try:
        factory = _factory(postgres_engine)
        first, second = factory(), factory()
        assert first is not second
        with first as uow:
            assert uow.work_intents.get(DispatchId("not-present")) is None
            uow.commit()
        first_checkins = checkins
        with second as uow:
            assert uow.work_intents.get(DispatchId("still-not-present")) is None
            uow.commit()
        assert first_checkins >= 1
        assert checkins > first_checkins
    finally:
        event.remove(postgres_engine, "checkin", on_checkin)
