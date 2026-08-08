"""Create the dedicated TS-01 test-only schema."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_ts01_base"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: str | None = None

SCHEMA_NAME = "ts01_compat"


def upgrade() -> None:
    op.create_table(
        "work_intent",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("holder_id", sa.String(length=80), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fencing_token", sa.BigInteger(), server_default="0", nullable=False),
        sa.CheckConstraint(
            "status IN ('available', 'claimed', 'completed')",
            name="ck_work_intent_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=SCHEMA_NAME,
    )
    op.create_table(
        "current_truth",
        sa.Column("work_intent_id", sa.String(length=80), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("committed_by", sa.String(length=80), nullable=False),
        sa.Column("committed_fencing_token", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["work_intent_id"],
            [f"{SCHEMA_NAME}.work_intent.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("work_intent_id"),
        schema=SCHEMA_NAME,
    )


def downgrade() -> None:
    op.drop_table("current_truth", schema=SCHEMA_NAME)
    op.drop_table("work_intent", schema=SCHEMA_NAME)
