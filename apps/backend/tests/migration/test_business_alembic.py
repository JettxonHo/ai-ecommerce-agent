"""Bounded real-PostgreSQL verification for the MVP0-019B Business tables.

The suite is opt-in because the default test lane blocks network access.  It
uses one fixed, test-owned schema and removes that schema during teardown; no
shared Business or Checkpoint table is touched.  Each test resets that schema
instead of downgrading the forward-only migration lineage.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError

from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)

pytestmark = [pytest.mark.integration, pytest.mark.live, pytest.mark.migration]

if os.environ.get("MVP0_RUN_POSTGRES_MIGRATION") != "1":
    pytest.skip(
        "set MVP0_RUN_POSTGRES_MIGRATION=1 for the opt-in real PostgreSQL "
        "migration suite",
        allow_module_level=True,
    )


BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"
BUSINESS_SCHEMA = "mvp0_019b_migration"
BASELINE_REVISION = "0001_business_baseline"
TASK_HEAD_REVISION = "0002_task_management"
SOURCE_HEAD_REVISION = "0003_source_evidence"
DISPATCH_HEAD_REVISION = "0004_durable_dispatch"
PREVIOUS_HEAD_REVISION = "0008_review_export"
REVIEW_PREVIOUS_REVISION = "0007_deterministic_result"
RESULT_PREVIOUS_REVISION = "0006_task_primary_input"
SUPERSESSION_REVISION = "0005_dispatch_supersession"
HEAD_REVISION = "0009_needs_input"
DATABASE_URL_ENV = "MVP0_MIGRATION_DATABASE_URL"
DOMAIN_TABLES = (
    "durable_dispatch_work_intents",
    "source_evidence_source_version_processing",
    "source_evidence_source_versions",
    "source_evidence_sources",
    "source_evidence_task_primary_inputs",
    "source_evidence_task_source_associations",
    "task_management_create_idempotency",
    "task_management_deterministic_results",
    "task_management_export_snapshots",
    "task_management_needs_input_requests",
    "task_management_runs",
    "task_management_stages",
    "task_management_tasks",
)
SOURCE_TABLE = "source_evidence_sources"
SOURCE_VERSION_TABLE = "source_evidence_source_versions"
PROCESSING_TABLE = "source_evidence_source_version_processing"
ASSOCIATION_TABLE = "source_evidence_task_source_associations"
DURABLE_TABLE = "durable_dispatch_work_intents"
RESULT_TABLE = "task_management_deterministic_results"
RESULT_COLUMNS = (
    "task_id",
    "result_revision",
    "input_revision",
    "idempotency_key",
    "status",
    "generated_at",
    "missing_information",
    "product_intake",
    "customer_insight",
    "product_positioning",
    "marketing_brief",
    "xiaohongshu_brief",
    "confirmed_at",
    "confirmation_idempotency_key",
    "confirmed_marketing_core_message",
    "confirmed_xiaohongshu_title_direction",
    "marketing_brief_version_id",
    "marketing_brief_version_number",
    "xiaohongshu_brief_version_id",
    "xiaohongshu_brief_version_number",
)
DURABLE_COLUMNS = (
    "dispatch_id",
    "intent_type",
    "owning_operation",
    "target_resource_kind",
    "target_resource_id",
    "command_id",
    "stage_run_id",
    "input_fingerprint",
    "fingerprint_schema_version",
    "base_domain_version_id",
    "expected_revision",
    "payload_resource_kind",
    "payload_resource_id",
    "rerun_of_dispatch_id",
    "ordering_key",
    "created_at",
    "available_at",
    "status",
    "revision",
    "cancellation_requested",
    "delivery_attempt_id",
    "lease_holder_id",
    "fencing_token",
    "lease_expires_at",
    "superseded_by_dispatch_id",
)
DURABLE_STATUS_VALUES = (
    "pending",
    "available",
    "leased",
    "in_progress",
    "succeeded",
    "failed_retryable",
    "failed_terminal",
    "cancelled",
    "superseded",
)
DURABLE_CHECK_COLUMN_NAMES = {
    "fingerprint_schema_version": "fp_schema_version",
    "base_domain_version_id": "base_version",
}
DURABLE_CONSTRAINT_NAMES = {
    "pk_durable_dispatch_work_intents",
    "fk_durable_dispatch_work_intents_rerun_of",
    "ck_durable_dispatch_work_intents_dispatch_id_nonempty",
    "ck_durable_dispatch_work_intents_intent_type_nonempty",
    "ck_durable_dispatch_work_intents_owning_operation_nonempty",
    "ck_durable_dispatch_work_intents_target_resource_kind_nonempty",
    "ck_durable_dispatch_work_intents_target_resource_id_nonempty",
    "ck_durable_dispatch_work_intents_command_id_nonempty",
    "ck_durable_dispatch_work_intents_input_fingerprint_nonempty",
    "ck_durable_dispatch_work_intents_fp_schema_version_nonempty",
    "ck_durable_dispatch_work_intents_payload_resource_kind_nonempty",
    "ck_durable_dispatch_work_intents_payload_resource_id_nonempty",
    "ck_durable_dispatch_work_intents_stage_run_id_nonempty",
    "ck_durable_dispatch_work_intents_base_version_nonempty",
    "ck_durable_dispatch_work_intents_rerun_of_dispatch_id_nonempty",
    "ck_durable_dispatch_work_intents_ordering_key_nonempty",
    "ck_durable_dispatch_work_intents_delivery_attempt_id_nonempty",
    "ck_durable_dispatch_work_intents_lease_holder_id_nonempty",
    "ck_durable_dispatch_work_intents_status",
    "ck_durable_dispatch_work_intents_revision_nonnegative",
    "ck_durable_dispatch_work_intents_expected_revision_nonnegative",
    "ck_durable_dispatch_work_intents_fencing_token_nonnegative",
    "ck_durable_dispatch_work_intents_available_not_before_created",
    "ck_durable_dispatch_work_intents_rerun_distinct",
    "ck_durable_dispatch_work_intents_lease_tuple",
    "ck_durable_dispatch_work_intents_leased_fencing_token",
    "fk_durable_dispatch_work_intents_superseded_by",
    "ck_durable_dispatch_work_intents_superseded_by_nonempty",
    "ck_durable_dispatch_work_intents_superseded_by_distinct",
}


class InjectedMigrationFailure(RuntimeError):
    """Injected failure used only by the bounded transaction test."""


def _database_url() -> str:
    url = os.environ.get(DATABASE_URL_ENV, "").strip()
    if not url:
        pytest.fail(
            f"{DATABASE_URL_ENV} must be set to a test-owned PostgreSQL URL "
            "when MVP0_RUN_POSTGRES_MIGRATION=1"
        )
    return url


@pytest.fixture(scope="module")
def migration_engine() -> Iterator[Engine]:
    """Own and remove exactly the fixed MVP0-019B verification schema."""

    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=_database_url(),
            pool_size=1,
            max_overflow=0,
            pool_timeout=2,
        )
    )
    _reset_schema(engine)
    try:
        yield engine
    finally:
        _drop_schema(engine)
        with engine.connect() as connection:
            remaining = connection.scalar(
                text("SELECT count(*) FROM pg_namespace WHERE nspname = :schema"),
                {"schema": BUSINESS_SCHEMA},
            )
        assert remaining == 0, "MVP0-019B test schema cleanup was not verifiable"
        engine.dispose()


def _reset_schema(engine: Engine) -> None:
    """Reset only the fixed test-owned schema between migration scenarios."""

    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{BUSINESS_SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{BUSINESS_SCHEMA}"'))


def _drop_schema(engine: Engine) -> None:
    """Drop only the fixed test-owned schema during fixture cleanup."""

    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{BUSINESS_SCHEMA}" CASCADE'))


def _config(database_url: str) -> Config:
    config = Config(str(ALEMBIC_INI))
    # ConfigParser treats percent signs as interpolation markers.  Escaping
    # them preserves URL-encoded credentials when Alembic reads this option.
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", BUSINESS_SCHEMA)
    config.set_main_option("version_table_schema", BUSINESS_SCHEMA)
    return config


def _version_rows(engine: Engine) -> list[str]:
    with engine.connect() as connection:
        return list(
            connection.scalars(
                text(
                    f'SELECT version_num FROM "{BUSINESS_SCHEMA}"."alembic_version" '
                    "ORDER BY version_num"
                )
            )
        )


def _tables(engine: Engine) -> list[str]:
    with engine.connect() as connection:
        return list(
            connection.scalars(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = :schema ORDER BY tablename"
                ),
                {"schema": BUSINESS_SCHEMA},
            )
        )


def _columns(engine: Engine, table_name: str) -> list[str]:
    with engine.connect() as connection:
        return list(
            connection.scalars(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = :schema AND table_name = :table "
                    "ORDER BY ordinal_position"
                ),
                {"schema": BUSINESS_SCHEMA, "table": table_name},
            )
        )


def _column_details(engine: Engine, table_name: str) -> list[tuple[str, str, str, str]]:
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT column_name, data_type, udt_name, is_nullable "
                "FROM information_schema.columns "
                "WHERE table_schema = :schema AND table_name = :table "
                "ORDER BY ordinal_position"
            ),
            {"schema": BUSINESS_SCHEMA, "table": table_name},
        )
        return [tuple(row) for row in rows]


def _table_exists(engine: Engine, table_name: str) -> bool:
    with engine.connect() as connection:
        return bool(
            connection.scalar(
                text(
                    "SELECT EXISTS (SELECT 1 FROM pg_class c "
                    "JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = :schema AND c.relname = :table "
                    "AND c.relkind IN ('r', 'p'))"
                ),
                {"schema": BUSINESS_SCHEMA, "table": table_name},
            )
        )


def _constraint_names(engine: Engine) -> set[str]:
    with engine.connect() as connection:
        return set(
            connection.scalars(
                text(
                    "SELECT con.conname "
                    "FROM pg_constraint con "
                    "JOIN pg_namespace n ON n.oid = con.connamespace "
                    "WHERE n.nspname = :schema"
                ),
                {"schema": BUSINESS_SCHEMA},
            )
        )


def _version_num_details(engine: Engine) -> tuple[str, int | None]:
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT data_type, character_maximum_length "
                "FROM information_schema.columns "
                "WHERE table_schema = :schema AND table_name = 'alembic_version' "
                "AND column_name = 'version_num'"
            ),
            {"schema": BUSINESS_SCHEMA},
        ).one()
    return str(row[0]), row[1]


def _constraint_definitions(engine: Engine, table_name: str) -> dict[str, str]:
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT con.conname, pg_get_constraintdef(con.oid) "
                "FROM pg_constraint con "
                "JOIN pg_class rel ON rel.oid = con.conrelid "
                "JOIN pg_namespace n ON n.oid = rel.relnamespace "
                "WHERE n.nspname = :schema AND rel.relname = :table "
                "ORDER BY con.conname"
            ),
            {"schema": BUSINESS_SCHEMA, "table": table_name},
        )
        definitions: dict[str, str] = {}
        for row in rows:
            definitions[str(row[0])] = str(row[1])
        return definitions


def _normalize_constraint_sql(expression: str) -> str:
    """Ignore formatting and only redundant outer CHECK parentheses."""

    normalized = " ".join(expression.lower().split())
    if normalized.startswith("check "):
        normalized = normalized[6:]
    while normalized.startswith("(") and normalized.endswith(")"):
        depth = 0
        closes_before_end = False
        for index, character in enumerate(normalized):
            if character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0 and index != len(normalized) - 1:
                    closes_before_end = True
                    break
        if closes_before_end:
            break
        normalized = normalized[1:-1].strip()
    return normalized


def _index_names(engine: Engine, table_name: str) -> set[str]:
    with engine.connect() as connection:
        return set(
            connection.scalars(
                text(
                    "SELECT indexname FROM pg_indexes "
                    "WHERE schemaname = :schema AND tablename = :table"
                ),
                {"schema": BUSINESS_SCHEMA, "table": table_name},
            )
        )


def _insert_work_intent(
    engine: Engine,
    *,
    dispatch_id: str,
    include_superseded_by: bool = True,
    intent_type: str = "source.process",
    owning_operation: str = "task.run",
    target_resource_kind: str = "task",
    target_resource_id: str = "task-01",
    command_id: str = "command-01",
    stage_run_id: str | None = None,
    input_fingerprint: str = "fingerprint-01",
    fingerprint_schema_version: str = "v1",
    base_domain_version_id: str | None = None,
    expected_revision: int | None = None,
    payload_resource_kind: str = "source_version",
    payload_resource_id: str = "source-version-01",
    rerun_of_dispatch_id: str | None = None,
    superseded_by_dispatch_id: str | None = None,
    ordering_key: str | None = None,
    created_at: datetime = datetime(2026, 8, 9, 10, 0, tzinfo=UTC),
    available_at: datetime = datetime(2026, 8, 9, 10, 0, tzinfo=UTC),
    status: str = "pending",
    revision: int = 0,
    cancellation_requested: bool = False,
    delivery_attempt_id: str | None = None,
    lease_holder_id: str | None = None,
    fencing_token: int = 0,
    lease_expires_at: datetime | None = None,
) -> None:
    columns = (
        "dispatch_id, intent_type, owning_operation, target_resource_kind, "
        "target_resource_id, command_id, stage_run_id, input_fingerprint, "
        "fingerprint_schema_version, base_domain_version_id, expected_revision, "
        "payload_resource_kind, payload_resource_id, rerun_of_dispatch_id, "
        "ordering_key, created_at, available_at, status, revision, "
        "cancellation_requested, delivery_attempt_id, lease_holder_id, "
        "fencing_token, lease_expires_at"
    )
    values = (
        ":dispatch_id, :intent_type, :owning_operation, :target_resource_kind, "
        ":target_resource_id, :command_id, :stage_run_id, :input_fingerprint, "
        ":fingerprint_schema_version, :base_domain_version_id, "
        ":expected_revision, :payload_resource_kind, :payload_resource_id, "
        ":rerun_of_dispatch_id, :ordering_key, :created_at, :available_at, "
        ":status, :revision, :cancellation_requested, :delivery_attempt_id, "
        ":lease_holder_id, :fencing_token, :lease_expires_at"
    )
    if include_superseded_by:
        columns += ", superseded_by_dispatch_id"
        values += ", :superseded_by_dispatch_id"
    with engine.begin() as connection:
        connection.execute(
            text(
                f'INSERT INTO "{BUSINESS_SCHEMA}"."{DURABLE_TABLE}" '
                f"({columns}) VALUES ({values})"
            ),
            {
                "dispatch_id": dispatch_id,
                "intent_type": intent_type,
                "owning_operation": owning_operation,
                "target_resource_kind": target_resource_kind,
                "target_resource_id": target_resource_id,
                "command_id": command_id,
                "stage_run_id": stage_run_id,
                "input_fingerprint": input_fingerprint,
                "fingerprint_schema_version": fingerprint_schema_version,
                "base_domain_version_id": base_domain_version_id,
                "expected_revision": expected_revision,
                "payload_resource_kind": payload_resource_kind,
                "payload_resource_id": payload_resource_id,
                "rerun_of_dispatch_id": rerun_of_dispatch_id,
                "superseded_by_dispatch_id": superseded_by_dispatch_id,
                "ordering_key": ordering_key,
                "created_at": created_at,
                "available_at": available_at,
                "status": status,
                "revision": revision,
                "cancellation_requested": cancellation_requested,
                "delivery_attempt_id": delivery_attempt_id,
                "lease_holder_id": lease_holder_id,
                "fencing_token": fencing_token,
                "lease_expires_at": lease_expires_at,
            },
        )


def _seed_source_schema(engine: Engine) -> None:
    """Create a valid synthetic Task/Source graph for constraint probes."""

    _reset_schema(engine)
    command.upgrade(_config(_database_url()), HEAD_REVISION)
    with engine.begin() as connection:
        connection.execute(
            text(
                f'INSERT INTO "{BUSINESS_SCHEMA}"."task_management_tasks" '
                "(task_id, task_name, product_category, promotion_goal, "
                "task_status, revision, updated_at) "
                "VALUES (:task_id, :task_name, :product_category, "
                ":promotion_goal, :task_status, :revision, :updated_at)"
            ),
            {
                "task_id": "task-01",
                "task_name": "Synthetic anchor",
                "product_category": "bags",
                "promotion_goal": "launch",
                "task_status": "draft",
                "revision": 0,
                "updated_at": datetime(2026, 8, 9, tzinfo=UTC),
            },
        )
        connection.execute(
            text(
                f'INSERT INTO "{BUSINESS_SCHEMA}"."task_management_tasks" '
                "(task_id, task_name, product_category, promotion_goal, "
                "task_status, revision, updated_at) "
                "VALUES (:task_id, :task_name, :product_category, "
                ":promotion_goal, :task_status, :revision, :updated_at)"
            ),
            {
                "task_id": "task-02",
                "task_name": "Synthetic second task",
                "product_category": "bags",
                "promotion_goal": "compare",
                "task_status": "draft",
                "revision": 0,
                "updated_at": datetime(2026, 8, 9, tzinfo=UTC),
            },
        )
        connection.execute(
            text(
                f'INSERT INTO "{BUSINESS_SCHEMA}"."{SOURCE_TABLE}" '
                "(source_id) VALUES (:source_id)"
            ),
            [{"source_id": "source-01"}, {"source_id": "source-02"}],
        )
        connection.execute(
            text(
                f'INSERT INTO "{BUSINESS_SCHEMA}"."{SOURCE_VERSION_TABLE}" '
                "(source_version_id, source_id, version_number) "
                "VALUES (:source_version_id, :source_id, :version_number)"
            ),
            [
                {
                    "source_version_id": "source-version-01",
                    "source_id": "source-01",
                    "version_number": 1,
                },
                {
                    "source_version_id": "source-version-02",
                    "source_id": "source-01",
                    "version_number": 2,
                },
                {
                    "source_version_id": "source-version-03",
                    "source_id": "source-02",
                    "version_number": 1,
                },
            ],
        )


def _insert_association(
    engine: Engine,
    *,
    association_id: str,
    task_id: str = "task-01",
    source_id: str = "source-01",
    source_version_id: str = "source-version-01",
    membership_state: str = "active",
    revision: int = 0,
    replaced_by_association_id: str | None = None,
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                f'INSERT INTO "{BUSINESS_SCHEMA}"."{ASSOCIATION_TABLE}" '
                "(source_association_id, task_id, source_id, "
                "source_version_id, membership_state, revision, "
                "replaced_by_association_id) VALUES "
                "(:association_id, :task_id, :source_id, :source_version_id, "
                ":membership_state, :revision, :replaced_by_association_id)"
            ),
            {
                "association_id": association_id,
                "task_id": task_id,
                "source_id": source_id,
                "source_version_id": source_version_id,
                "membership_state": membership_state,
                "revision": revision,
                "replaced_by_association_id": replaced_by_association_id,
            },
        )


def test_revision_graph_has_one_business_head() -> None:
    """The production lineage has one Durable Dispatch head and parent."""

    script = ScriptDirectory.from_config(_config(_database_url()))
    assert len(HEAD_REVISION) <= 32
    assert script.get_heads() == [HEAD_REVISION]
    head = script.get_revision(HEAD_REVISION)
    assert head is not None
    assert head.down_revision == PREVIOUS_HEAD_REVISION
    previous_head = script.get_revision(PREVIOUS_HEAD_REVISION)
    assert previous_head is not None
    assert previous_head.down_revision == REVIEW_PREVIOUS_REVISION
    review_previous = script.get_revision(REVIEW_PREVIOUS_REVISION)
    assert review_previous is not None
    assert review_previous.down_revision == RESULT_PREVIOUS_REVISION
    result_previous = script.get_revision(RESULT_PREVIOUS_REVISION)
    assert result_previous is not None
    assert result_previous.down_revision == SUPERSESSION_REVISION
    supersession = script.get_revision(SUPERSESSION_REVISION)
    assert supersession is not None
    assert supersession.down_revision == DISPATCH_HEAD_REVISION
    dispatch_head = script.get_revision(DISPATCH_HEAD_REVISION)
    assert dispatch_head is not None
    assert dispatch_head.down_revision == SOURCE_HEAD_REVISION
    source_head = script.get_revision(SOURCE_HEAD_REVISION)
    assert source_head is not None
    assert source_head.down_revision == TASK_HEAD_REVISION
    task_head = script.get_revision(TASK_HEAD_REVISION)
    assert task_head is not None
    assert task_head.down_revision == BASELINE_REVISION
    baseline = script.get_revision(BASELINE_REVISION)
    assert baseline is not None
    assert baseline.down_revision is None


def test_fresh_upgrade_reaches_current_head(
    migration_engine: Engine,
) -> None:
    """A fresh test schema reaches the single head and creates all tables."""

    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), "head")

    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]
    assert _version_num_details(migration_engine) == ("character varying", 32)


def test_explicit_baseline_to_head_upgrade(
    migration_engine: Engine,
) -> None:
    """A schema explicitly at 0001 can advance to the Durable Dispatch head."""

    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, BASELINE_REVISION)
    assert _version_rows(migration_engine) == [BASELINE_REVISION]
    assert _tables(migration_engine) == ["alembic_version"]

    command.upgrade(config, HEAD_REVISION)
    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]


def test_existing_task_head_to_current_head_upgrade(
    migration_engine: Engine,
) -> None:
    """A schema at the Task head advances through Source to the current head."""

    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, TASK_HEAD_REVISION)
    assert _version_rows(migration_engine) == [TASK_HEAD_REVISION]
    assert _tables(migration_engine) == [
        "alembic_version",
        "task_management_runs",
        "task_management_stages",
        "task_management_tasks",
    ]

    command.upgrade(config, HEAD_REVISION)
    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]


def test_existing_source_head_to_durable_head_upgrade(
    migration_engine: Engine,
) -> None:
    """A schema at 0003 adds Durable Dispatch and its 0005 column."""

    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, SOURCE_HEAD_REVISION)
    assert _version_rows(migration_engine) == [SOURCE_HEAD_REVISION]
    assert _tables(migration_engine) == [
        "alembic_version",
        "source_evidence_source_version_processing",
        "source_evidence_source_versions",
        "source_evidence_sources",
        "source_evidence_task_source_associations",
        "task_management_runs",
        "task_management_stages",
        "task_management_tasks",
    ]

    command.upgrade(config, HEAD_REVISION)
    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]
    assert _columns(migration_engine, DURABLE_TABLE)[-1] == (
        "superseded_by_dispatch_id"
    )


def test_existing_durable_head_to_supersession_head_preserves_rows(
    migration_engine: Engine,
) -> None:
    """A 0004 row survives the additive 0005 upgrade with a null reference."""

    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, DISPATCH_HEAD_REVISION)
    _insert_work_intent(
        migration_engine,
        dispatch_id="dispatch-0004",
        include_superseded_by=False,
    )

    command.upgrade(config, HEAD_REVISION)

    assert _version_rows(migration_engine) == [HEAD_REVISION]
    with migration_engine.connect() as connection:
        assert (
            connection.execute(
                text(
                    f'SELECT superseded_by_dispatch_id FROM "{BUSINESS_SCHEMA}".'
                    f"\"{DURABLE_TABLE}\" WHERE dispatch_id = 'dispatch-0004'"
                )
            ).scalar_one()
            is None
        )


def test_durable_downgrade_is_forward_only_and_preserves_state(
    migration_engine: Engine,
) -> None:
    """A rejected downgrade preserves the head, table, and Work Intent row."""

    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, HEAD_REVISION)
    _insert_work_intent(migration_engine, dispatch_id="dispatch-downgrade")

    with pytest.raises(RuntimeError, match="forward-fix-only"):
        command.downgrade(config, PREVIOUS_HEAD_REVISION)

    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _version_num_details(migration_engine) == ("character varying", 32)
    assert _table_exists(migration_engine, DURABLE_TABLE)
    assert _columns(migration_engine, DURABLE_TABLE)[-1] == (
        "superseded_by_dispatch_id"
    )
    assert {
        "fk_durable_dispatch_work_intents_superseded_by",
        "ck_durable_dispatch_work_intents_superseded_by_nonempty",
        "ck_durable_dispatch_work_intents_superseded_by_distinct",
    } <= _constraint_names(migration_engine)
    with migration_engine.connect() as connection:
        assert (
            connection.scalar(
                text(
                    f'SELECT count(*) FROM "{BUSINESS_SCHEMA}"."{DURABLE_TABLE}" '
                    "WHERE dispatch_id = 'dispatch-downgrade'"
                )
            )
            == 1
        )


def test_alembic_current_check_and_offline_sql_are_reviewable(
    migration_engine: Engine,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Current, drift check, and offline SQL identify the Durable revision."""

    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, "head")
    command.current(config)
    command.check(config)
    command.upgrade(config, "head", sql=True)
    output = capsys.readouterr().out

    assert HEAD_REVISION in output
    assert "CREATE TABLE" in output
    # PostgreSQL's offline compiler may quote or leave a safe lowercase
    # identifier unquoted; the schema-qualified identity is what matters.
    assert f"{BUSINESS_SCHEMA}.alembic_version" in output
    assert all(table in output for table in DOMAIN_TABLES)
    for table in DOMAIN_TABLES:
        assert f"CREATE TABLE {BUSINESS_SCHEMA}.{table}" in output
        assert f"CREATE TABLE {table}" not in output
    assert f"ALTER TABLE {BUSINESS_SCHEMA}.{DURABLE_TABLE}" in output
    assert f"ALTER TABLE {DURABLE_TABLE}" not in output


