"""Bounded real-PostgreSQL verification for the MVP0-010B1 Source tables.

The suite is opt-in because the default test lane blocks network access.  It
uses one fixed, test-owned schema and removes that schema during teardown; no
shared Business or Checkpoint table is touched.  Each test resets that schema
instead of downgrading the forward-only Task migration.
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
BUSINESS_SCHEMA = "mvp0_010b1_migration"
BASELINE_REVISION = "0001_business_baseline"
TASK_HEAD_REVISION = "0002_task_management"
HEAD_REVISION = "0003_source_evidence"
DATABASE_URL_ENV = "MVP0_MIGRATION_DATABASE_URL"
DOMAIN_TABLES = (
    "source_evidence_source_version_processing",
    "source_evidence_source_versions",
    "source_evidence_sources",
    "source_evidence_task_source_associations",
    "task_management_runs",
    "task_management_stages",
    "task_management_tasks",
)
SOURCE_TABLE = "source_evidence_sources"
SOURCE_VERSION_TABLE = "source_evidence_source_versions"
PROCESSING_TABLE = "source_evidence_source_version_processing"
ASSOCIATION_TABLE = "source_evidence_task_source_associations"


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
    """Own and remove exactly the fixed MVP0-010B1 verification schema."""

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
        assert remaining == 0, "MVP0-010B1 test schema cleanup was not verifiable"
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
    """The production lineage has one Source head and a Task parent."""

    script = ScriptDirectory.from_config(_config(_database_url()))
    assert script.get_heads() == [HEAD_REVISION]
    head = script.get_revision(HEAD_REVISION)
    assert head is not None
    assert head.down_revision == TASK_HEAD_REVISION
    task_head = script.get_revision(TASK_HEAD_REVISION)
    assert task_head is not None
    assert task_head.down_revision == BASELINE_REVISION
    baseline = script.get_revision(BASELINE_REVISION)
    assert baseline is not None
    assert baseline.down_revision is None


def test_fresh_upgrade_reaches_task_head(
    migration_engine: Engine,
) -> None:
    """A fresh test schema reaches the single head and creates all tables."""

    _reset_schema(migration_engine)
    command.upgrade(_config(_database_url()), "head")

    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]


def test_explicit_baseline_to_head_upgrade(
    migration_engine: Engine,
) -> None:
    """A schema explicitly at 0001 can advance to the Source head."""

    _reset_schema(migration_engine)
    config = _config(_database_url())
    command.upgrade(config, BASELINE_REVISION)
    assert _version_rows(migration_engine) == [BASELINE_REVISION]
    assert _tables(migration_engine) == ["alembic_version"]

    command.upgrade(config, HEAD_REVISION)
    assert _version_rows(migration_engine) == [HEAD_REVISION]
    assert _tables(migration_engine) == ["alembic_version", *DOMAIN_TABLES]


def test_existing_task_head_to_source_head_upgrade(
    migration_engine: Engine,
) -> None:
    """A schema at the current Task head advances with one Source revision."""

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


def test_alembic_current_check_and_offline_sql_are_reviewable(
    migration_engine: Engine,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Current, drift check, and offline SQL identify the Task revision."""

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
            "mvp0_010b1_failed_probe",
            sa.Column("id", sa.Integer, primary_key=True),
            schema=BUSINESS_SCHEMA,
        )
        raise InjectedMigrationFailure("representative test-only migration failure")


def _run_test_only_forward_repair(engine: Engine) -> None:
    """Repair the failed test path with a new transaction, not a rewrite."""

    with engine.begin() as connection:
        operations = Operations(MigrationContext.configure(connection))
        operations.create_table(
            "mvp0_010b1_failed_probe",
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

    assert not _table_exists(migration_engine, "mvp0_010b1_failed_probe")
    _run_test_only_forward_repair(migration_engine)
    assert _table_exists(migration_engine, "mvp0_010b1_failed_probe")
    assert _version_rows(migration_engine) == [HEAD_REVISION]
