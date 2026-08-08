"""Names and SQLAlchemy metadata for the dedicated test-only schema."""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    MetaData,
    String,
    Table,
    Text,
)

SCHEMA_NAME = "ts01_compat"

metadata = MetaData(schema=SCHEMA_NAME)

work_intents = Table(
    "work_intent",
    metadata,
    Column("id", String(80), primary_key=True),
    Column("status", String(16), nullable=False),
    Column("holder_id", String(80), nullable=True),
    Column("lease_expires_at", DateTime(timezone=True), nullable=True),
    Column("fencing_token", BigInteger, nullable=False, server_default="0"),
    CheckConstraint(
        "status IN ('available', 'claimed', 'completed')",
        name="ck_work_intent_status",
    ),
    schema=SCHEMA_NAME,
)

current_truth = Table(
    "current_truth",
    metadata,
    Column(
        "work_intent_id",
        String(80),
        ForeignKey(f"{SCHEMA_NAME}.work_intent.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("value", Text, nullable=False),
    Column("revision", BigInteger, nullable=False),
    Column("committed_by", String(80), nullable=False),
    Column("committed_fencing_token", BigInteger, nullable=False),
    schema=SCHEMA_NAME,
)
