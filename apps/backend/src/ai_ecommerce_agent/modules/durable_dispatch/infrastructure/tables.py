"""Logical-schema SQLAlchemy Core table for Durable Dispatch Work Intents."""

from __future__ import annotations

import re

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    MetaData,
    PrimaryKeyConstraint,
    Table,
    Text,
)

DURABLE_DISPATCH_SCHEMA_TOKEN = "__durable_dispatch_schema__"
DURABLE_DISPATCH_METADATA = MetaData()
_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")
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


def _in(column: str, values: tuple[str, ...]) -> str:
    """Render a stable SQL check for an exact finite catalog."""

    return f"{column} IN ({', '.join(repr(value) for value in values)})"


def _schema(name: str) -> str:
    if not _IDENTIFIER.fullmatch(name):
        raise ValueError("schema must be a lowercase PostgreSQL identifier")
    return name


def _required_string_checks() -> tuple[CheckConstraint, ...]:
    return tuple(
        CheckConstraint(
            f"length(btrim({column})) > 0",
            name=(
                "ck_durable_dispatch_work_intents_"
                f"{_CHECK_NAME_COLUMNS.get(column, column)}_nonempty"
            ),
        )
        for column in _REQUIRED_STRING_COLUMNS
    )


def _optional_string_checks() -> tuple[CheckConstraint, ...]:
    return tuple(
        CheckConstraint(
            f"{column} IS NULL OR length(btrim({column})) > 0",
            name=(
                "ck_durable_dispatch_work_intents_"
                f"{_CHECK_NAME_COLUMNS.get(column, column)}_nonempty"
            ),
        )
        for column in _OPTIONAL_STRING_COLUMNS
    )


WORK_INTENTS_TABLE = Table(
    "durable_dispatch_work_intents",
    DURABLE_DISPATCH_METADATA,
    Column("dispatch_id", Text(), nullable=False),
    Column("intent_type", Text(), nullable=False),
    Column("owning_operation", Text(), nullable=False),
    Column("target_resource_kind", Text(), nullable=False),
    Column("target_resource_id", Text(), nullable=False),
    Column("command_id", Text(), nullable=False),
    Column("stage_run_id", Text(), nullable=True),
    Column("input_fingerprint", Text(), nullable=False),
    Column("fingerprint_schema_version", Text(), nullable=False),
    Column("base_domain_version_id", Text(), nullable=True),
    Column("expected_revision", BigInteger(), nullable=True),
    Column("payload_resource_kind", Text(), nullable=False),
    Column("payload_resource_id", Text(), nullable=False),
    Column("rerun_of_dispatch_id", Text(), nullable=True),
    Column("ordering_key", Text(), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("available_at", DateTime(timezone=True), nullable=False),
    Column("status", Text(), nullable=False),
    Column("revision", BigInteger(), nullable=False),
    Column("cancellation_requested", Boolean(), nullable=False),
    Column("delivery_attempt_id", Text(), nullable=True),
    Column("lease_holder_id", Text(), nullable=True),
    Column("fencing_token", BigInteger(), nullable=False),
    Column("lease_expires_at", DateTime(timezone=True), nullable=True),
    Column("superseded_by_dispatch_id", Text(), nullable=True),
    PrimaryKeyConstraint("dispatch_id", name="pk_durable_dispatch_work_intents"),
    ForeignKeyConstraint(
        ["rerun_of_dispatch_id"],
        [f"{DURABLE_DISPATCH_SCHEMA_TOKEN}.durable_dispatch_work_intents.dispatch_id"],
        name="fk_durable_dispatch_work_intents_rerun_of",
    ),
    ForeignKeyConstraint(
        ["superseded_by_dispatch_id"],
        [f"{DURABLE_DISPATCH_SCHEMA_TOKEN}.durable_dispatch_work_intents.dispatch_id"],
        name="fk_durable_dispatch_work_intents_superseded_by",
    ),
    *_required_string_checks(),
    *_optional_string_checks(),
    CheckConstraint(
        _in("status", _STATUS_VALUES),
        name="ck_durable_dispatch_work_intents_status",
    ),
    CheckConstraint(
        "revision >= 0",
        name="ck_durable_dispatch_work_intents_revision_nonnegative",
    ),
    CheckConstraint(
        "expected_revision IS NULL OR expected_revision >= 0",
        name="ck_durable_dispatch_work_intents_expected_revision_nonnegative",
    ),
    CheckConstraint(
        "fencing_token >= 0",
        name="ck_durable_dispatch_work_intents_fencing_token_nonnegative",
    ),
    CheckConstraint(
        "available_at >= created_at",
        name="ck_durable_dispatch_work_intents_available_not_before_created",
    ),
    CheckConstraint(
        "rerun_of_dispatch_id IS NULL OR rerun_of_dispatch_id <> dispatch_id",
        name="ck_durable_dispatch_work_intents_rerun_distinct",
    ),
    CheckConstraint(
        "superseded_by_dispatch_id IS NULL OR "
        "length(btrim(superseded_by_dispatch_id)) > 0",
        name="ck_durable_dispatch_work_intents_superseded_by_nonempty",
    ),
    CheckConstraint(
        "superseded_by_dispatch_id IS NULL OR superseded_by_dispatch_id <> dispatch_id",
        name="ck_durable_dispatch_work_intents_superseded_by_distinct",
    ),
    CheckConstraint(
        "(delivery_attempt_id IS NULL AND lease_holder_id IS NULL AND "
        "lease_expires_at IS NULL) OR "
        "(delivery_attempt_id IS NOT NULL AND lease_holder_id IS NOT NULL "
        "AND lease_expires_at IS NOT NULL)",
        name="ck_durable_dispatch_work_intents_lease_tuple",
    ),
    CheckConstraint(
        "(delivery_attempt_id IS NULL AND lease_holder_id IS NULL AND "
        "lease_expires_at IS NULL) OR fencing_token >= 1",
        name="ck_durable_dispatch_work_intents_leased_fencing_token",
    ),
    schema=DURABLE_DISPATCH_SCHEMA_TOKEN,
)


def schema_translate_map(schema: str) -> dict[str, str]:
    """Return the explicit map from the logical token to a real schema."""

    return {DURABLE_DISPATCH_SCHEMA_TOKEN: _schema(schema)}


__all__ = [
    "DURABLE_DISPATCH_SCHEMA_TOKEN",
    "DURABLE_DISPATCH_METADATA",
    "WORK_INTENTS_TABLE",
    "schema_translate_map",
]
