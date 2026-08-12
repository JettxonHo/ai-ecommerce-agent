"""Logical-schema SQLAlchemy Core tables owned by Source and Evidence.

This module describes the four tables introduced by the ``0003_source_evidence``
Business migration.  The schema name is deliberately a logical token: a
composition root binds it to a deployment schema through SQLAlchemy's
``schema_translate_map`` execution option.  No engine, session, connection, or
DDL is created here.
"""

from __future__ import annotations

import re

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKeyConstraint,
    MetaData,
    PrimaryKeyConstraint,
    Table,
    Text,
    UniqueConstraint,
)

SOURCE_EVIDENCE_SCHEMA_TOKEN = "__source_evidence_schema__"
SOURCE_EVIDENCE_METADATA = MetaData()
PRIMARY_INPUT_SCHEMA_TOKEN = "__primary_input_schema__"
PRIMARY_INPUT_METADATA = MetaData()
_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")
_PROCESSING_STATUSES = (
    "registered",
    "processing",
    "ready",
    "ready_with_rejections",
    "failed",
    "superseded",
)
_MEMBERSHIP_STATES = ("active", "removed", "replaced")


def _in(column: str, values: tuple[str, ...]) -> str:
    """Render a stable SQL check for an exact finite catalog."""

    return f"{column} IN ({', '.join(repr(value) for value in values)})"


def _schema(name: str) -> str:
    if not _IDENTIFIER.fullmatch(name):
        raise ValueError("schema must be a lowercase PostgreSQL identifier")
    return name


SOURCES_TABLE = Table(
    "source_evidence_sources",
    SOURCE_EVIDENCE_METADATA,
    Column("source_id", Text(), nullable=False),
    PrimaryKeyConstraint("source_id", name="pk_source_evidence_sources"),
    schema=SOURCE_EVIDENCE_SCHEMA_TOKEN,
)

SOURCE_VERSIONS_TABLE = Table(
    "source_evidence_source_versions",
    SOURCE_EVIDENCE_METADATA,
    Column("source_version_id", Text(), nullable=False),
    Column("source_id", Text(), nullable=False),
    Column("version_number", BigInteger(), nullable=False),
    PrimaryKeyConstraint(
        "source_version_id", name="pk_source_evidence_source_versions"
    ),
    UniqueConstraint(
        "source_id",
        "version_number",
        name="uq_source_evidence_source_versions_source_version_number",
    ),
    UniqueConstraint(
        "source_version_id",
        "source_id",
        name="uq_source_evidence_source_versions_version_source",
    ),
    ForeignKeyConstraint(
        ["source_id"],
        [f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}.source_evidence_sources.source_id"],
        name="fk_source_evidence_source_versions_source_owner",
    ),
    CheckConstraint(
        "version_number >= 1",
        name="ck_source_evidence_source_versions_version_number_positive",
    ),
    schema=SOURCE_EVIDENCE_SCHEMA_TOKEN,
)

SOURCE_VERSION_PROCESSING_TABLE = Table(
    "source_evidence_source_version_processing",
    SOURCE_EVIDENCE_METADATA,
    Column("source_version_id", Text(), nullable=False),
    Column("status", Text(), nullable=False),
    Column("revision", BigInteger(), nullable=False),
    Column("failure_summary", Text(), nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    PrimaryKeyConstraint(
        "source_version_id",
        name="pk_source_evidence_source_version_processing",
    ),
    ForeignKeyConstraint(
        ["source_version_id"],
        [
            f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}."
            "source_evidence_source_versions.source_version_id"
        ],
        name="fk_source_evidence_source_version_processing_version_owner",
    ),
    CheckConstraint(
        _in("status", _PROCESSING_STATUSES),
        name="ck_source_evidence_source_version_processing_status",
    ),
    CheckConstraint(
        "revision >= 0",
        name="ck_source_evidence_processing_revision_nonnegative",
    ),
    schema=SOURCE_EVIDENCE_SCHEMA_TOKEN,
)