def test_named_tables_and_constraints_are_present(
    migration_engine: Engine,
) -> None:
    """The head owns exact tables and named ownership/state constraints."""

    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), "head")

    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]
    expected_constraints = {
        "pk_task_management_tasks",
        "pk_task_management_runs",
        "pk_task_management_stages",
        "uq_task_management_runs_task_run",
        "fk_task_management_runs_task_owner",
        "fk_task_management_runs_source_owner",
        "fk_task_management_runs_current_stage_owner",
        "fk_task_management_stages_task_owner",
        "fk_task_management_stages_last_run_owner",
        "fk_task_management_tasks_current_stage_owner",
        "fk_task_management_tasks_active_run_owner",
        "fk_task_management_tasks_latest_run_owner",
        "pk_task_management_create_idempotency",
        "uq_task_management_create_idempotency_task",
        "fk_task_management_create_idempotency_task_owner",
        "ck_task_management_create_idempotency_key_nonempty",
        "ck_task_management_tasks_status",
        "ck_task_management_runs_status",
        "ck_task_management_stages_stage",
        "ck_task_management_stages_status",
        "pk_source_evidence_sources",
        "pk_source_evidence_source_versions",
        "pk_source_evidence_source_version_processing",
        "pk_source_evidence_task_source_associations",
        "uq_source_evidence_source_versions_source_version_number",
        "uq_source_evidence_source_versions_version_source",
        "uq_source_evidence_task_source_associations_association_owner",
        "fk_source_evidence_source_versions_source_owner",
        "fk_source_evidence_source_version_processing_version_owner",
        "fk_source_evidence_task_source_associations_task_owner",
        "fk_source_evidence_task_source_associations_source_owner",
        "fk_source_evidence_assoc_source_version_owner",
        "fk_source_evidence_task_source_associations_replacement_owner",
        "ck_source_evidence_source_versions_version_number_positive",
        "ck_source_evidence_source_version_processing_status",
        "ck_source_evidence_processing_revision_nonnegative",
        "ck_source_evidence_task_source_associations_membership_state",
        "ck_source_evidence_assoc_revision_nonnegative",
        "ck_source_evidence_assoc_replacement_distinct",
        "ck_source_evidence_assoc_replacement_link",
        "pk_source_evidence_task_primary_inputs",
        "fk_source_evidence_task_primary_inputs_task_owner",
        "ck_source_evidence_task_primary_inputs_kind",
        "ck_source_evidence_task_primary_inputs_content_nonempty",
        "ck_source_evidence_task_primary_inputs_byte_count",
        "ck_source_evidence_task_primary_inputs_revision_nonnegative",
        "ck_source_evidence_task_primary_inputs_filename_pair",
        "pk_task_management_deterministic_results",
        "uq_task_management_results_task_input",
        "uq_task_management_results_task_key",
        "fk_task_management_results_task_owner",
        "ck_task_management_results_task_id_nonempty",
        "ck_task_management_results_key_nonempty",
        "ck_task_management_results_result_revision_nonnegative",
        "ck_task_management_results_input_revision_nonnegative",
        "ck_task_management_results_status",
        "ck_task_management_results_missing_information_nonempty",
        "ck_task_management_results_confirmation_projection",
        "ck_task_management_results_confirmation_size",
        "uq_task_management_results_task_confirmation_key",
        "pk_task_management_export_snapshots",
        "uq_task_management_export_snapshots_task_key",
        "fk_task_management_export_snapshots_task_owner",
        "ck_task_management_export_snapshots_id_nonempty",
        "ck_task_management_export_snapshots_task_id_nonempty",
        "ck_task_management_export_snapshots_key_nonempty",
        "ck_task_management_export_snapshots_brief_kind",
        "ck_task_management_export_snapshots_revisions_nonnegative",
        "ck_task_management_export_snapshots_version_positive",
        "ck_task_management_export_snapshots_version_id_nonempty",
        "ck_task_management_export_snapshots_media_type",
        "ck_task_management_export_snapshots_template_version",
        "ck_task_management_export_snapshots_content_nonempty",
        "ck_task_management_export_snapshots_content_utf8_nonempty",
        "pk_task_management_needs_input_requests",
        "uq_task_management_needs_input_requests_task_action",
        "fk_task_management_needs_input_requests_task_owner",
        "fk_task_management_needs_input_requests_superseded_by",
        "ck_task_management_needs_input_requests_id_nonempty",
        "ck_task_management_needs_input_requests_task_id_nonempty",
        "ck_task_management_needs_input_requests_revision_nonnegative",
        "ck_task_management_needs_input_requests_status",
        "ck_task_management_needs_input_requests_reason_type",
        "ck_task_management_needs_input_requests_reason_summary",
        "ck_task_management_needs_input_requests_affected_stages",
        "ck_task_management_needs_input_requests_source_references",
        "ck_task_management_needs_input_requests_conflict_values",
        "ck_task_management_needs_input_requests_allowed_resolutions",
        "ck_task_management_needs_input_requests_expected_recovery",
        "ck_task_management_needs_input_requests_resolution_key",
        "ck_task_management_needs_input_requests_resolution_type",
        "ck_task_management_needs_input_requests_resolution_payload",
        "ck_task_management_needs_input_requests_state_projection",
        "ck_task_management_needs_input_requests_resolution_status",
        "ck_task_management_needs_input_requests_superseded_distinct",
        *DURABLE_CONSTRAINT_NAMES,
    }
    assert expected_constraints <= _constraint_names(migration_engine)


