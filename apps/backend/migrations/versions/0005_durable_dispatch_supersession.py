"""Add the nullable Durable Dispatch supersession reference.

This revision appends one causal reference to the Work Intent current-state
table.  It performs no backfill, rewrite, transition, or successor creation.
The revision is forward-repair-only; a later revision must repair production
state instead of destructively removing this reference.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_dispatch_supersession"
down_revision: str | None = "0004_durable_dispatch"
branch_labels: Sequence[str] | None = None
depends_on: str | None = None

OWNER = "Durable Dispatch Persistence (MVP0-019B)"
WORK_INTENT_TABLE = "durable_dispatch_work_intents"
AFFECTED_TABLES: tuple[str, ...] = (WORK_INTENT_TABLE,)
REVISION_CLASSIFICATION = "FORWARD_FIX_ONLY"
UPGRADE_STRATEGY = "Append one nullable supersession reference without backfill"
DOWNGRADE_CLASSIFICATION = "Unsupported; use a forward repair revision"
COMPATIBILITY_WINDOW = (
    "Old runtimes ignore the nullable column; new runtimes require schema 0005"
)
DATA_LOSS_RISK = "None on upgrade; destructive downgrade is unsupported"
LOCK_RISK = "Short table lock for ADD COLUMN and named FK/CHECK validation"
LOCK_TIMEOUT = "Not overridden; migration operator owns timeout policy"
STATEMENT_TIMEOUT = "Not overridden; migration operator owns timeout policy"
DDL_TRANSACTION_BOUNDARY = (
    "Alembic transaction_per_migration=True; PostgreSQL DDL is transactional"
)
REWRITE_RISK = "None; nullable column has no default and existing rows are untouched"
BACKFILL_REQUIREMENT = "None"
DESTRUCTIVE_OPERATION = "None on upgrade; no destructive downgrade"
NON_TRANSACTIONAL_OPERATION = "None"
VERIFICATION_QUERY = (
    "SELECT column_name FROM information_schema.columns "
    "WHERE table_schema = <business_schema> "
    "AND table_name = 'durable_dispatch_work_intents' "
    "AND column_name = 'superseded_by_dispatch_id'"
)
RECOVERY_STRATEGY = (
    "Forward-recovery-first; preserve this revision and repair with a later "
    "forward revision"
)
REQUIRED_APPLICATION_VERSION = "MVP0-019B"
RELATED_DQ_DEC_RFC = (
    "RFC-001; RFC-002 DQ-02/06/07/09/14/16; RFC-003 DQ-04/06/09; DEC-050; Issue #184"
)


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


def upgrade() -> None:
    """Append the nullable causal reference and exact named constraints."""

    schema = _schema()
    op.add_column(
        WORK_INTENT_TABLE,
        sa.Column("superseded_by_dispatch_id", sa.Text(), nullable=True),
        schema=schema,
    )
    op.create_foreign_key(
        "fk_durable_dispatch_work_intents_superseded_by",
        WORK_INTENT_TABLE,
        WORK_INTENT_TABLE,
        ["superseded_by_dispatch_id"],
        ["dispatch_id"],
        source_schema=schema,
        referent_schema=schema,
    )
    op.create_check_constraint(
        "ck_durable_dispatch_work_intents_superseded_by_nonempty",
        WORK_INTENT_TABLE,
        "superseded_by_dispatch_id IS NULL OR "
        "length(btrim(superseded_by_dispatch_id)) > 0",
        schema=schema,
    )
    op.create_check_constraint(
        "ck_durable_dispatch_work_intents_superseded_by_distinct",
        WORK_INTENT_TABLE,
        "superseded_by_dispatch_id IS NULL OR superseded_by_dispatch_id <> dispatch_id",
        schema=schema,
    )


def downgrade() -> None:
    """Reject destructive rollback; repair with a later forward revision."""

    raise RuntimeError(
        "0005_dispatch_supersession is forward-fix-only; use a new "
        "forward repair revision instead of destructive downgrade"
    )
