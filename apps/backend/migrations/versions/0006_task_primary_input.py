"""Add the minimal Task-scoped primary-input Current Truth table.

The table stores exactly one current pasted/TXT/Markdown input per Task.  It
is additive, has no backfill, and is forward-fix-only like the existing
Business migration lineage.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006_task_primary_input"
down_revision: str | None = "0005_dispatch_supersession"
branch_labels: Sequence[str] | None = None
depends_on: str | None = None

OWNER = "Fast Lane Task Primary Input (Issue #249)"
AFFECTED_TABLES: tuple[str, ...] = (
    "task_management_create_idempotency",
    "source_evidence_task_primary_inputs",
)
REVISION_CLASSIFICATION = "FORWARD_FIX_ONLY"
UPGRADE_STRATEGY = (
    "Create additive Task idempotency and Task-scoped current primary-input tables"
)
DOWNGRADE_CLASSIFICATION = "Unsupported; use a forward repair revision"
COMPATIBILITY_WINDOW = "New table is unused by older runtimes"
DATA_LOSS_RISK = "None on upgrade; downgrade is intentionally unsupported"
LOCK_RISK = "Short transactional table and named constraint creation"
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
    "SELECT table_name FROM information_schema.tables WHERE table_schema = "
    "<business_schema> AND table_name IN ("
    "'task_management_create_idempotency',"
    "'source_evidence_task_primary_inputs')"
)
RECOVERY_STRATEGY = (
    "Forward-recovery-first; preserve this revision and repair with a later "
    "Forward Repair revision"
)
REQUIRED_APPLICATION_VERSION = "MVP0-FL1A"
RELATED_DQ_DEC_RFC = "DEC-078; Issue #249"

_INPUT_KINDS = ("pasted_text", "text_file", "markdown_file")


def _schema() -> str:
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
    """Create the idempotency and current-input tables without touching rows."""

    schema = _schema()
    kinds = ", ".join(f"'{value}'" for value in _INPUT_KINDS)
    op.create_table(
        "task_management_create_idempotency",
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint(
            "idempotency_key", name="pk_task_management_create_idempotency"
        ),
        sa.UniqueConstraint(
            "task_id", name="uq_task_management_create_idempotency_task"
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            [f"{schema}.task_management_tasks.task_id"],
            name="fk_task_management_create_idempotency_task_owner",
        ),
        sa.CheckConstraint(
            "length(btrim(idempotency_key)) > 0",
            name="ck_task_management_create_idempotency_key_nonempty",
        ),
        schema=schema,
    )
    op.create_table(
        "source_evidence_task_primary_inputs",
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.Column("input_kind", sa.Text(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("byte_count", sa.BigInteger(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "task_id", name="pk_source_evidence_task_primary_inputs"
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            [f"{schema}.task_management_tasks.task_id"],
            name="fk_source_evidence_task_primary_inputs_task_owner",
        ),
        sa.CheckConstraint(
            f"input_kind IN ({kinds})",
            name="ck_source_evidence_task_primary_inputs_kind",
        ),
        sa.CheckConstraint(
            "length(btrim(content)) > 0",
            name="ck_source_evidence_task_primary_inputs_content_nonempty",
        ),
        sa.CheckConstraint(
            "byte_count >= 1 AND byte_count <= 1048576",
            name="ck_source_evidence_task_primary_inputs_byte_count",
        ),
        sa.CheckConstraint(
            "revision >= 0",
            name="ck_source_evidence_task_primary_inputs_revision_nonnegative",
        ),
        sa.CheckConstraint(
            "(input_kind = 'pasted_text' AND file_name IS NULL) OR "
            "(input_kind <> 'pasted_text' AND file_name IS NOT NULL)",
            name="ck_source_evidence_task_primary_inputs_filename_pair",
        ),
        schema=schema,
    )


def downgrade() -> None:
    """Reject destructive rollback; repair with a later forward revision."""

    raise RuntimeError(
        "0006_task_primary_input is forward-fix-only; use a new forward repair "
        "revision instead of destructive downgrade"
    )