def test_source_tables_have_exact_minimal_columns(
    migration_engine: Engine,
) -> None:
    """Source persistence contains only the accepted identity/state fields."""

    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), HEAD_REVISION)

    assert _columns(migration_engine, SOURCE_TABLE) == ["source_id"]
    assert _columns(migration_engine, SOURCE_VERSION_TABLE) == [
        "source_version_id",
        "source_id",
        "version_number",
    ]
    assert _columns(migration_engine, PROCESSING_TABLE) == [
        "source_version_id",
        "status",
        "revision",
        "failure_summary",
        "updated_at",
    ]
    assert _columns(migration_engine, ASSOCIATION_TABLE) == [
        "source_association_id",
        "task_id",
        "source_id",
        "source_version_id",
        "membership_state",
        "revision",
        "replaced_by_association_id",
    ]


def test_deterministic_result_has_exact_atomic_columns_and_constraints(
    migration_engine: Engine,
) -> None:
    """Result rows carry one complete candidate set and durable fences."""

    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), HEAD_REVISION)

    assert _columns(migration_engine, RESULT_TABLE) == list(RESULT_COLUMNS)
    assert _column_details(migration_engine, RESULT_TABLE) == [
        ("task_id", "text", "text", "NO"),
        ("result_revision", "bigint", "int8", "NO"),
        ("input_revision", "bigint", "int8", "NO"),
        ("idempotency_key", "text", "text", "NO"),
        ("status", "text", "text", "NO"),
        ("generated_at", "timestamp with time zone", "timestamptz", "NO"),
        ("missing_information", "text", "text", "NO"),
        ("product_intake", "text", "text", "YES"),
        ("customer_insight", "text", "text", "YES"),
        ("product_positioning", "text", "text", "YES"),
        ("marketing_brief", "text", "text", "YES"),
        ("xiaohongshu_brief", "text", "text", "YES"),
        ("confirmed_at", "timestamp with time zone", "timestamptz", "YES"),
        ("confirmation_idempotency_key", "text", "text", "YES"),
        ("confirmed_marketing_core_message", "text", "text", "YES"),
        ("confirmed_xiaohongshu_title_direction", "text", "text", "YES"),
        ("marketing_brief_version_id", "text", "text", "YES"),
        ("marketing_brief_version_number", "bigint", "int8", "YES"),
        ("xiaohongshu_brief_version_id", "text", "text", "YES"),
        ("xiaohongshu_brief_version_number", "bigint", "int8", "YES"),
    ]
    assert {
        "pk_task_management_deterministic_results",
        "uq_task_management_results_task_input",
        "uq_task_management_results_task_key",
        "fk_task_management_results_task_owner",
        "ck_task_management_results_status",
    } <= set(_constraint_definitions(migration_engine, RESULT_TABLE))


