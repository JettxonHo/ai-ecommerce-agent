"""Acceptance contract for the single L1 Needs Input Business revision."""

from __future__ import annotations

import io
import os
from collections.abc import Iterator
from contextlib import redirect_stdout
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError

from ai_ecommerce_agent.modules.needs_input.infrastructure.tables import (
    NEEDS_INPUT_REQUESTS_TABLE,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)

pytestmark = pytest.mark.migration

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"
BUSINESS_SCHEMA = "mvp0_318_needs_input"
PREVIOUS_HEAD = "0008_review_export"
HEAD_REVISION = "0009_needs_input"
DATABASE_URL_ENV = "MVP0_MIGRATION_DATABASE_URL"
TABLE = "task_management_needs_input_requests"
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
EXPECTED_COLUMNS = (
    "action_request_id",
    "task_id",
    "revision",
    "status",
    "reason_type",
    "reason_summary",
    "affected_stages",
    "source_references",
    "conflict_values",
    "allowed_resolution_types",
    "expected_recovery",
    "superseded_by_action_request_id",
    "resolution_idempotency_key",
    "resolution_type",
    "resolution_payload",
    "resolved_at",
    "created_at",
    "updated_at",
)


def _database_url() -> str:
    value = os.environ.get(DATABASE_URL_ENV, "").strip()
    if not value:
        pytest.skip(f"set {DATABASE_URL_ENV}=... for real PostgreSQL migration tests")
    return value


def _config(database_url: str) -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", BUSINESS_SCHEMA)
    config.set_main_option("version_table_schema", BUSINESS_SCHEMA)
    return config


def _offline_sql() -> str:
    """Render the production lineage without opening a database connection."""

    config = _config("postgresql+psycopg://offline:offline@127.0.0.1/test")
    output = io.StringIO()
    with redirect_stdout(output):
        command.upgrade(config, "head", sql=True)
    return " ".join(output.getvalue().split())


def _reset_schema(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{BUSINESS_SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{BUSINESS_SCHEMA}"'))


@pytest.fixture(scope="module")
def migration_engine() -> Iterator[Engine]:
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
        with engine.begin() as connection:
            connection.execute(
                text(f'DROP SCHEMA IF EXISTS "{BUSINESS_SCHEMA}" CASCADE')
            )
        engine.dispose()


def _version_rows(engine: Engine) -> list[str]:
    with engine.connect() as connection:
        return list(
            connection.scalars(
                text(f'SELECT version_num FROM "{BUSINESS_SCHEMA}"."alembic_version"')
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


def _columns(engine: Engine) -> list[str]:
    with engine.connect() as connection:
        return list(
            connection.scalars(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = :schema AND table_name = :table "
                    "ORDER BY ordinal_position"
                ),
                {"schema": BUSINESS_SCHEMA, "table": TABLE},
            )
        )


def _index_definition(engine: Engine, name: str) -> str:
    with engine.connect() as connection:
        value = connection.scalar(
            text(
                "SELECT indexdef FROM pg_indexes "
                "WHERE schemaname = :schema AND tablename = :table "
                "AND indexname = :name"
            ),
            {"schema": BUSINESS_SCHEMA, "table": TABLE, "name": name},
        )
    assert value is not None
    return str(value)


def _seed_task(engine: Engine, *, task_id: str = "task-318") -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                f'INSERT INTO "{BUSINESS_SCHEMA}"."task_management_tasks" '
                "(task_id, task_name, product_category, promotion_goal, "
                "task_status, revision, updated_at) VALUES "
                "(:task_id, :task_name, :product_category, :promotion_goal, "
                ":task_status, :revision, :updated_at)"
            ),
            {
                "task_id": task_id,
                "task_name": "Synthetic Needs Input",
                "product_category": "bags",
                "promotion_goal": "launch",
                "task_status": "waiting_for_input",
                "revision": 0,
                "updated_at": datetime.now(UTC),
            },
        )


def _request_values(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "action_request_id": "needs-318-1",
        "task_id": "task-318",
        "revision": 0,
        "status": "open",
        "reason_type": "missing_information",
        "reason_summary": "A fictional product fact is required.",
        "affected_stages": '["product_intake_and_fact_extraction"]',
        "source_references": "[]",
        "conflict_values": "[]",
        "allowed_resolution_types": '["submit_correction"]',
        "expected_recovery": "rerun",
        "superseded_by_action_request_id": None,
        "resolution_idempotency_key": None,
        "resolution_type": None,
        "resolution_payload": None,
        "resolved_at": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    values.update(overrides)
    return values


def _insert_request(engine: Engine, **overrides: object) -> None:
    values = _request_values(**overrides)
    columns = ", ".join(values)
    bind_names = ", ".join(f":{key}" for key in values)
    with engine.begin() as connection:
        connection.execute(
            text(
                f'INSERT INTO "{BUSINESS_SCHEMA}"."{TABLE}" '
                f"({columns}) VALUES ({bind_names})"
            ),
            values,
        )


def test_revision_graph_has_one_needs_input_head() -> None:
    """L1 adds exactly one forward-only revision after 0008."""

    config = Config(str(ALEMBIC_INI))
    script = ScriptDirectory.from_config(config)
    assert script.get_heads() == [HEAD_REVISION]
    head = script.get_revision(HEAD_REVISION)
    assert head is not None
    assert head.down_revision == PREVIOUS_HEAD
    assert script.get_revision(PREVIOUS_HEAD) is not None


def test_supersession_fk_preserves_task_ownership() -> None:
    """A superseding request must belong to the same Task as its predecessor."""

    sql = _offline_sql()
    assert (
        "CONSTRAINT fk_task_management_needs_input_requests_superseded_by "
        "FOREIGN KEY(task_id, superseded_by_action_request_id) REFERENCES "
        "mvp0_318_needs_input.task_management_needs_input_requests "
        "(task_id, action_request_id)"
    ) in sql


def test_terminal_resolution_status_mapping_is_database_enforced() -> None:
    """Only cancel_path may produce cancelled; other resolutions resolve."""

    sql = _offline_sql()
    assert (
        "CONSTRAINT ck_task_management_needs_input_requests_resolution_status "
        "CHECK (((status IN ('open', 'superseded') AND resolution_type IS NULL) "
        "OR (status = 'cancelled' AND resolution_type = 'cancel_path') "
        "OR (status = 'resolved' AND resolution_type IN "
        "('provide_source_reference', 'choose_existing_value', "
        "'submit_correction', 'confirm_known_limitation'))))"
    ) in sql


def test_sufficient_result_supersession_allows_null_successor() -> None:
    """A sufficient result may supersede without inventing a replacement request."""

    sql = _offline_sql()
    assert (
        "(status = 'superseded' "
        "AND resolution_idempotency_key IS NULL AND resolution_type IS NULL "
        "AND resolution_payload IS NULL AND resolved_at IS NULL)"
    ) in sql


def test_successor_fk_is_deferred_and_only_that_fk_is_deferred() -> None:
    """Replacement ordering relies on a deferred same-Task successor FK."""

    sql = _offline_sql()
    assert (
        "CONSTRAINT fk_task_management_needs_input_requests_superseded_by "
        "FOREIGN KEY(task_id, superseded_by_action_request_id) REFERENCES "
        f"{BUSINESS_SCHEMA}.task_management_needs_input_requests "
        "(task_id, action_request_id) DEFERRABLE INITIALLY DEFERRED"
    ) in sql

    constraints = {
        constraint.name: constraint
        for constraint in NEEDS_INPUT_REQUESTS_TABLE.constraints
        if constraint.name is not None
    }
    successor = constraints["fk_task_management_needs_input_requests_superseded_by"]
    owner = constraints["fk_task_management_needs_input_requests_task_owner"]
    assert successor.deferrable is True
    assert successor.initially == "DEFERRED"
    assert owner.deferrable is None
    assert owner.initially is None


def test_fresh_upgrade_creates_one_task_owned_table(
    migration_engine: Engine,
) -> None:
    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), "head")
    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]
    assert _columns(migration_engine) == list(EXPECTED_COLUMNS)


