"""Add one-shot current-result confirmation and immutable Markdown snapshots.

The revision is additive.  Existing deterministic result rows remain intact;
only the accepted ``confirmed`` state and nullable confirmation metadata are
introduced.  Export content is stored as UTF-8 text so a later download never
re-renders or changes an immutable snapshot.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008_review_export"
down_revision: str | None = "0007_deterministic_result"
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
    """Extend current results and create the narrow immutable snapshot table."""

    schema = _schema()
    result_table = "task_management_deterministic_results"

    for column in (
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("confirmation_idempotency_key", sa.Text()),
        sa.Column("confirmed_marketing_core_message", sa.Text()),
        sa.Column("confirmed_xiaohongshu_title_direction", sa.Text()),
        sa.Column("marketing_brief_version_id", sa.Text()),
        sa.Column("marketing_brief_version_number", sa.BigInteger()),
        sa.Column("xiaohongshu_brief_version_id", sa.Text()),
        sa.Column("xiaohongshu_brief_version_number", sa.BigInteger()),
    ):
        op.add_column(result_table, column, schema=schema)

    op.drop_constraint(
        "ck_task_management_results_status",
        table_name=result_table,
        schema=schema,
        type_="check",
    )
    op.create_check_constraint(
        "ck_task_management_results_status",
        result_table,
        "status IN ('awaiting_review', 'insufficient_input', 'confirmed')",
        schema=schema,
    )
    op.create_unique_constraint(
        "uq_task_management_results_task_confirmation_key",
        result_table,
        ["task_id", "confirmation_idempotency_key"],
        schema=schema,
    )
    op.create_check_constraint(
        "ck_task_management_results_confirmation_projection",
        result_table,
        "((status = 'confirmed' AND confirmed_at IS NOT NULL "
        "AND length(btrim(confirmation_idempotency_key)) > 0 "
        "AND length(btrim(confirmed_marketing_core_message)) > 0 "
        "AND length(btrim(confirmed_xiaohongshu_title_direction)) > 0 "
        "AND length(btrim(marketing_brief_version_id)) > 0 "
        "AND marketing_brief_version_number >= 1 "
        "AND length(btrim(xiaohongshu_brief_version_id)) > 0 "
        "AND xiaohongshu_brief_version_number >= 1) OR "
        "(status <> 'confirmed' AND confirmed_at IS NULL "
        "AND confirmation_idempotency_key IS NULL "
        "AND confirmed_marketing_core_message IS NULL "
        "AND confirmed_xiaohongshu_title_direction IS NULL "
        "AND marketing_brief_version_id IS NULL "
        "AND marketing_brief_version_number IS NULL "
        "AND xiaohongshu_brief_version_id IS NULL "
        "AND xiaohongshu_brief_version_number IS NULL))",
        schema=schema,
    )
    op.create_check_constraint(
        "ck_task_management_results_confirmation_size",
        result_table,
        "((confirmed_marketing_core_message IS NULL OR octet_length(confirmed_marketing_core_message) <= 4096) "
        "AND (confirmed_xiaohongshu_title_direction IS NULL OR octet_length(confirmed_xiaohongshu_title_direction) <= 4096))",
        schema=schema,
    )

    op.create_table(
        "task_management_export_snapshots",
        sa.Column("export_snapshot_id", sa.Text(), nullable=False),
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.Column("task_revision", sa.BigInteger(), nullable=False),
        sa.Column("result_revision", sa.BigInteger(), nullable=False),
        sa.Column("input_revision", sa.BigInteger(), nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=False),
        sa.Column("brief_kind", sa.Text(), nullable=False),
        sa.Column("brief_version_id", sa.Text(), nullable=False),
        sa.Column("brief_version_number", sa.BigInteger(), nullable=False),
        sa.Column("upstream_versions", sa.Text(), nullable=False),
        sa.Column("hypotheses", sa.Text(), nullable=False),
        sa.Column("evidence_limitations", sa.Text(), nullable=False),
        sa.Column("risks", sa.Text(), nullable=False),
        sa.Column("basis", sa.Text(), nullable=False),
        sa.Column("exported_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("media_type", sa.Text(), nullable=False),
        sa.Column("content_location", sa.Text(), nullable=False),
        sa.Column("template_version", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint(
            "export_snapshot_id", name="pk_task_management_export_snapshots"
        ),
        sa.UniqueConstraint(
            "task_id",
            "idempotency_key",
            name="uq_task_management_export_snapshots_task_key",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            [f"{schema}.task_management_tasks.task_id"],
            name="fk_task_management_export_snapshots_task_owner",
        ),
        sa.CheckConstraint(
            "length(btrim(export_snapshot_id)) > 0",
            name="ck_task_management_export_snapshots_id_nonempty",
        ),
        sa.CheckConstraint(
            "length(btrim(task_id)) > 0",
            name="ck_task_management_export_snapshots_task_id_nonempty",
        ),
        sa.CheckConstraint(
            "length(btrim(idempotency_key)) > 0",
            name="ck_task_management_export_snapshots_key_nonempty",
        ),
        sa.CheckConstraint(
            "brief_kind IN ('marketing', 'xiaohongshu')",
            name="ck_task_management_export_snapshots_brief_kind",
        ),
        sa.CheckConstraint(
            "task_revision >= 0 AND result_revision >= 0 AND input_revision >= 0",
            name="ck_task_management_export_snapshots_revisions_nonnegative",
        ),
        sa.CheckConstraint(
            "brief_version_number >= 1",
            name="ck_task_management_export_snapshots_version_positive",
        ),
        sa.CheckConstraint(
            "length(btrim(brief_version_id)) > 0",
            name="ck_task_management_export_snapshots_version_id_nonempty",
        ),
        sa.CheckConstraint(
            "media_type = 'text/markdown; charset=utf-8'",
            name="ck_task_management_export_snapshots_media_type",
        ),
        sa.CheckConstraint(
            "template_version = 'mvp0-markdown-v1'",
            name="ck_task_management_export_snapshots_template_version",
        ),
        sa.CheckConstraint(
            "length(content) > 0",
            name="ck_task_management_export_snapshots_content_nonempty",
        ),
        sa.CheckConstraint(
            "octet_length(content) > 0",
            name="ck_task_management_export_snapshots_content_utf8_nonempty",
        ),
        schema=schema,
    )


def downgrade() -> None:
    """Reject destructive rollback; repair with a later forward revision."""

    raise RuntimeError(
        "0008_review_export is forward-fix-only; use a new forward repair "
        "revision instead of destructive downgrade"
    )