TASK_SOURCE_ASSOCIATIONS_TABLE = Table(
    "source_evidence_task_source_associations",
    SOURCE_EVIDENCE_METADATA,
    Column("source_association_id", Text(), nullable=False),
    Column("task_id", Text(), nullable=False),
    Column("source_id", Text(), nullable=False),
    Column("source_version_id", Text(), nullable=False),
    Column("membership_state", Text(), nullable=False),
    Column("revision", BigInteger(), nullable=False),
    Column("replaced_by_association_id", Text(), nullable=True),
    PrimaryKeyConstraint(
        "source_association_id",
        name="pk_source_evidence_task_source_associations",
    ),
    UniqueConstraint(
        "source_association_id",
        "task_id",
        "source_id",
        name="uq_source_evidence_task_source_associations_association_owner",
    ),
    ForeignKeyConstraint(
        ["task_id"],
        [f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}.task_management_tasks.task_id"],
        name="fk_source_evidence_task_source_associations_task_owner",
    ),
    ForeignKeyConstraint(
        ["source_id"],
        [f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}.source_evidence_sources.source_id"],
        name="fk_source_evidence_task_source_associations_source_owner",
    ),
    ForeignKeyConstraint(
        ["source_version_id", "source_id"],
        [
            f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}."
            "source_evidence_source_versions.source_version_id",
            f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}.source_evidence_source_versions.source_id",
        ],
        name="fk_source_evidence_assoc_source_version_owner",
    ),
    ForeignKeyConstraint(
        ["replaced_by_association_id", "task_id", "source_id"],
        [
            f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}."
            "source_evidence_task_source_associations.source_association_id",
            f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}."
            "source_evidence_task_source_associations.task_id",
            f"{SOURCE_EVIDENCE_SCHEMA_TOKEN}."
            "source_evidence_task_source_associations.source_id",
        ],
        name="fk_source_evidence_task_source_associations_replacement_owner",
    ),
    CheckConstraint(
        _in("membership_state", _MEMBERSHIP_STATES),
        name="ck_source_evidence_task_source_associations_membership_state",
    ),
    CheckConstraint(
        "revision >= 0",
        name="ck_source_evidence_assoc_revision_nonnegative",
    ),
    CheckConstraint(
        "replaced_by_association_id IS NULL OR "
        "replaced_by_association_id <> source_association_id",
        name="ck_source_evidence_assoc_replacement_distinct",
    ),
    CheckConstraint(
        "(membership_state = 'replaced' AND "
        "replaced_by_association_id IS NOT NULL) OR "
        "(membership_state <> 'replaced' AND "
        "replaced_by_association_id IS NULL)",
        name="ck_source_evidence_assoc_replacement_link",
    ),
    schema=SOURCE_EVIDENCE_SCHEMA_TOKEN,
)

TASK_PRIMARY_INPUTS_TABLE = Table(
    "source_evidence_task_primary_inputs",
    PRIMARY_INPUT_METADATA,
    Column("task_id", Text(), nullable=False),
    Column("input_kind", Text(), nullable=False),
    Column("file_name", Text(), nullable=True),
    Column("content", Text(), nullable=False),
    Column("byte_count", BigInteger(), nullable=False),
    Column("revision", BigInteger(), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    PrimaryKeyConstraint("task_id", name="pk_source_evidence_task_primary_inputs"),
    ForeignKeyConstraint(
        ["task_id"],
        [f"{PRIMARY_INPUT_SCHEMA_TOKEN}.task_management_tasks.task_id"],
        name="fk_source_evidence_task_primary_inputs_task_owner",
    ),
    CheckConstraint(
        _in("input_kind", ("pasted_text", "text_file", "markdown_file")),
        name="ck_source_evidence_task_primary_inputs_kind",
    ),
    CheckConstraint(
        "length(btrim(content)) > 0",
        name="ck_source_evidence_task_primary_inputs_content_nonempty",
    ),
    CheckConstraint(
        "byte_count >= 1 AND byte_count <= 1048576",
        name="ck_source_evidence_task_primary_inputs_byte_count",
    ),
    CheckConstraint(
        "revision >= 0",
        name="ck_source_evidence_task_primary_inputs_revision_nonnegative",
    ),
    CheckConstraint(
        "(input_kind = 'pasted_text' AND file_name IS NULL) OR "
        "(input_kind <> 'pasted_text' AND file_name IS NOT NULL)",
        name="ck_source_evidence_task_primary_inputs_filename_pair",
    ),
    schema=PRIMARY_INPUT_SCHEMA_TOKEN,
)


def schema_translate_map(schema: str) -> dict[str, str]:
    """Return the explicit map from the logical token to a real schema."""

    return {SOURCE_EVIDENCE_SCHEMA_TOKEN: _schema(schema)}


def primary_input_schema_translate_map(schema: str) -> dict[str, str]:
    """Bind the isolated primary-input metadata token to a Business schema."""

    return {PRIMARY_INPUT_SCHEMA_TOKEN: _schema(schema)}


__all__ = [
    "SOURCE_EVIDENCE_METADATA",
    "SOURCE_EVIDENCE_SCHEMA_TOKEN",
    "PRIMARY_INPUT_METADATA",
    "PRIMARY_INPUT_SCHEMA_TOKEN",
    "SOURCE_VERSION_PROCESSING_TABLE",
    "SOURCE_VERSIONS_TABLE",
    "SOURCES_TABLE",
    "TASK_SOURCE_ASSOCIATIONS_TABLE",
    "TASK_PRIMARY_INPUTS_TABLE",
    "primary_input_schema_translate_map",
    "schema_translate_map",
]
