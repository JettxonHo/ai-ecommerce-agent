"""Create the Source and Task Source membership Business tables.

The Source/Evidence module owns only the stable Source identity, immutable
SourceVersion identity, revisioned processing Current Truth, and revisioned
TaskSourceAssociation records in this slice.  Content, storage, parsing,
retrieval, and Evidence Link tables are intentionally deferred to their own
bounded revisions.

This revision is forward-repair-only.  A production downgrade would destroy
Source history and membership data; recovery keeps the expanded schema and
uses a later forward repair revision instead.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_source_evidence"
down_revision: str | None = "0002_task_management"
branch_labels: Sequence[str] | None = None
depends_on: str | None = None

OWNER = "Source Evidence Persistence (MVP0-010B1)"
SOURCE_TABLE = "source_evidence_sources"
SOURCE_VERSION_TABLE = "source_evidence_source_versions"
PROCESSING_TABLE = "source_evidence_source_version_processing"
ASSOCIATION_TABLE = "source_evidence_task_source_associations"
AFFECTED_TABLES: tuple[str, ...] = (
    SOURCE_TABLE,
    SOURCE_VERSION_TABLE,
    PROCESSING_TABLE,
    ASSOCIATION_TABLE,
)
REVISION_CLASSIFICATION = "FORWARD_FIX_ONLY"
UPGRADE_STRATEGY = (
    "Create Source identity, immutable SourceVersion, processing Current Truth, "
    "and TaskSourceAssociation tables"
)
DOWNGRADE_CLASSIFICATION = "Unsupported; use a forward repair revision"
COMPATIBILITY_WINDOW = "Additive Source persistence tables; no prior Source tables"
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
    "AND table_name IN ("
    "'source_evidence_sources',"
    "'source_evidence_source_versions',"
    "'source_evidence_source_version_processing',"
    "'source_evidence_task_source_associations')"
)
RECOVERY_STRATEGY = (
    "Forward-recovery-first; preserve this revision and repair with a new "
    "Forward Repair revision"
)
REQUIRED_APPLICATION_VERSION = "MVP0-010B1"
RELATED_DQ_DEC_RFC = (
    "RFC-002 DQ-02/04/05/06/07/11/12/14/16; RFC-005 DQ-01/02/03; "
    "DEC-067; DEC-076; Issue #113"
)

_PROCESSING_STATUSES = (
    "registered",
    "processing",
    "ready",
    "ready_with_rejections",
    "failed",
    "superseded",
)
_MEMBERSHIP_STATES = ("active", "removed", "replaced")


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


def upgrade() -> None:
    """Create the Source graph tables and their ownership constraints."""

    schema = _schema()

    # Source is deliberately an identity anchor only.  Display, type, origin,
    # storage, submission, and other metadata require later accepted contracts.
    op.create_table(
        SOURCE_TABLE,
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("source_id", name="pk_source_evidence_sources"),
        schema=schema,
    )

    # The (source_version_id, source_id) unique key is the ownership target for
    # TaskSourceAssociation's composite SourceVersion foreign key.
    op.create_table(
        SOURCE_VERSION_TABLE,
        sa.Column("source_version_id", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("version_number", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "source_version_id", name="pk_source_evidence_source_versions"
        ),
        sa.UniqueConstraint(
            "source_id",
            "version_number",
            name="uq_source_evidence_source_versions_source_version_number",
        ),
        sa.UniqueConstraint(
            "source_version_id",
            "source_id",
            name="uq_source_evidence_source_versions_version_source",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            [f"{schema}.{SOURCE_TABLE}.source_id"],
            name="fk_source_evidence_source_versions_source_owner",
        ),
        sa.CheckConstraint(
            "version_number >= 1",
            name="ck_source_evidence_source_versions_version_number_positive",
        ),
        schema=schema,
    )

    op.create_table(
        PROCESSING_TABLE,
        sa.Column("source_version_id", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("failure_summary", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "source_version_id", name="pk_source_evidence_source_version_processing"
        ),
        sa.ForeignKeyConstraint(
            ["source_version_id"],
            [f"{schema}.{SOURCE_VERSION_TABLE}.source_version_id"],
            name="fk_source_evidence_source_version_processing_version_owner",
        ),
        sa.CheckConstraint(
            _in_check("status", _PROCESSING_STATUSES),
            name="ck_source_evidence_source_version_processing_status",
        ),
        sa.CheckConstraint(
            "revision >= 0",
            name="ck_source_evidence_processing_revision_nonnegative",
        ),
        schema=schema,
    )

    # The composite SourceVersion FK prevents an association from pairing a
    # Source identity with a version owned by a different Source.  The
    # composite replacement FK applies the same Task+Source ownership rule to
    # the replacement association and remains nullable for active/removed rows.
    op.create_table(
        ASSOCIATION_TABLE,
        sa.Column("source_association_id", sa.Text(), nullable=False),
        sa.Column("task_id", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("source_version_id", sa.Text(), nullable=False),
        sa.Column("membership_state", sa.Text(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("replaced_by_association_id", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint(
            "source_association_id",
            name="pk_source_evidence_task_source_associations",
        ),
        sa.UniqueConstraint(
            "source_association_id",
            "task_id",
            "source_id",
            name="uq_source_evidence_task_source_associations_association_owner",
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            [f"{schema}.task_management_tasks.task_id"],
            name="fk_source_evidence_task_source_associations_task_owner",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            [f"{schema}.{SOURCE_TABLE}.source_id"],
            name="fk_source_evidence_task_source_associations_source_owner",
        ),
        sa.ForeignKeyConstraint(
            ["source_version_id", "source_id"],
            [
                f"{schema}.{SOURCE_VERSION_TABLE}.source_version_id",
                f"{schema}.{SOURCE_VERSION_TABLE}.source_id",
            ],
            name="fk_source_evidence_assoc_source_version_owner",
        ),
        sa.ForeignKeyConstraint(
            ["replaced_by_association_id", "task_id", "source_id"],
            [
                f"{schema}.{ASSOCIATION_TABLE}.source_association_id",
                f"{schema}.{ASSOCIATION_TABLE}.task_id",
                f"{schema}.{ASSOCIATION_TABLE}.source_id",
            ],
            name="fk_source_evidence_task_source_associations_replacement_owner",
        ),
        sa.CheckConstraint(
            _in_check("membership_state", _MEMBERSHIP_STATES),
            name="ck_source_evidence_task_source_associations_membership_state",
        ),
        sa.CheckConstraint(
            "revision >= 0",
            name="ck_source_evidence_assoc_revision_nonnegative",
        ),
        sa.CheckConstraint(
            "replaced_by_association_id IS NULL OR "
            "replaced_by_association_id <> source_association_id",
            name="ck_source_evidence_assoc_replacement_distinct",
        ),
        sa.CheckConstraint(
            "(membership_state = 'replaced' AND "
            "replaced_by_association_id IS NOT NULL) OR "
            "(membership_state <> 'replaced' AND "
            "replaced_by_association_id IS NULL)",
            name="ck_source_evidence_assoc_replacement_link",
        ),
        schema=schema,
    )


def downgrade() -> None:
    """Reject destructive rollback; repair the schema with a new revision."""

    raise RuntimeError(
        "0003_source_evidence is forward-fix-only; use a new forward repair "
        "revision instead of destructive downgrade"
    )
