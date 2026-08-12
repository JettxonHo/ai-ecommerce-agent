"""Logical-schema SQLAlchemy Core tables owned by Task Management."""

from __future__ import annotations

import re

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    MetaData,
    PrimaryKeyConstraint,
    Table,
    Text,
    UniqueConstraint,
)

TASK_MANAGEMENT_SCHEMA_TOKEN = "__task_management_schema__"
TASK_MANAGEMENT_METADATA = MetaData()
_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")
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


def _in(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN ({', '.join(repr(value) for value in values)})"


def _schema(name: str) -> str:
    if not _IDENTIFIER.fullmatch(name):
        raise ValueError("schema must be a lowercase PostgreSQL identifier")
    return name


TASKS_TABLE = Table(
    "task_management_tasks",
    TASK_MANAGEMENT_METADATA,
    Column("task_id", Text(), nullable=False),
    Column("task_name", Text(), nullable=False),
    Column("product_category", Text(), nullable=False),
    Column("promotion_goal", Text(), nullable=False),
    Column("task_status", Text(), nullable=False),
    Column("revision", BigInteger(), nullable=False),
    Column("current_stage", Text()),
    Column("active_run_id", Text()),
    Column("latest_run_id", Text()),
    Column("waiting_reason", Text()),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    PrimaryKeyConstraint("task_id", name="pk_task_management_tasks"),
    CheckConstraint(
        "length(btrim(task_id)) > 0", name="ck_task_management_tasks_task_id_nonempty"
    ),
    CheckConstraint(
        _in("task_status", _TASK_STATUSES), name="ck_task_management_tasks_status"
    ),
    CheckConstraint(
        "revision >= 0", name="ck_task_management_tasks_revision_nonnegative"
    ),
    CheckConstraint(
        f"current_stage IS NULL OR {_in('current_stage', _STAGES)}",
        name="ck_task_management_tasks_current_stage",
    ),
    CheckConstraint(
        "active_run_id IS NULL OR length(btrim(active_run_id)) > 0",
        name="ck_task_management_tasks_active_run_id_nonempty",
    ),
    CheckConstraint(
        "latest_run_id IS NULL OR length(btrim(latest_run_id)) > 0",
        name="ck_task_management_tasks_latest_run_id_nonempty",
    ),
    schema=TASK_MANAGEMENT_SCHEMA_TOKEN,
)

TASK_CREATE_IDEMPOTENCY_TABLE = Table(
    "task_management_create_idempotency",
    TASK_MANAGEMENT_METADATA,
    Column("idempotency_key", Text(), nullable=False),
    Column("task_id", Text(), nullable=False),
    PrimaryKeyConstraint(
        "idempotency_key", name="pk_task_management_create_idempotency"
    ),
    UniqueConstraint("task_id", name="uq_task_management_create_idempotency_task"),
    ForeignKeyConstraint(
        ["task_id"],
        [f"{TASK_MANAGEMENT_SCHEMA_TOKEN}.task_management_tasks.task_id"],
        name="fk_task_management_create_idempotency_task_owner",
    ),
    CheckConstraint(
        "length(btrim(idempotency_key)) > 0",
        name="ck_task_management_create_idempotency_key_nonempty",
    ),
    schema=TASK_MANAGEMENT_SCHEMA_TOKEN,
)

RUNS_TABLE = Table(
    "task_management_runs",
    TASK_MANAGEMENT_METADATA,
    Column("run_id", Text(), nullable=False),
    Column("task_id", Text(), nullable=False),
    Column("source_run_id", Text()),
    Column("status", Text(), nullable=False),
    Column("revision", BigInteger(), nullable=False),
    Column("current_stage", Text()),
    Column("started_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    Column("failure_summary", Text()),
    Column("last_valid_result_version_id", Text()),
    Column("last_valid_result_version_number", BigInteger()),
    PrimaryKeyConstraint("run_id", name="pk_task_management_runs"),
    UniqueConstraint("task_id", "run_id", name="uq_task_management_runs_task_run"),
    ForeignKeyConstraint(
        ["task_id"],
        [f"{TASK_MANAGEMENT_SCHEMA_TOKEN}.task_management_tasks.task_id"],
        name="fk_task_management_runs_task_owner",
    ),
    ForeignKeyConstraint(
        ["task_id", "source_run_id"],
        [
            f"{TASK_MANAGEMENT_SCHEMA_TOKEN}.task_management_runs.task_id",
            f"{TASK_MANAGEMENT_SCHEMA_TOKEN}.task_management_runs.run_id",
        ],
        name="fk_task_management_runs_source_owner",
    ),
    CheckConstraint(
        "length(btrim(run_id)) > 0", name="ck_task_management_runs_run_id_nonempty"
    ),
    CheckConstraint(
        "length(btrim(task_id)) > 0", name="ck_task_management_runs_task_id_nonempty"
    ),
    CheckConstraint(
        "source_run_id IS NULL OR source_run_id <> run_id",
        name="ck_task_management_runs_source_distinct",
    ),
    CheckConstraint(
        _in("status", _RUN_STATUSES), name="ck_task_management_runs_status"
    ),
    CheckConstraint(
        "revision >= 0", name="ck_task_management_runs_revision_nonnegative"
    ),
    CheckConstraint(
        f"current_stage IS NULL OR {_in('current_stage', _STAGES)}",
        name="ck_task_management_runs_current_stage",
    ),
    CheckConstraint(
        "(last_valid_result_version_id IS NULL AND "
        "last_valid_result_version_number IS NULL) OR "
        "(last_valid_result_version_id IS NOT NULL AND "
        "last_valid_result_version_number IS NOT NULL "
        "AND last_valid_result_version_number >= 1)",
        name="ck_task_management_runs_last_valid_result_pair",
    ),
    schema=TASK_MANAGEMENT_SCHEMA_TOKEN,
)

STAGES_TABLE = Table(
    "task_management_stages",
    TASK_MANAGEMENT_METADATA,
    Column("task_id", Text(), nullable=False),
    Column("stage", Text(), nullable=False),
    Column("status", Text(), nullable=False),
    Column("revision", BigInteger(), nullable=False),
    Column("current_version_id", Text()),
    Column("current_version_number", BigInteger()),
    Column("last_valid_version_id", Text()),
    Column("last_valid_version_number", BigInteger()),
    Column("last_run_id", Text()),
    Column("waiting_reason", Text()),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    PrimaryKeyConstraint("task_id", "stage", name="pk_task_management_stages"),
    ForeignKeyConstraint(
        ["task_id"],
        [f"{TASK_MANAGEMENT_SCHEMA_TOKEN}.task_management_tasks.task_id"],
        name="fk_task_management_stages_task_owner",
    ),
    ForeignKeyConstraint(
        ["task_id", "last_run_id"],
        [
            f"{TASK_MANAGEMENT_SCHEMA_TOKEN}.task_management_runs.task_id",
            f"{TASK_MANAGEMENT_SCHEMA_TOKEN}.task_management_runs.run_id",
        ],
        name="fk_task_management_stages_last_run_owner",
    ),
    CheckConstraint(
        "length(btrim(task_id)) > 0", name="ck_task_management_stages_task_id_nonempty"
    ),
    CheckConstraint(_in("stage", _STAGES), name="ck_task_management_stages_stage"),
    CheckConstraint(
        _in("status", _STAGE_STATUSES), name="ck_task_management_stages_status"
    ),
    CheckConstraint(
        "revision >= 0", name="ck_task_management_stages_revision_nonnegative"
    ),
    CheckConstraint(
        "(current_version_id IS NULL AND current_version_number IS NULL) OR "
        "(current_version_id IS NOT NULL AND "
        "current_version_number IS NOT NULL AND current_version_number >= 1)",
        name="ck_task_management_stages_current_version_pair",
    ),
    CheckConstraint(
        "(last_valid_version_id IS NULL AND last_valid_version_number IS NULL) OR "
        "(last_valid_version_id IS NOT NULL AND "
        "last_valid_version_number IS NOT NULL AND last_valid_version_number >= 1)",
        name="ck_task_management_stages_last_valid_version_pair",
    ),
    CheckConstraint(
        "last_run_id IS NULL OR length(btrim(last_run_id)) > 0",
        name="ck_task_management_stages_last_run_id_nonempty",
    ),
    schema=TASK_MANAGEMENT_SCHEMA_TOKEN,
)


# Keep the cyclic nullable owner pointers out-of-line, matching the migration.
for columns, target, name in (
    (
        ["task_id", "current_stage"],
        "task_management_stages|task_id|stage",
        "fk_task_management_tasks_current_stage_owner",
    ),
    (
        ["task_id", "active_run_id"],
        "task_management_runs|task_id|run_id",
        "fk_task_management_tasks_active_run_owner",
    ),
    (
        ["task_id", "latest_run_id"],
        "task_management_runs|task_id|run_id",
        "fk_task_management_tasks_latest_run_owner",
    ),
    (
        ["task_id", "current_stage"],
        "task_management_stages|task_id|stage",
        "fk_task_management_runs_current_stage_owner",
    ),
):
    table = RUNS_TABLE if name.startswith("fk_task_management_runs_") else TASKS_TABLE
    parts = target.split("|")
    table.append_constraint(
        ForeignKeyConstraint(
            columns,
            [
                f"{TASK_MANAGEMENT_SCHEMA_TOKEN}.{parts[0]}.{column}"
                for column in parts[1:]
            ],
            name=name,
        )
    )


def schema_translate_map(schema: str) -> dict[str, str]:
    """Return the explicit map from logical metadata token to real schema."""

    return {TASK_MANAGEMENT_SCHEMA_TOKEN: _schema(schema)}


__all__ = [
    "RUNS_TABLE",
    "STAGES_TABLE",
    "TASKS_TABLE",
    "TASK_CREATE_IDEMPOTENCY_TABLE",
    "TASK_MANAGEMENT_METADATA",
    "TASK_MANAGEMENT_SCHEMA_TOKEN",
    "schema_translate_map",
]
