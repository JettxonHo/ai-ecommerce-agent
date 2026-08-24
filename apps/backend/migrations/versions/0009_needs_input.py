"""Create the Task-owned Needs Input action-request resource.

This revision is additive and forward-only.  One row is the durable action
request, its lifecycle, and the single committed resolution/idempotency replay
projection.  Existing Business tables are intentionally not altered.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_needs_input"
down_revision: str | None = "0008_review_export"
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
    """Create one Task-owned Needs Input table and its bounded indexes."""

    schema = _schema()
    table = "task_management_needs_input_requests"
    op.create_table(
        table,
        sa.Column("action_request_id", sa.Text(), nullable=False),
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("reason_type", sa.Text(), nullable=False),
        sa.Column("reason_summary", sa.Text(), nullable=False),
        sa.Column("affected_stages", sa.Text(), nullable=False),
        sa.Column("source_references", sa.Text(), nullable=False),
        sa.Column("conflict_values", sa.Text(), nullable=False),
        sa.Column("allowed_resolution_types", sa.Text(), nullable=False),
        sa.Column("expected_recovery", sa.Text(), nullable=False),
        sa.Column("superseded_by_action_request_id", sa.Text()),
        sa.Column("resolution_idempotency_key", sa.Text()),
        sa.Column("resolution_type", sa.Text()),
        sa.Column("resolution_payload", sa.Text()),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "action_request_id", name="pk_task_management_needs_input_requests"
        ),
        sa.UniqueConstraint(
            "task_id",
            "action_request_id",
            name="uq_task_management_needs_input_requests_task_action",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            [f"{schema}.task_management_tasks.task_id"],
            name="fk_task_management_needs_input_requests_task_owner",
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "superseded_by_action_request_id"],
            [f"{schema}.{table}.task_id", f"{schema}.{table}.action_request_id"],
            name="fk_task_management_needs_input_requests_superseded_by",
        ),
        sa.CheckConstraint(
            "length(btrim(action_request_id)) > 0",
            name="ck_task_management_needs_input_requests_id_nonempty",
        ),
        sa.CheckConstraint(
            "length(btrim(task_id)) > 0",
            name="ck_task_management_needs_input_requests_task_id_nonempty",
        ),
        sa.CheckConstraint(
            "revision >= 0",
            name="ck_task_management_needs_input_requests_revision_nonnegative",
        ),
        sa.CheckConstraint(
            "status IN ('open', 'resolved', 'superseded', 'cancelled')",
            name="ck_task_management_needs_input_requests_status",
        ),
        sa.CheckConstraint(
            "length(btrim(reason_type)) > 0 AND octet_length(reason_type) <= 200",
            name="ck_task_management_needs_input_requests_reason_type",
        ),
        sa.CheckConstraint(
            "length(btrim(reason_summary)) > 0 "
            "AND octet_length(reason_summary) <= 4096",
            name="ck_task_management_needs_input_requests_reason_summary",
        ),
        sa.CheckConstraint(
            "length(btrim(affected_stages)) > 0 "
            "AND octet_length(affected_stages) <= 16384",
            name="ck_task_management_needs_input_requests_affected_stages",
        ),
        sa.CheckConstraint(
            "length(btrim(source_references)) > 0 "
            "AND octet_length(source_references) <= 16384",
            name="ck_task_management_needs_input_requests_source_references",
        ),
        sa.CheckConstraint(
            "length(btrim(conflict_values)) > 0 "
            "AND octet_length(conflict_values) <= 32768",
            name="ck_task_management_needs_input_requests_conflict_values",
        ),
        sa.CheckConstraint(
            "length(btrim(allowed_resolution_types)) > 0 "
            "AND octet_length(allowed_resolution_types) <= 4096",
            name="ck_task_management_needs_input_requests_allowed_resolutions",
        ),
        sa.CheckConstraint(
            "expected_recovery IN ('resume', 'rerun', 'manual_review', 'none')",
            name="ck_task_management_needs_input_requests_expected_recovery",
        ),
        sa.CheckConstraint(
            "resolution_idempotency_key IS NULL OR "
            "(length(btrim(resolution_idempotency_key)) > 0 "
            "AND octet_length(resolution_idempotency_key) <= 200)",
            name="ck_task_management_needs_input_requests_resolution_key",
        ),
        sa.CheckConstraint(
            "resolution_type IS NULL OR resolution_type IN "
            "('provide_source_reference', 'choose_existing_value', "
            "'submit_correction', 'confirm_known_limitation', 'cancel_path')",
            name="ck_task_management_needs_input_requests_resolution_type",
        ),
        sa.CheckConstraint(
            "resolution_payload IS NULL OR "
            "(length(btrim(resolution_payload)) > 0 "
            "AND octet_length(resolution_payload) <= 32768)",
            name="ck_task_management_needs_input_requests_resolution_payload",
        ),
        sa.CheckConstraint(
            "((status = 'open' AND superseded_by_action_request_id IS NULL "
            "AND resolution_idempotency_key IS NULL AND resolution_type IS NULL "
            "AND resolution_payload IS NULL AND resolved_at IS NULL) OR "
            "(status IN ('resolved', 'cancelled') "
            "AND superseded_by_action_request_id IS NULL "
            "AND resolution_idempotency_key IS NOT NULL "
            "AND resolution_type IS NOT NULL AND resolution_payload IS NOT NULL "
            "AND resolved_at IS NOT NULL) OR "
            "(status = 'superseded' "
            "AND superseded_by_action_request_id IS NOT NULL "
            "AND resolution_idempotency_key IS NULL AND resolution_type IS NULL "
            "AND resolution_payload IS NULL AND resolved_at IS NULL))",
            name="ck_task_management_needs_input_requests_state_projection",
        ),
        sa.CheckConstraint(
            "((status IN ('open', 'superseded') AND resolution_type IS NULL) OR "
            "(status = 'cancelled' AND resolution_type = 'cancel_path') OR "
            "(status = 'resolved' AND resolution_type IN "
            "('provide_source_reference', 'choose_existing_value', "
            "'submit_correction', 'confirm_known_limitation')))",
            name="ck_task_management_needs_input_requests_resolution_status",
        ),
        sa.CheckConstraint(
            "superseded_by_action_request_id IS NULL "
            "OR superseded_by_action_request_id <> action_request_id",
            name="ck_task_management_needs_input_requests_superseded_distinct",
        ),
        schema=schema,
    )
    # This is both the current-request lookup path and the one-open-request
    # invariant.  Historical resolved/superseded rows remain durable.
    op.create_index(
        "uq_task_management_needs_input_requests_open_task",
        table,
        ["task_id"],
        unique=True,
        postgresql_where=sa.text("status = 'open'"),
        schema=schema,
    )


def downgrade() -> None:
    """Reject destructive rollback; repair with a later forward revision."""

    raise RuntimeError(
        "0009_needs_input is forward-fix-only; use a new forward repair "
        "revision instead of destructive downgrade"
    )