def test_durable_work_intent_has_exact_columns_and_types(
    migration_engine: Engine,
) -> None:
    """The Work Intent table has the frozen ordered 25-column shape."""

    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), HEAD_REVISION)

    assert _columns(migration_engine, DURABLE_TABLE) == list(DURABLE_COLUMNS)
    assert _column_details(migration_engine, DURABLE_TABLE) == [
        ("dispatch_id", "text", "text", "NO"),
        ("intent_type", "text", "text", "NO"),
        ("owning_operation", "text", "text", "NO"),
        ("target_resource_kind", "text", "text", "NO"),
        ("target_resource_id", "text", "text", "NO"),
        ("command_id", "text", "text", "NO"),
        ("stage_run_id", "text", "text", "YES"),
        ("input_fingerprint", "text", "text", "NO"),
        ("fingerprint_schema_version", "text", "text", "NO"),
        ("base_domain_version_id", "text", "text", "YES"),
        ("expected_revision", "bigint", "int8", "YES"),
        ("payload_resource_kind", "text", "text", "NO"),
        ("payload_resource_id", "text", "text", "NO"),
        ("rerun_of_dispatch_id", "text", "text", "YES"),
        ("ordering_key", "text", "text", "YES"),
        ("created_at", "timestamp with time zone", "timestamptz", "NO"),
        ("available_at", "timestamp with time zone", "timestamptz", "NO"),
        ("status", "text", "text", "NO"),
        ("revision", "bigint", "int8", "NO"),
        ("cancellation_requested", "boolean", "bool", "NO"),
        ("delivery_attempt_id", "text", "text", "YES"),
        ("lease_holder_id", "text", "text", "YES"),
        ("fencing_token", "bigint", "int8", "NO"),
        ("lease_expires_at", "timestamp with time zone", "timestamptz", "YES"),
        ("superseded_by_dispatch_id", "text", "text", "YES"),
    ]


