"""Logical SQLAlchemy table metadata for the existing 0009 table.

This module describes the one migration-owned table; it does not create DDL.
"""

from __future__ import annotations

import re

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Index,
    MetaData,
    PrimaryKeyConstraint,
    Table,
    Text,
    UniqueConstraint,
    text,
)

NEEDS_INPUT_SCHEMA_TOKEN = "__task_management_schema__"
NEEDS_INPUT_METADATA = MetaData()
_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")

NEEDS_INPUT_REQUESTS_TABLE = Table(
    "task_management_needs_input_requests",
    NEEDS_INPUT_METADATA,
    Column("action_request_id", Text(), nullable=False),
    Column("task_id", Text(), nullable=False),
    Column("revision", BigInteger(), nullable=False),
    Column("status", Text(), nullable=False),
    Column("reason_type", Text(), nullable=False),
    Column("reason_summary", Text(), nullable=False),
    Column("affected_stages", Text(), nullable=False),
    Column("source_references", Text(), nullable=False),
    Column("conflict_values", Text(), nullable=False),
    Column("allowed_resolution_types", Text(), nullable=False),
    Column("expected_recovery", Text(), nullable=False),
    Column("superseded_by_action_request_id", Text()),
    Column("resolution_idempotency_key", Text()),
    Column("resolution_type", Text()),
    Column("resolution_payload", Text()),
    Column("resolved_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    PrimaryKeyConstraint(
        "action_request_id", name="pk_task_management_needs_input_requests"
    ),
    UniqueConstraint(
        "task_id",
        "action_request_id",
        name="uq_task_management_needs_input_requests_task_action",
    ),
    ForeignKeyConstraint(
        ["task_id"],
        [f"{NEEDS_INPUT_SCHEMA_TOKEN}.task_management_tasks.task_id"],
        name="fk_task_management_needs_input_requests_task_owner",
    ),
    ForeignKeyConstraint(
        ["task_id", "superseded_by_action_request_id"],
        [
            f"{NEEDS_INPUT_SCHEMA_TOKEN}.task_management_needs_input_requests.task_id",
            f"{NEEDS_INPUT_SCHEMA_TOKEN}.task_management_needs_input_requests.action_request_id",
        ],
        name="fk_task_management_needs_input_requests_superseded_by",
        deferrable=True,
        initially="DEFERRED",
    ),
    CheckConstraint(
        "((status = 'open' AND superseded_by_action_request_id IS NULL "
        "AND resolution_idempotency_key IS NULL AND resolution_type IS NULL "
        "AND resolution_payload IS NULL AND resolved_at IS NULL) OR "
        "(status IN ('resolved', 'cancelled') "
        "AND superseded_by_action_request_id IS NULL "
        "AND resolution_idempotency_key IS NOT NULL "
        "AND resolution_type IS NOT NULL AND resolution_payload IS NOT NULL "
        "AND resolved_at IS NOT NULL) OR "
        "(status = 'superseded' "
        "AND resolution_idempotency_key IS NULL AND resolution_type IS NULL "
        "AND resolution_payload IS NULL AND resolved_at IS NULL))",
        name="ck_task_management_needs_input_requests_state_projection",
    ),
    CheckConstraint(
        "superseded_by_action_request_id IS NULL "
        "OR superseded_by_action_request_id <> action_request_id",
        name="ck_task_management_needs_input_requests_superseded_distinct",
    ),
    Index(
        "uq_task_management_needs_input_requests_open_task",
        "task_id",
        unique=True,
        postgresql_where=text("status = 'open'"),
    ),
    schema=NEEDS_INPUT_SCHEMA_TOKEN,
)


def _schema(name: str) -> str:
    if not _IDENTIFIER.fullmatch(name):
        raise ValueError("schema must be a lowercase PostgreSQL identifier")
    return name


def schema_translate_map(schema: str) -> dict[str, str]:
    """Bind the logical table token to one explicit Business schema."""

    return {NEEDS_INPUT_SCHEMA_TOKEN: _schema(schema)}


__all__ = [
    "NEEDS_INPUT_METADATA",
    "NEEDS_INPUT_REQUESTS_TABLE",
    "NEEDS_INPUT_SCHEMA_TOKEN",
    "schema_translate_map",
]
