"""Opt-in PostgreSQL acceptance for Durable Dispatch control operations."""

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

from ai_ecommerce_agent.bootstrap.durable_dispatch_postgres import (
    DurableDispatchPostgresComposition,
    compose_durable_dispatch_postgres,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_commands import (
    AcknowledgeWorkIntentStop,
    RequestWorkIntentCancellation,
    SupersedeWorkIntent,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_errors import (
    DurableDispatchControlError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_queries import (
    CheckOwnedWorkIntentControl,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_results import (
    WorkIntentControlDisposition,
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
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure.repositories import (
    DurableDispatchPostgresWorkIntentRepository,
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

if os.environ.get("MVP0_RUN_DURABLE_DISPATCH_CONTROL_APPLICATION_POSTGRES") != "1":
    pytest.skip(
        "set MVP0_RUN_DURABLE_DISPATCH_CONTROL_APPLICATION_POSTGRES=1 for the "
        "opt-in Durable Dispatch control PostgreSQL suite",
        allow_module_level=True,
    )

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA = "mvp0_019c_control_application"
_URL_ENV = "MVP0_DURABLE_DISPATCH_DATABASE_URL"
_DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)
_NOW = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)


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
    cancellation_requested: bool = False,
    lease: WorkIntentLease | None = None,
    superseded_by: DispatchId | None = None,
    rerun_of: DispatchId | None = None,
    expires_at: datetime = _NOW + timedelta(hours=1),
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
            rerun_of,
            f"ordering-{suffix}",
            _NOW,
            _NOW,
        ),
        status,
        Revision(revision),
        cancellation_requested,
        lease,
        superseded_by,
    )


def _leased_snapshot(
    suffix: str,
    *,
    token: int = 4,
    status: WorkIntentStatus = WorkIntentStatus.LEASED,
    revision: int = 0,
    cancellation_requested: bool = False,
    superseded_by: DispatchId | None = None,
    expires_at: datetime = _NOW + timedelta(hours=1),
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
        cancellation_requested=cancellation_requested,
        lease=lease,
        superseded_by=superseded_by,
    )


def _successor_envelope(
    old: WorkIntentSnapshot, suffix: str = "successor"
) -> WorkIntentEnvelope:
    return WorkIntentEnvelope(
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
        old.envelope.dispatch_id,
        f"ordering-{suffix}",
        _NOW,
        _NOW,
    )


def _seed(
    composition: DurableDispatchPostgresComposition,
    *snapshots: WorkIntentSnapshot,
) -> None:
    with composition.uow_factory() as uow:
        for snapshot in snapshots:
            uow.work_intents.add(snapshot)
        uow.commit()


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


def _changed_keys(before: dict[str, object], after: dict[str, object]) -> set[str]:
    return {key for key in before if before[key] != after[key]}


def _cancel(snapshot: WorkIntentSnapshot) -> RequestWorkIntentCancellation:
    return RequestWorkIntentCancellation(
        snapshot.envelope.dispatch_id, snapshot.revision, _NOW
    )


def _owned_query(
    snapshot: WorkIntentSnapshot, *, expected: Revision | None = None
) -> CheckOwnedWorkIntentControl:
    assert snapshot.current_lease is not None
    lease = snapshot.current_lease
    return CheckOwnedWorkIntentControl(
        snapshot.envelope.dispatch_id,
        lease.delivery_attempt_id,
        lease.holder_id,
        lease.fencing_token,
        expected or snapshot.revision,
        _NOW,
    )


def _ack(snapshot: WorkIntentSnapshot) -> AcknowledgeWorkIntentStop:
    assert snapshot.current_lease is not None
    lease = snapshot.current_lease
    return AcknowledgeWorkIntentStop(
        snapshot.envelope.dispatch_id,
        lease.delivery_attempt_id,
        lease.holder_id,
        lease.fencing_token,
        snapshot.revision,
        _NOW,
    )


def test_control_query_and_active_cancellation_commit_once_and_release_connection(
    composition: DurableDispatchPostgresComposition,
) -> None:
    initial = _leased_snapshot("query-cancel")
    _seed(composition, initial)
    before_query = _raw_row(composition.engine, initial.envelope.dispatch_id)
    checked = composition.control_application.check_owned_work_intent_control(
        _owned_query(initial)
    )
    assert checked.disposition is WorkIntentControlDisposition.CONTINUE_EXECUTION
    after_query = _raw_row(composition.engine, initial.envelope.dispatch_id)
    assert after_query == before_query
    requested = composition.control_application.request_work_intent_cancellation(
        _cancel(initial)
    )
    assert requested.status is WorkIntentStatus.LEASED
    assert requested.cancellation_requested is True
    assert requested.revision == Revision(1)
    after_cancel = _raw_row(composition.engine, initial.envelope.dispatch_id)
    assert _changed_keys(after_query, after_cancel) == {
        "revision",
        "cancellation_requested",
    }
    assert after_cancel["status"] == WorkIntentStatus.LEASED.value
    assert after_cancel["cancellation_requested"] is True
    assert after_cancel["revision"] == 1
    assert after_cancel["fencing_token"] == 4
    assert (
        composition.control_application.check_owned_work_intent_control(
            _owned_query(requested)
        ).disposition
        is WorkIntentControlDisposition.STOP_FOR_CANCELLATION
    )
    acknowledged = composition.control_application.acknowledge_work_intent_stop(
        _ack(requested)
    )
    assert acknowledged.status is WorkIntentStatus.CANCELLED
    after_ack = _raw_row(composition.engine, initial.envelope.dispatch_id)
    assert _changed_keys(after_cancel, after_ack) == {
        "revision",
        "status",
        "delivery_attempt_id",
        "lease_holder_id",
        "lease_expires_at",
    }
    assert after_ack["fencing_token"] == 4


def test_unowned_and_expired_cancellation_terminalize_without_fencing_drift(
    composition: DurableDispatchPostgresComposition,
) -> None:
    available = _snapshot("unowned-cancel")
    expired = _leased_snapshot(
        "expired-cancel",
        token=7,
        expires_at=_NOW - timedelta(minutes=1),
    )
    _seed(composition, available, expired)
    available_before = _raw_row(composition.engine, available.envelope.dispatch_id)
    cancelled = composition.control_application.request_work_intent_cancellation(
        _cancel(available)
    )
    assert cancelled.status is WorkIntentStatus.CANCELLED
    assert cancelled.current_lease is None
    available_after = _raw_row(composition.engine, available.envelope.dispatch_id)
    assert _changed_keys(available_before, available_after) == {
        "status",
        "revision",
        "cancellation_requested",
    }
    assert available_after["status"] == WorkIntentStatus.CANCELLED.value
    assert available_after["revision"] == 1
    assert available_after["fencing_token"] == available_before["fencing_token"]
    assert available_after["delivery_attempt_id"] is None
    expired_before = _raw_row(composition.engine, expired.envelope.dispatch_id)
    expired_cancelled = (
        composition.control_application.request_work_intent_cancellation(
            _cancel(expired)
        )
    )
    assert expired_cancelled.status is WorkIntentStatus.CANCELLED
    assert expired_cancelled.current_lease is None
    expired_after = _raw_row(composition.engine, expired.envelope.dispatch_id)
    assert _changed_keys(expired_before, expired_after) == {
        "status",
        "revision",
        "cancellation_requested",
        "delivery_attempt_id",
        "lease_holder_id",
        "lease_expires_at",
    }
    assert expired_after["status"] == WorkIntentStatus.CANCELLED.value
    assert expired_after["fencing_token"] == 7
    assert expired_after["delivery_attempt_id"] is None


def test_supersession_adds_successor_and_acknowledges_only_current_owner(
    composition: DurableDispatchPostgresComposition,
) -> None:
    old = _leased_snapshot("supersede-active", token=8)
    successor = _successor_envelope(old)
    _seed(composition, old)
    old_before = _raw_row(composition.engine, old.envelope.dispatch_id)
    result = composition.control_application.supersede_work_intent(
        SupersedeWorkIntent(old.envelope.dispatch_id, successor, old.revision, _NOW)
    )
    assert result.superseded.status is WorkIntentStatus.LEASED
    assert result.superseded.current_lease == old.current_lease
    assert result.successor.status is WorkIntentStatus.AVAILABLE
    old_row = _raw_row(composition.engine, old.envelope.dispatch_id)
    assert _changed_keys(old_before, old_row) == {
        "revision",
        "superseded_by_dispatch_id",
    }
    assert old_row["superseded_by_dispatch_id"] == successor.dispatch_id.value
    assert old_row["status"] == WorkIntentStatus.LEASED.value
    assert old_row["revision"] == 1
    assert (
        _raw_row(composition.engine, successor.dispatch_id)["rerun_of_dispatch_id"]
        == old.envelope.dispatch_id.value
    )
    acknowledged = composition.control_application.acknowledge_work_intent_stop(
        _ack(result.superseded)
    )
    assert acknowledged.status is WorkIntentStatus.SUPERSEDED
    assert acknowledged.current_lease is None
    after_ack = _raw_row(composition.engine, old.envelope.dispatch_id)
    assert _changed_keys(old_row, after_ack) == {
        "status",
        "revision",
        "delivery_attempt_id",
        "lease_holder_id",
        "lease_expires_at",
    }
    assert after_ack["fencing_token"] == 8
    assert after_ack["status"] == WorkIntentStatus.SUPERSEDED.value


def test_unowned_and_expired_supersession_terminalize_old_and_add_available_successor(
    composition: DurableDispatchPostgresComposition,
) -> None:
    unowned = _snapshot("supersede-unowned")
    unowned_successor = _successor_envelope(unowned, "successor-unowned")
    _seed(composition, unowned)
    unowned_before = _raw_row(composition.engine, unowned.envelope.dispatch_id)
    unowned_result = composition.control_application.supersede_work_intent(
        SupersedeWorkIntent(
            unowned.envelope.dispatch_id,
            unowned_successor,
            unowned.revision,
            _NOW,
        )
    )
    assert unowned_result.superseded.status is WorkIntentStatus.SUPERSEDED
    assert unowned_result.superseded.current_lease is None
    unowned_after = _raw_row(composition.engine, unowned.envelope.dispatch_id)
    assert _changed_keys(unowned_before, unowned_after) == {
        "status",
        "revision",
        "superseded_by_dispatch_id",
    }
    assert (
        _raw_row(composition.engine, unowned_successor.dispatch_id)["status"]
        == WorkIntentStatus.AVAILABLE.value
    )

    expired = _leased_snapshot(
        "supersede-expired",
        expires_at=_NOW - timedelta(minutes=1),
    )
    expired_successor = _successor_envelope(expired, "successor-expired")
    _seed(composition, expired)
    expired_result = composition.control_application.supersede_work_intent(
        SupersedeWorkIntent(
            expired.envelope.dispatch_id,
            expired_successor,
            expired.revision,
            _NOW,
        )
    )
    assert expired_result.superseded.status is WorkIntentStatus.SUPERSEDED
    assert expired_result.superseded.current_lease is None
    assert expired_result.successor.status is WorkIntentStatus.AVAILABLE


def test_supersession_cas_loss_rolls_back_successor_and_keeps_competing_cas_update(
    composition: DurableDispatchPostgresComposition,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old = _leased_snapshot("supersede-cas-loss", token=9)
    successor = _successor_envelope(old, "successor-cas-loss")
    _seed(composition, old)
    before = _raw_row(composition.engine, old.envelope.dispatch_id)
    competitor = create_postgres_engine(
        PostgresEngineConfig(
            database_url=_database_url(),
            pool_size=1,
            max_overflow=0,
            pool_timeout=3,
        )
    )
    original_add = DurableDispatchPostgresWorkIntentRepository.add

    def add_then_competing_cas(
        repository: DurableDispatchPostgresWorkIntentRepository,
        snapshot: WorkIntentSnapshot,
    ) -> None:
        original_add(repository, snapshot)
        with competitor.begin() as connection:
            connection.execute(
                text(
                    f'UPDATE "{_SCHEMA}"."durable_dispatch_work_intents" '
                    "SET revision = revision + 1, "
                    "lease_expires_at = lease_expires_at + interval '5 minutes' "
                    "WHERE dispatch_id = :dispatch_id"
                ),
                {"dispatch_id": old.envelope.dispatch_id.value},
            )

    monkeypatch.setattr(
        DurableDispatchPostgresWorkIntentRepository,
        "add",
        add_then_competing_cas,
    )
    try:
        with pytest.raises(DurableDispatchControlError) as raised:
            composition.control_application.supersede_work_intent(
                SupersedeWorkIntent(
                    old.envelope.dispatch_id,
                    successor,
                    old.revision,
                    _NOW,
                )
            )
    finally:
        competitor.dispose()
    assert raised.value.error_code == "revision_conflict"
    after = _raw_row(composition.engine, old.envelope.dispatch_id)
    assert _changed_keys(before, after) == {"revision", "lease_expires_at"}
    assert after["revision"] == 1
    with composition.engine.connect() as connection:
        count = connection.execute(
            text(
                f'SELECT count(*) FROM "{_SCHEMA}"."durable_dispatch_work_intents" '
                "WHERE dispatch_id = :dispatch_id"
            ),
            {"dispatch_id": successor.dispatch_id.value},
        ).scalar_one()
    assert count == 0


def test_duplicate_successor_constraint_rolls_back_old_without_orphan(
    composition: DurableDispatchPostgresComposition,
) -> None:
    old = _snapshot("supersede-duplicate", status=WorkIntentStatus.AVAILABLE)
    existing_successor = _snapshot(
        "successor-duplicate",
        status=WorkIntentStatus.AVAILABLE,
        rerun_of=old.envelope.dispatch_id,
    )
    _seed(composition, old, existing_successor)
    old_before = _raw_row(composition.engine, old.envelope.dispatch_id)
    with pytest.raises(DurableDispatchControlError) as raised:
        composition.control_application.supersede_work_intent(
            SupersedeWorkIntent(
                old.envelope.dispatch_id,
                _successor_envelope(old, "successor-duplicate"),
                old.revision,
                _NOW,
            )
        )
    assert raised.value.error_code == "constraint_violation"
    assert _raw_row(composition.engine, old.envelope.dispatch_id) == old_before
    with composition.engine.connect() as connection:
        count = connection.execute(
            text(
                f'SELECT count(*) FROM "{_SCHEMA}"."durable_dispatch_work_intents" '
                "WHERE dispatch_id = :dispatch_id"
            ),
            {"dispatch_id": existing_successor.envelope.dispatch_id.value},
        ).scalar_one()
    assert count == 1


def test_expired_owned_check_preserves_full_row_without_write(
    composition: DurableDispatchPostgresComposition,
) -> None:
    expired = _leased_snapshot(
        "expired-owned-check",
        expires_at=_NOW - timedelta(minutes=1),
    )
    _seed(composition, expired)
    before = _raw_row(composition.engine, expired.envelope.dispatch_id)
    with pytest.raises(DurableDispatchControlError) as raised:
        composition.control_application.check_owned_work_intent_control(
            _owned_query(expired)
        )
    assert raised.value.error_code == "ownership_lost"
    assert _raw_row(composition.engine, expired.envelope.dispatch_id) == before


def test_control_errors_preserve_rows_on_owner_loss_and_no_stop_ack(
    composition: DurableDispatchPostgresComposition,
) -> None:
    initial = _leased_snapshot("owner-loss")
    _seed(composition, initial)
    before = _raw_row(composition.engine, initial.envelope.dispatch_id)
    with pytest.raises(DurableDispatchControlError) as raised:
        composition.control_application.acknowledge_work_intent_stop(
            replace(_ack(initial), holder_id=LeaseHolderId("wrong-holder"))
        )
    assert raised.value.error_code == "ownership_lost"
    assert _raw_row(composition.engine, initial.envelope.dispatch_id) == before
    with pytest.raises(DurableDispatchControlError) as no_stop:
        composition.control_application.acknowledge_work_intent_stop(_ack(initial))
    assert no_stop.value.error_code == "invalid_state"
    assert _raw_row(composition.engine, initial.envelope.dispatch_id) == before


def test_newer_authoritative_stop_is_observable_without_caller_revision_write(
    composition: DurableDispatchPostgresComposition,
) -> None:
    initial = _leased_snapshot("newer-stop")
    _seed(composition, initial)
    stopped = replace(
        initial,
        revision=Revision(1),
        cancellation_requested=True,
    )
    with composition.uow_factory() as uow:
        uow.work_intents.save(stopped, expected_revision=initial.revision)
        uow.commit()
    result = composition.control_application.check_owned_work_intent_control(
        _owned_query(stopped, expected=Revision(0))
    )
    assert result.snapshot.revision == Revision(1)
    assert result.disposition is WorkIntentControlDisposition.STOP_FOR_CANCELLATION