def test_durable_work_intent_has_named_checks_fk_and_only_primary_index(
    migration_engine: Engine,
) -> None:
    """The Work Intent table exposes only named structural constraints."""

    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), HEAD_REVISION)

    definitions = _constraint_definitions(migration_engine, DURABLE_TABLE)
    assert set(definitions) == DURABLE_CONSTRAINT_NAMES
    assert definitions["pk_durable_dispatch_work_intents"] == (
        "PRIMARY KEY (dispatch_id)"
    )
    assert _normalize_constraint_sql(
        definitions["fk_durable_dispatch_work_intents_rerun_of"]
    ) == _normalize_constraint_sql(
        "FOREIGN KEY (rerun_of_dispatch_id) REFERENCES "
        f"{BUSINESS_SCHEMA}.{DURABLE_TABLE}(dispatch_id)"
    )
    expected_checks = {
        **{
            (
                "ck_durable_dispatch_work_intents_"
                f"{DURABLE_CHECK_COLUMN_NAMES.get(column, column)}_nonempty"
            ): (f"length(btrim({column})) > 0")
            for column in (
                "dispatch_id",
                "intent_type",
                "owning_operation",
                "target_resource_kind",
                "target_resource_id",
                "command_id",
                "input_fingerprint",
                "fingerprint_schema_version",
                "payload_resource_kind",
                "payload_resource_id",
            )
        },
        **{
            (
                "ck_durable_dispatch_work_intents_"
                f"{DURABLE_CHECK_COLUMN_NAMES.get(column, column)}_nonempty"
            ): (f"({column} IS NULL) OR (length(btrim({column})) > 0)")
            for column in (
                "stage_run_id",
                "base_domain_version_id",
                "rerun_of_dispatch_id",
                "ordering_key",
                "delivery_attempt_id",
                "lease_holder_id",
            )
        },
        "ck_durable_dispatch_work_intents_status": (
            "status = ANY (ARRAY["
            + ", ".join(f"'{value}'::text" for value in DURABLE_STATUS_VALUES)
            + "])"
        ),
        "ck_durable_dispatch_work_intents_revision_nonnegative": "revision >= 0",
        "ck_durable_dispatch_work_intents_expected_revision_nonnegative": (
            "(expected_revision IS NULL) OR (expected_revision >= 0)"
        ),
        "ck_durable_dispatch_work_intents_fencing_token_nonnegative": (
            "fencing_token >= 0"
        ),
        "ck_durable_dispatch_work_intents_available_not_before_created": (
            "available_at >= created_at"
        ),
        "ck_durable_dispatch_work_intents_rerun_distinct": (
            "(rerun_of_dispatch_id IS NULL) OR (rerun_of_dispatch_id <> dispatch_id)"
        ),
        "ck_durable_dispatch_work_intents_lease_tuple": (
            "((delivery_attempt_id IS NULL) AND (lease_holder_id IS NULL) AND "
            "(lease_expires_at IS NULL)) OR "
            "((delivery_attempt_id IS NOT NULL) AND "
            "(lease_holder_id IS NOT NULL) AND "
            "(lease_expires_at IS NOT NULL))"
        ),
        "ck_durable_dispatch_work_intents_leased_fencing_token": (
            "((delivery_attempt_id IS NULL) AND (lease_holder_id IS NULL) AND "
            "(lease_expires_at IS NULL)) OR (fencing_token >= 1)"
        ),
        "fk_durable_dispatch_work_intents_superseded_by": (
            "FOREIGN KEY (superseded_by_dispatch_id) REFERENCES "
            f"{BUSINESS_SCHEMA}.{DURABLE_TABLE}(dispatch_id)"
        ),
        "ck_durable_dispatch_work_intents_superseded_by_nonempty": (
            "(superseded_by_dispatch_id IS NULL) OR "
            "(length(btrim(superseded_by_dispatch_id)) > 0)"
        ),
        "ck_durable_dispatch_work_intents_superseded_by_distinct": (
            "(superseded_by_dispatch_id IS NULL) OR "
            "(superseded_by_dispatch_id <> dispatch_id)"
        ),
    }
    assert {
        name: _normalize_constraint_sql(definitions[name]) for name in expected_checks
    } == {
        name: _normalize_constraint_sql(expression)
        for name, expression in expected_checks.items()
    }
    assert _index_names(migration_engine, DURABLE_TABLE) == {
        "pk_durable_dispatch_work_intents"
    }


