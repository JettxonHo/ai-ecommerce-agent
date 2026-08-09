"""Create the Durable Dispatch Work Intent Business table.

This revision establishes the durable identity and current-state storage
boundary for Work Intent.  It intentionally does not implement claim, lease,
heartbeat, cancellation transitions, attempt history, or payload storage.

The revision is forward-repair-only.  A production downgrade would remove
durable dispatch identity and recovery state; a later forward revision must be
used for repair instead of a destructive rollback.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_durable_dispatch"
down_revision: str | None = "0003_source_evidence"
branch_labels: Sequence[str] | None = None
depends_on: str | None = None

OWNER = "Durable Dispatch Persistence (MVP0-018F)"
WORK_INTENT_TABLE = "durable_dispatch_work_intents"
AFFECTED_TABLES: tuple[str, ...] = (WORK_INTENT_TABLE,)
REVISION_CLASSIFICATION = "FORWARD_FIX_ONLY"
UPGRADE_STRATEGY = "Create the Durable Dispatch Work Intent current-state table"
DOWNGRADE_CLASSIFICATION = "Unsupported; use a forward repair revision"
COMPATIBILITY_WINDOW = (
    "Additive Work Intent persistence; claim and lifecycle behavior remain deferred"
)
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
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema = <business_schema> "
    "AND table_name = 'durable_dispatch_work_intents'"
)
RECOVERY_STRATEGY = (
    "Forward-recovery-first; preserve this revision and repair with a new "
    "Forward Repair revision"
)
REQUIRED_APPLICATION_VERSION = "MVP0-018F"
RELATED_DQ_DEC_RFC = (
    "RFC-001; RFC-002 DQ-02/04/05/06/07/08/09/14/16/17; RFC-003 DQ-04/05/06; "
    "DEC-050; Issue #158; Issue #168"
)

_STATUS_VALUES = (
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
_REQUIRED_STRING_COLUMNS = (
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
_OPTIONAL_STRING_COLUMNS = (
    "stage_run_id",
    "base_domain_version_id",
    "rerun_of_dispatch_id",
    "ordering_key",
    "delivery_attempt_id",
    "lease_holder_id",
)
_CHECK_NAME_COLUMNS = {
    "fingerprint_schema_version": "fp_schema_version",
    "base_domain_version_id": "base_version",
}


def _in_check(column: str, values: tuple[str, ...]) -> str:
    """Render a stable SQL check for an exact finite catalog."""

    rendered = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({rendered})"


def _schema() -> str:
    """Read the explicit Business/version schema selected by Alembic."""

    config = op.get_context().config
    business_schema = (config.get_main_option("business_schema") or "").strip()
    version_schema = (config.get_main_option("version_table_schema") or "").strip()
    if business_schema and version_schema and business_schema != version_schema:
        raise ValueError(
            "business_schema and version_table_schema must identify the same "
            "Business migration schema"
        )
    return business_schema or version_schema or "public"


def _required_string_checks() -> tuple[sa.CheckConstraint, ...]:
    return tuple(
        sa.CheckConstraint(
            f"length(btrim({column})) > 0",
            name=(
                "ck_durable_dispatch_work_intents_"
                f"{_CHECK_NAME_COLUMNS.get(column, column)}_nonempty"
            ),
        )
        for column in _REQUIRED_STRING_COLUMNS
    )


def _optional_string_checks() -> tuple[sa.CheckConstraint, ...]:
    return tuple(
        sa.CheckConstraint(
            f"{column} IS NULL OR length(btrim({column})) > 0",
            name=(
                "ck_durable_dispatch_work_intents_"
                f"{_CHECK_NAME_COLUMNS.get(column, column)}_nonempty"
            ),
        )
        for column in _OPTIONAL_STRING_COLUMNS
    )


def upgrade() -> None:
    """Create Work Intent identity, references, current state, and bounds."""

    schema = _schema()
    op.create_table(
        WORK_INTENT_TABLE,
        sa.Column("dispatch_id", sa.Text(), nullable=False),
        sa.Column("intent_type", sa.Text(), nullable=False),
        sa.Column("owning_operation", sa.Text(), nullable=False),
        sa.Column("target_resource_kind", sa.Text(), nullable=False),
        sa.Column("target_resource_id", sa.Text(), nullable=False),
        sa.Column("command_id", sa.Text(), nullable=False),
        sa.Column("stage_run_id", sa.Text(), nullable=True),
        sa.Column("input_fingerprint", sa.Text(), nullable=False),
        sa.Column("fingerprint_schema_version", sa.Text(), nullable=False),
        sa.Column("base_domain_version_id", sa.Text(), nullable=True),
        sa.Column("expected_revision", sa.BigInteger(), nullable=True),
        sa.Column("payload_resource_kind", sa.Text(), nullable=False),
        sa.Column("payload_resource_id", sa.Text(), nullable=False),
        sa.Column("rerun_of_dispatch_id", sa.Text(), nullable=True),
        sa.Column("ordering_key", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("cancellation_requested", sa.Boolean(), nullable=False),
        sa.Column("delivery_attempt_id", sa.Text(), nullable=True),
        sa.Column("lease_holder_id", sa.Text(), nullable=True),
        sa.Column("fencing_token", sa.BigInteger(), nullable=False),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("dispatch_id", name="pk_durable_dispatch_work_intents"),
        sa.ForeignKeyConstraint(
            ["rerun_of_dispatch_id"],
            [f"{schema}.{WORK_INTENT_TABLE}.dispatch_id"],
            name="fk_durable_dispatch_work_intents_rerun_of",
        ),
        *_required_string_checks(),
        *_optional_string_checks(),
        sa.CheckConstraint(
            _in_check("status", _STATUS_VALUES),
            name="ck_durable_dispatch_work_intents_status",
        ),
        sa.CheckConstraint(
            "revision >= 0",
            name="ck_durable_dispatch_work_intents_revision_nonnegative",
        ),
        sa.CheckConstraint(
            "expected_revision IS NULL OR expected_revision >= 0",
            name="ck_durable_dispatch_work_intents_expected_revision_nonnegative",
        ),
        sa.CheckConstraint(
            "fencing_token >= 0",
            name="ck_durable_dispatch_work_intents_fencing_token_nonnegative",
        ),
        sa.CheckConstraint(
            "available_at >= created_at",
            name="ck_durable_dispatch_work_intents_available_not_before_created",
        ),
        sa.CheckConstraint(
            "rerun_of_dispatch_id IS NULL OR rerun_of_dispatch_id <> dispatch_id",
            name="ck_durable_dispatch_work_intents_rerun_distinct",
        ),
        sa.CheckConstraint(
            "(delivery_attempt_id IS NULL AND lease_holder_id IS NULL AND "
            "lease_expires_at IS NULL) OR "
            "(delivery_attempt_id IS NOT NULL AND lease_holder_id IS NOT NULL "
            "AND lease_expires_at IS NOT NULL)",
            name="ck_durable_dispatch_work_intents_lease_tuple",
        ),
        sa.CheckConstraint(
            "(delivery_attempt_id IS NULL AND lease_holder_id IS NULL AND "
            "lease_expires_at IS NULL) OR fencing_token >= 1",
            name="ck_durable_dispatch_work_intents_leased_fencing_token",
        ),
        schema=schema,
    )


def downgrade() -> None:
    """Reject destructive rollback; repair with a later forward revision."""

    raise RuntimeError(
        "0004_durable_dispatch is forward-fix-only; use a new forward repair "
        "revision instead of destructive downgrade"
    )
