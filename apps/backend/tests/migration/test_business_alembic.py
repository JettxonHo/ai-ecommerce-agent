"""Bounded real-PostgreSQL verification for the MVP0-008 baseline.

The suite is opt-in because the default test lane blocks network access.  It
uses one fixed, test-owned schema and removes that schema during teardown;
no shared Business or Checkpoint table is touched.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text

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
BUSINESS_SCHEMA = "mvp0_008_migration"
BASELINE_REVISION = "0001_business_baseline"
DATABASE_URL_ENV = "MVP0_MIGRATION_DATABASE_URL"


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
    """Own and remove exactly the fixed MVP0-008 verification schema."""

    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=_database_url(),
            pool_size=1,
            max_overflow=0,
            pool_timeout=2,
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{BUSINESS_SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{BUSINESS_SCHEMA}"'))
    try:
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(
                text(f'DROP SCHEMA IF EXISTS "{BUSINESS_SCHEMA}" CASCADE')
            )
        with engine.connect() as connection:
            remaining = connection.scalar(
                text("SELECT count(*) FROM pg_namespace WHERE nspname = :schema"),
                {"schema": BUSINESS_SCHEMA},
            )
        assert remaining == 0, "MVP0-008 test schema cleanup was not verifiable"
        engine.dispose()


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


def test_revision_graph_has_one_business_head() -> None:
    """The production lineage has one head and a detached baseline parent."""

    script = ScriptDirectory.from_config(_config(_database_url()))
    assert script.get_heads() == [BASELINE_REVISION]
    revision = script.get_revision(BASELINE_REVISION)
    assert revision is not None
    assert revision.down_revision is None


def test_fresh_upgrade_creates_only_migration_identity(
    migration_engine: Engine,
) -> None:
    """Fresh PostgreSQL schema reaches head without any future Business table."""

    command.upgrade(_config(_database_url()), "head")

    assert _version_rows(migration_engine) == [BASELINE_REVISION]
    with migration_engine.connect() as connection:
        tables = list(
            connection.scalars(
                text(
                    "SELECT tablename FROM pg_tables "
                    "WHERE schemaname = :schema ORDER BY tablename"
                ),
                {"schema": BUSINESS_SCHEMA},
            )
        )
    assert tables == ["alembic_version"]


def test_supported_base_to_head_and_current_revision(
    migration_engine: Engine,
) -> None:
    """A supported base can upgrade one step and expose current Alembic ID."""

    config = _config(_database_url())
    command.downgrade(config, "base")
    # Alembic may retain its empty identity table at base; either physical
    # representation is valid as long as no revision remains applied.
    if _table_exists(migration_engine, "alembic_version"):
        assert _version_rows(migration_engine) == []

    command.upgrade(config, "head")
    assert _version_rows(migration_engine) == [BASELINE_REVISION]
    command.current(config)


def test_alembic_check_and_offline_sql_are_reviewable(
    migration_engine: Engine,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Drift check is clean and offline output identifies the baseline."""

    config = _config(_database_url())
    command.check(config)
    command.upgrade(config, "head", sql=True)
    output = capsys.readouterr().out

    assert "CREATE TABLE" in output
    assert "alembic_version" in output
    assert BASELINE_REVISION in output


def _run_test_only_failure_path(engine: Engine) -> None:
    """Create a probe with Alembic Operations, then fail its transaction."""

    with engine.begin() as connection:
        operations = Operations(MigrationContext.configure(connection))
        operations.create_table(
            "mvp0_008_failed_probe",
            sa.Column("id", sa.Integer, primary_key=True),
            schema=BUSINESS_SCHEMA,
        )
        raise InjectedMigrationFailure("representative test-only migration failure")


def _run_test_only_forward_repair(engine: Engine) -> None:
    """Repair the failed test path with a new transaction, not a rewrite."""

    with engine.begin() as connection:
        operations = Operations(MigrationContext.configure(connection))
        operations.create_table(
            "mvp0_008_failed_probe",
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

    config = _config(_database_url())
    command.upgrade(config, "head")
    with pytest.raises(InjectedMigrationFailure):
        _run_test_only_failure_path(migration_engine)

    assert not _table_exists(migration_engine, "mvp0_008_failed_probe")
    _run_test_only_forward_repair(migration_engine)
    assert _table_exists(migration_engine, "mvp0_008_failed_probe")
    assert _version_rows(migration_engine) == [BASELINE_REVISION]