def test_durable_work_intent_constraints_enforce_catalog_and_lease_shape(
    migration_engine: Engine,
) -> None:
    """Real PostgreSQL rejects invalid identity, state, and lease tuples."""

    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), HEAD_REVISION)

    # A no-lease row may retain the initial zero fencing counter.
    _insert_work_intent(migration_engine, dispatch_id="dispatch-01")
    # Distinct dispatch identities may share a command identity; no semantic
    # command uniqueness is encoded by this revision.
    _insert_work_intent(
        migration_engine, dispatch_id="dispatch-02", command_id="command-01"
    )
    _insert_work_intent(
        migration_engine,
        dispatch_id="dispatch-03",
        status="leased",
        delivery_attempt_id="attempt-01",
        lease_holder_id="worker-01",
        fencing_token=1,
        lease_expires_at=datetime(2026, 8, 9, 11, 0, tzinfo=UTC),
    )
    _insert_work_intent(
        migration_engine,
        dispatch_id="dispatch-04",
        rerun_of_dispatch_id="dispatch-01",
        superseded_by_dispatch_id="dispatch-02",
    )
    for index, status in enumerate(DURABLE_STATUS_VALUES, start=10):
        _insert_work_intent(
            migration_engine,
            dispatch_id=f"dispatch-status-{index}",
            status=status,
        )

    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine, dispatch_id="dispatch-whitespace", intent_type=" "
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-optional-whitespace",
            stage_run_id=" ",
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine, dispatch_id="dispatch-status", status="running"
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine, dispatch_id="dispatch-revision", revision=-1
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-expected-revision",
            expected_revision=-1,
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine, dispatch_id="dispatch-fencing", fencing_token=-1
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-time-order",
            created_at=datetime(2026, 8, 9, 12, 0, tzinfo=UTC),
            available_at=datetime(2026, 8, 9, 11, 0, tzinfo=UTC),
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-self-rerun",
            rerun_of_dispatch_id="dispatch-self-rerun",
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-partial-lease",
            delivery_attempt_id="attempt-partial",
            lease_holder_id=None,
            lease_expires_at=datetime(2026, 8, 9, 11, 0, tzinfo=UTC),
            fencing_token=1,
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-zero-leased-token",
            delivery_attempt_id="attempt-zero",
            lease_holder_id="worker-zero",
            lease_expires_at=datetime(2026, 8, 9, 11, 0, tzinfo=UTC),
            fencing_token=0,
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-missing-rerun",
            rerun_of_dispatch_id="dispatch-missing",
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-superseded-whitespace",
            superseded_by_dispatch_id=" ",
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-superseded-self",
            superseded_by_dispatch_id="dispatch-superseded-self",
        )
    with pytest.raises(IntegrityError):
        _insert_work_intent(
            migration_engine,
            dispatch_id="dispatch-superseded-missing",
            superseded_by_dispatch_id="dispatch-not-present",
        )

    with migration_engine.begin() as connection:
        connection.execute(
            text(
                f'UPDATE "{BUSINESS_SCHEMA}"."{DURABLE_TABLE}" '
                "SET delivery_attempt_id = NULL, lease_holder_id = NULL, "
                "lease_expires_at = NULL "
                "WHERE dispatch_id = 'dispatch-03'"
            )
        )
        retained = connection.execute(
            text(
                f'SELECT fencing_token FROM "{BUSINESS_SCHEMA}"."{DURABLE_TABLE}" '
                "WHERE dispatch_id = 'dispatch-03'"
            )
        ).scalar_one()
    assert retained == 1


