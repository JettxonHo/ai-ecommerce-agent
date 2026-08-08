"""Create the Task Management Business Current Truth tables.

This is the first non-empty Business revision.  The three tables are owned by
the Task Management module; no Runtime or vendor Checkpoint tables belong to
this Alembic lineage.  The revision is intentionally forward-repair-only:
production recovery must keep an expanded schema and use a later repair
revision rather than relying on a destructive downgrade.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_task_management"
down_revision: str | None = "0001_business_baseline"
branch_labels: Sequence[str] | None = None
depends_on: str | None = None

OWNER = "Task Management Persistence (MVP0-009B)"
AFFECTED_TABLES: tuple[str, ...] = (
    "task_management_tasks",
    "task_management_runs",
    "task_management_stages",
)
REVISION_CLASSIFICATION = "FORWARD_FIX_ONLY"
UPGRADE_STRATEGY = "Create Task, Run, and Stage Current Truth tables"
DOWNGRADE_CLASSIFICATION = "Unsupported; use a forward repair revision"
COMPATIBILITY_WINDOW = "Additive first Business schema; no prior aggregate tables"
DATA_LOSS_RISK = "None on upgrade; downgrade is intentionally unsupported"
LOCK_RISK = "Short transactional table and constraint creation"
LOCK_TIMEOUT = "Not overridden; migration operator owns timeout policy"
STATEMENT_TIMEOUT = "Not overridden; migration operator owns timeout policy"
DDL_TRANSACTION_BOUNDARY = (
    "Alembic transaction_per_migration=True; PostgreSQL DDL is transactional"
)
REWRITE_RISK = "None; no existing Business rows are rewritten"
BACKFILL_REQUIREMENT = "None"
DESTRUCTIVE_OPERATION = "None on upgrade; no destructive downgrade"
NON_TRANSACTIONAL_OPERATION = "None"
VERIFICATION_QUERY = (
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema = <business_schema> "
    "AND table_name IN ("
    "'task_management_tasks','task_management_runs','task_management_stages')"
)
RECOVERY_STRATEGY = (
    "Forward-recovery-first; preserve this revision and repair with a new "
    "Forward Repair revision"
)
REQUIRED_APPLICATION_VERSION = "MVP0-009B"
RELATED_DQ_DEC_RFC = "RFC-001 DQ-03/04; RFC-002 DQ-02/04/05/06/07/14/16; Issue #88"

_STAGES = (
    "product_intake_and_fact_extraction",
    "customer_insight_analysis",
    "product_positioning",
    "human_review",
    "marketing_brief_generation",
    "xiaohongshu_brief_mapping",
)
_TASK_STATUSES = (
    "draft",
    "running",
    "waiting_for_input",
    "waiting_for_review",
    "paused",
    "completed",
    "failed",
    "cancelled",
)
_RUN_STATUSES = (
    "queued",
    "running",
    "retrying",
    "waiting_for_input",
    "waiting_for_review",
    "paused",
    "cancellation_requested",
    "completed",
    "failed",
    "cancelled",
    "superseded",
)
_STAGE_STATUSES = (
    "not_started",
    "ready",
    "running",
    "waiting_input",
    "waiting_review",
    "valid",
    "invalid",
    "failed",
    "skipped",
)


def _in_check(column: str, values: tuple[str, ...]) -> str:
    """Render a stable SQL check for a finite public catalog."""

    rendered = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({rendered})"


def _schema() -> str:
    """Read the explicit Business/version schema selected by Alembic.

    ``env.py`` requires these two settings to agree, but accepting either one
    here keeps direct revision execution schema-safe while never consulting
    Checkpoint or vendor migration settings.
    """

    config = op.get_context().config
    business_schema = (config.get_main_option("business_schema") or "").strip()
    version_schema = (config.get_main_option("version_table_schema") or "").strip()
    if business_schema and version_schema and business_schema != version_schema:
        raise ValueError(
            "business_schema and version_table_schema must identify the same "
            "Business migration schema"
        )
    return business_schema or version_schema or "public"


def upgrade() -> None:
    """Create all three tables and then close their ownership cycle."""

    schema = _schema()

    # Task is created first so Run and Stage can enforce their owner with a
    # simple FK.  Task's nullable current/latest pointers are added after the
    # target tables exist and use composite owner keys.
    op.create_table(
        "task_management_tasks",
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.Column("task_name", sa.Text(), nullable=False),
        sa.Column("product_category", sa.Text(), nullable=False),
        sa.Column("promotion_goal", sa.Text(), nullable=False),
        sa.Column("task_status", sa.Text(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("current_stage", sa.Text(), nullable=True),
        sa.Column("active_run_id", sa.Text(), nullable=True),
        sa.Column("latest_run_id", sa.Text(), nullable=True),
        sa.Column("waiting_reason", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("task_id", name="pk_task_management_tasks"),
        sa.CheckConstraint(
            "length(btrim(task_id)) > 0",
            name="ck_task_management_tasks_task_id_nonempty",
        ),
        sa.CheckConstraint(
            _in_check("task_status", _TASK_STATUSES),
            name="ck_task_management_tasks_status",
        ),
        sa.CheckConstraint(
            "revision >= 0",
            name="ck_task_management_tasks_revision_nonnegative",
        ),
        sa.CheckConstraint(
            f"current_stage IS NULL OR {_in_check('current_stage', _STAGES)}",
            name="ck_task_management_tasks_current_stage",
        ),
        sa.CheckConstraint(
            "active_run_id IS NULL OR length(btrim(active_run_id)) > 0",
            name="ck_task_management_tasks_active_run_id_nonempty",
        ),
        sa.CheckConstraint(
            "latest_run_id IS NULL OR length(btrim(latest_run_id)) > 0",
            name="ck_task_management_tasks_latest_run_id_nonempty",
        ),
        schema=schema,
    )

    op.create_table(
        "task_management_runs",
        sa.Column("run_id", sa.Text(), nullable=False),
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.Column("source_run_id", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("current_stage", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_summary", sa.Text(), nullable=True),
        sa.Column("last_valid_result_version_id", sa.Text(), nullable=True),
        sa.Column("last_valid_result_version_number", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("run_id", name="pk_task_management_runs"),
        sa.UniqueConstraint(
            "task_id",
            "run_id",
            name="uq_task_management_runs_task_run",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            [f"{schema}.task_management_tasks.task_id"],
            name="fk_task_management_runs_task_owner",
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "source_run_id"],
            [
                f"{schema}.task_management_runs.task_id",
                f"{schema}.task_management_runs.run_id",
            ],
            name="fk_task_management_runs_source_owner",
        ),
        sa.CheckConstraint(
            "length(btrim(run_id)) > 0",
            name="ck_task_management_runs_run_id_nonempty",
        ),
        sa.CheckConstraint(
            "length(btrim(task_id)) > 0",
            name="ck_task_management_runs_task_id_nonempty",
        ),
        sa.CheckConstraint(
            "source_run_id IS NULL OR source_run_id <> run_id",
            name="ck_task_management_runs_source_distinct",
        ),
        sa.CheckConstraint(
            _in_check("status", _RUN_STATUSES),
            name="ck_task_management_runs_status",
        ),
        sa.CheckConstraint(
            "revision >= 0",
            name="ck_task_management_runs_revision_nonnegative",
        ),
        sa.CheckConstraint(
            f"current_stage IS NULL OR {_in_check('current_stage', _STAGES)}",
            name="ck_task_management_runs_current_stage",
        ),
        sa.CheckConstraint(
            "(last_valid_result_version_id IS NULL AND "
            "last_valid_result_version_number IS NULL) OR "
            "(last_valid_result_version_id IS NOT NULL AND "
            "last_valid_result_version_number IS NOT NULL AND "
            "last_valid_result_version_number >= 1)",
            name="ck_task_management_runs_last_valid_result_pair",
        ),
        schema=schema,
    )

    op.create_table(
        "task_management_stages",
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.Column("stage", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("current_version_id", sa.Text(), nullable=True),
        sa.Column("current_version_number", sa.BigInteger(), nullable=True),
        sa.Column("last_valid_version_id", sa.Text(), nullable=True),
        sa.Column("last_valid_version_number", sa.BigInteger(), nullable=True),
        sa.Column("last_run_id", sa.Text(), nullable=True),
        sa.Column("waiting_reason", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "task_id",
            "stage",
            name="pk_task_management_stages",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            [f"{schema}.task_management_tasks.task_id"],
            name="fk_task_management_stages_task_owner",
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "last_run_id"],
            [
                f"{schema}.task_management_runs.task_id",
                f"{schema}.task_management_runs.run_id",
            ],
            name="fk_task_management_stages_last_run_owner",
        ),
        sa.CheckConstraint(
            "length(btrim(task_id)) > 0",
            name="ck_task_management_stages_task_id_nonempty",
        ),
        sa.CheckConstraint(
            _in_check("stage", _STAGES),
            name="ck_task_management_stages_stage",
        ),
        sa.CheckConstraint(
            _in_check("status", _STAGE_STATUSES),
            name="ck_task_management_stages_status",
        ),
        sa.CheckConstraint(
            "revision >= 0",
            name="ck_task_management_stages_revision_nonnegative",
        ),
        sa.CheckConstraint(
            "(current_version_id IS NULL AND current_version_number IS NULL) OR "
            "(current_version_id IS NOT NULL AND "
            "current_version_number IS NOT NULL AND current_version_number >= 1)",
            name="ck_task_management_stages_current_version_pair",
        ),
        sa.CheckConstraint(
            "(last_valid_version_id IS NULL AND last_valid_version_number IS NULL) OR "
            "(last_valid_version_id IS NOT NULL AND "
            "last_valid_version_number IS NOT NULL AND last_valid_version_number >= 1)",
            name="ck_task_management_stages_last_valid_version_pair",
        ),
        sa.CheckConstraint(
            "last_run_id IS NULL OR length(btrim(last_run_id)) > 0",
            name="ck_task_management_stages_last_run_id_nonempty",
        ),
        schema=schema,
    )

    # These nullable pointers close the ownership cycle only after both target
    # tables exist.  A pointer from Task to another Task's Run/Stage therefore
    # fails in PostgreSQL instead of relying on an application pre-check.
    op.create_foreign_key(
        "fk_task_management_tasks_current_stage_owner",
        "task_management_tasks",
        "task_management_stages",
        ["task_id", "current_stage"],
        ["task_id", "stage"],
        source_schema=schema,
        referent_schema=schema,
    )
    op.create_foreign_key(
        "fk_task_management_tasks_active_run_owner",
        "task_management_tasks",
        "task_management_runs",
        ["task_id", "active_run_id"],
        ["task_id", "run_id"],
        source_schema=schema,
        referent_schema=schema,
    )
    op.create_foreign_key(
        "fk_task_management_tasks_latest_run_owner",
        "task_management_tasks",
        "task_management_runs",
        ["task_id", "latest_run_id"],
        ["task_id", "run_id"],
        source_schema=schema,
        referent_schema=schema,
    )
    op.create_foreign_key(
        "fk_task_management_runs_current_stage_owner",
        "task_management_runs",
        "task_management_stages",
        ["task_id", "current_stage"],
        ["task_id", "stage"],
        source_schema=schema,
        referent_schema=schema,
    )


def downgrade() -> None:
    """Reject destructive rollback; repair the schema with a new revision."""

    raise RuntimeError(
        "0002_task_management is forward-fix-only; use a new forward repair "
        "revision instead of destructive downgrade"
    )
