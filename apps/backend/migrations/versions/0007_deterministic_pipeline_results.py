"""Add the Task-owned deterministic Fast Lane current-result table.

The table is additive and empty on upgrade.  A result is one atomic row bound
to one Task and one persisted primary-input revision; no existing rows are
rewritten and downgrade remains forward-fix-only.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007_deterministic_result"
down_revision: str | None = "0006_task_primary_input"
branch_labels: Sequence[str] | None = None
depends_on: str | None = None


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
    """Create the empty Task-owned current-result table."""

    schema = _schema()
    op.create_table(
        "task_management_deterministic_results",
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.Column("result_revision", sa.BigInteger(), nullable=False),
        sa.Column("input_revision", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("missing_information", sa.Text(), nullable=False),
        sa.Column("product_intake", sa.Text(), nullable=True),
        sa.Column("customer_insight", sa.Text(), nullable=True),
        sa.Column("product_positioning", sa.Text(), nullable=True),
        sa.Column("marketing_brief", sa.Text(), nullable=True),
        sa.Column("xiaohongshu_brief", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint(
            "task_id",
            "result_revision",
            name="pk_task_management_deterministic_results",
        ),
        sa.UniqueConstraint(
            "task_id",
            "input_revision",
            name="uq_task_management_results_task_input",
        ),
        sa.UniqueConstraint(
            "task_id",
            "idempotency_key",
            name="uq_task_management_results_task_key",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            [f"{schema}.task_management_tasks.task_id"],
            name="fk_task_management_results_task_owner",
        ),
        sa.CheckConstraint(
            "length(btrim(task_id)) > 0",
            name="ck_task_management_results_task_id_nonempty",
        ),
        sa.CheckConstraint(
            "length(btrim(idempotency_key)) > 0",
            name="ck_task_management_results_key_nonempty",
        ),
        sa.CheckConstraint(
            "result_revision >= 0",
            name="ck_task_management_results_result_revision_nonnegative",
        ),
        sa.CheckConstraint(
            "input_revision >= 0",
            name="ck_task_management_results_input_revision_nonnegative",
        ),
        sa.CheckConstraint(
            "status IN ('awaiting_review', 'insufficient_input')",
            name="ck_task_management_results_status",
        ),
        sa.CheckConstraint(
            "length(btrim(missing_information)) > 0",
            name="ck_task_management_results_missing_information_nonempty",
        ),
        schema=schema,
    )


def downgrade() -> None:
    """Reject destructive rollback; repair with a later forward revision."""

    raise RuntimeError(
        "0007_deterministic_result is forward-fix-only; use a new "
        "forward repair revision instead of destructive downgrade"
    )