def test_source_constraints_reject_invalid_version_processing_and_revision(
    migration_engine: Engine,
) -> None:
    """PostgreSQL enforces immutable-version, status, and revision bounds."""

    _seed_source_schema(migration_engine)

    with pytest.raises(IntegrityError):
        with migration_engine.begin() as connection:
            connection.execute(
                text(
                    f'INSERT INTO "{BUSINESS_SCHEMA}"."{SOURCE_VERSION_TABLE}" '
                    "(source_version_id, source_id, version_number) "
                    "VALUES (:source_version_id, :source_id, :version_number)"
                ),
                {
                    "source_version_id": "source-version-zero",
                    "source_id": "source-01",
                    "version_number": 0,
                },
            )

    with pytest.raises(IntegrityError):
        with migration_engine.begin() as connection:
            connection.execute(
                text(
                    f'INSERT INTO "{BUSINESS_SCHEMA}"."{SOURCE_VERSION_TABLE}" '
                    "(source_version_id, source_id, version_number) "
                    "VALUES (:source_version_id, :source_id, :version_number)"
                ),
                {
                    "source_version_id": "source-version-duplicate-number",
                    "source_id": "source-01",
                    "version_number": 1,
                },
            )

    with pytest.raises(IntegrityError):
        with migration_engine.begin() as connection:
            connection.execute(
                text(
                    f'INSERT INTO "{BUSINESS_SCHEMA}"."{PROCESSING_TABLE}" '
                    "(source_version_id, status, revision, updated_at) "
                    "VALUES (:source_version_id, :status, :revision, :updated_at)"
                ),
                {
                    "source_version_id": "source-version-01",
                    "status": "not-a-status",
                    "revision": 0,
                    "updated_at": datetime(2026, 8, 9, tzinfo=UTC),
                },
            )

    with pytest.raises(IntegrityError):
        with migration_engine.begin() as connection:
            connection.execute(
                text(
                    f'INSERT INTO "{BUSINESS_SCHEMA}"."{PROCESSING_TABLE}" '
                    "(source_version_id, status, revision, updated_at) "
                    "VALUES (:source_version_id, :status, :revision, :updated_at)"
                ),
                {
                    "source_version_id": "source-version-01",
                    "status": "registered",
                    "revision": -1,
                    "updated_at": datetime(2026, 8, 9, tzinfo=UTC),
                },
            )

    _insert_association(migration_engine, association_id="association-valid")
    with pytest.raises(IntegrityError):
        _insert_association(
            migration_engine,
            association_id="association-negative-revision",
            revision=-1,
        )


