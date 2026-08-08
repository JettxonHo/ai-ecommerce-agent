"""Establish the empty production Business migration baseline.

This revision intentionally creates no Business tables.  The only object
created by ``alembic upgrade head`` is Alembic's own version table, which is
the migration tool's identity and is not a domain version, business revision,
checkpoint schema version, or vendor migration record.
"""

from collections.abc import Sequence

revision: str = "0001_business_baseline"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: str | None = None

# DQ-14 revision-level governance declarations.  These are deliberately
# explicit even for an empty baseline so later revisions inherit a reviewable
# shape before any aggregate table is introduced.
OWNER = "Business Migration Capability (MVP0-008)"
AFFECTED_TABLES: tuple[str, ...] = ()
REVISION_CLASSIFICATION = "REVERSIBLE_SCHEMA"
UPGRADE_STRATEGY = "Empty initial baseline; creates no Business tables"
DOWNGRADE_CLASSIFICATION = "Bounded empty-baseline downgrade only"
COMPATIBILITY_WINDOW = "Not applicable before the first aggregate revision"
DATA_LOSS_RISK = "None; no Business data or table is touched"
LOCK_RISK = "Alembic version-table DDL only"
LOCK_TIMEOUT = "Not overridden; no Business table/index lock is requested"
STATEMENT_TIMEOUT = "Not overridden; no Business table/index statement is run"
DDL_TRANSACTION_BOUNDARY = (
    "Alembic transaction_per_migration=True; no non-transactional DDL"
)
REWRITE_RISK = "None"
BACKFILL_REQUIREMENT = "None"
DESTRUCTIVE_OPERATION = "None"
NON_TRANSACTIONAL_OPERATION = "None"
VERIFICATION_QUERY = "SELECT version_num FROM alembic_version"
RECOVERY_STRATEGY = (
    "Forward-recovery-first; preserve this revision and repair later revisions "
    "with a new Forward Repair revision"
)
REQUIRED_APPLICATION_VERSION = "MVP0-008"
RELATED_DQ_DEC_RFC = "RFC-002 DQ-11, DQ-14, DQ-16; Issue #79"


def upgrade() -> None:
    """Mark the first Business Alembic revision without creating domain DDL."""


def downgrade() -> None:
    """Bounded empty-baseline operation; not a universal production rollback."""