def test_existing_0008_upgrade_preserves_rows_and_adds_only_needs_input(
    migration_engine: Engine,
) -> None:
    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, PREVIOUS_HEAD)
    _seed_task(migration_engine)
    command.upgrade(config, "head")
    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]
    with migration_engine.connect() as connection:
        assert (
            connection.scalar(
                text(
                    f'SELECT task_id FROM "{BUSINESS_SCHEMA}"."task_management_tasks" '
                    "WHERE task_id = :task_id"
                ),
                {"task_id": "task-318"},
            )
            == "task-318"
        )


def test_needs_input_constraints_reject_invalid_owner_revision_status_and_payload(
    migration_engine: Engine,
) -> None:
    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), "head")
    _seed_task(migration_engine)
    with pytest.raises(IntegrityError):
        _insert_request(migration_engine, task_id="missing-task")
    with pytest.raises(IntegrityError):
        _insert_request(migration_engine, revision=-1)
    with pytest.raises(IntegrityError):
        _insert_request(migration_engine, status="unknown")
    with pytest.raises(IntegrityError):
        _insert_request(migration_engine, reason_summary=" ")
    with pytest.raises(IntegrityError):
        _insert_request(migration_engine, resolution_type="submit_correction")
    _insert_request(migration_engine)
    with pytest.raises(IntegrityError):
        _insert_request(migration_engine, action_request_id="needs-318-2")


def test_current_open_request_is_unique_and_downgrade_is_forward_only(
    migration_engine: Engine,
) -> None:
    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, "head")
    _seed_task(migration_engine)
    _insert_request(migration_engine)
    index = _index_definition(
        migration_engine, "uq_task_management_needs_input_requests_open_task"
    )
    assert "CREATE UNIQUE INDEX" in index
    assert "(status = 'open'::text)" in index
    with pytest.raises(IntegrityError):
        _insert_request(migration_engine, action_request_id="needs-318-2")
    with pytest.raises(RuntimeError, match="forward-fix-only"):
        command.downgrade(config, PREVIOUS_HEAD)
    assert _version_rows(migration_engine) == [HEAD_REVISION]