def test_source_constraints_enforce_task_and_source_version_ownership(
    migration_engine: Engine,
) -> None:
    """Task, Source, and exact SourceVersion ownership are database FKs."""

    _seed_source_schema(migration_engine)

    with pytest.raises(IntegrityError):
        _insert_association(
            migration_engine,
            association_id="association-unknown-task",
            task_id="task-missing",
        )

    with pytest.raises(IntegrityError):
        _insert_association(
            migration_engine,
            association_id="association-cross-source-version",
            source_id="source-02",
            source_version_id="source-version-01",
        )

    with pytest.raises(IntegrityError):
        _insert_association(
            migration_engine,
            association_id="association-unknown-version",
            source_version_id="source-version-missing",
        )


def test_source_constraints_enforce_replacement_identity_and_link_state(
    migration_engine: Engine,
) -> None:
    """Replacement links are same-owner, distinct, and state-consistent."""

    _seed_source_schema(migration_engine)
    _insert_association(migration_engine, association_id="association-one")
    _insert_association(
        migration_engine,
        association_id="association-two",
        source_version_id="source-version-02",
    )

    # A non-replaced row cannot carry a replacement link, even when the target
    # exists and belongs to the same Task and Source.
    with pytest.raises(IntegrityError):
        _insert_association(
            migration_engine,
            association_id="association-three",
            replaced_by_association_id="association-two",
        )

    # A replaced row must carry a link to a distinct same-owner association.
    with pytest.raises(IntegrityError):
        _insert_association(
            migration_engine,
            association_id="association-self",
            membership_state="replaced",
            replaced_by_association_id="association-self",
        )

    with pytest.raises(IntegrityError):
        _insert_association(
            migration_engine,
            association_id="association-no-link",
            membership_state="replaced",
        )

    # A target with a different Task cannot satisfy the composite replacement
    # FK, even when its association identity is otherwise valid.
    _insert_association(
        migration_engine,
        association_id="association-other-task",
        task_id="task-02",
        source_version_id="source-version-02",
    )
    with pytest.raises(IntegrityError):
        _insert_association(
            migration_engine,
            association_id="association-cross-task",
            replaced_by_association_id="association-other-task",
            membership_state="replaced",
        )


def _run_test_only_failure_path(engine: Engine) -> None:
    """Create a probe with Alembic Operations, then fail its transaction."""

    with engine.begin() as connection:
        operations = Operations(MigrationContext.configure(connection))
        operations.create_table(
            "mvp0_018f_failed_probe",
            sa.Column("id", sa.Integer, primary_key=True),
            schema=BUSINESS_SCHEMA,
        )
        raise InjectedMigrationFailure("representative test-only migration failure")


def _run_test_only_forward_repair(engine: Engine) -> None:
    """Repair the failed test path with a new transaction, not a rewrite."""

    with engine.begin() as connection:
        operations = Operations(MigrationContext.configure(connection))
        operations.create_table(
            "mvp0_018f_failed_probe",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column(
                "repaired", sa.Boolean, nullable=False, server_default=sa.false()
            ),
            schema=BUSINESS_SCHEMA,
        )


def test_representative_failure_rolls_back_and_forward_repairs(
    migration_engine: Engine,
) -> None:
    """Transactional DDL leaves no partial object; a new repair succeeds."""

    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, "head")
    with pytest.raises(InjectedMigrationFailure):
        _run_test_only_failure_path(migration_engine)

    assert not _table_exists(migration_engine, "mvp0_018f_failed_probe")
    _run_test_only_forward_repair(migration_engine)
    assert _table_exists(migration_engine, "mvp0_018f_failed_probe")
    assert _version_rows(migration_engine) == [HEAD_REVISION]
