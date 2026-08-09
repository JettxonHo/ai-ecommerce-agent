"""Contract checks for the Source and Evidence SQLAlchemy Core tables."""

from __future__ import annotations

from typing import cast

import pytest
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
)

from ai_ecommerce_agent.modules.source_evidence.infrastructure import tables

pytestmark = pytest.mark.contract

_TABLES = (
    tables.SOURCES_TABLE,
    tables.SOURCE_VERSIONS_TABLE,
    tables.SOURCE_VERSION_PROCESSING_TABLE,
    tables.TASK_SOURCE_ASSOCIATIONS_TABLE,
)
_TABLE_BY_NAME = {table.name: table for table in _TABLES}


def _normalize_sql(expression: object) -> str:
    """Compare SQL text while ignoring only formatting whitespace."""

    return " ".join(str(expression).split())


def test_metadata_contains_exactly_the_four_migration_tables() -> None:
    assert set(tables.SOURCE_EVIDENCE_METADATA.tables) == {
        table.fullname for table in _TABLES
    }
    assert all(table.metadata is tables.SOURCE_EVIDENCE_METADATA for table in _TABLES)
    assert all(table.schema == tables.SOURCE_EVIDENCE_SCHEMA_TOKEN for table in _TABLES)
    assert all(not table.indexes for table in _TABLES)


def test_table_columns_match_the_minimal_source_migration() -> None:
    assert [column.name for column in tables.SOURCES_TABLE.columns] == ["source_id"]
    assert [column.name for column in tables.SOURCE_VERSIONS_TABLE.columns] == [
        "source_version_id",
        "source_id",
        "version_number",
    ]
    assert [
        column.name for column in tables.SOURCE_VERSION_PROCESSING_TABLE.columns
    ] == [
        "source_version_id",
        "status",
        "revision",
        "failure_summary",
        "updated_at",
    ]
    assert [
        column.name for column in tables.TASK_SOURCE_ASSOCIATIONS_TABLE.columns
    ] == [
        "source_association_id",
        "task_id",
        "source_id",
        "source_version_id",
        "membership_state",
        "revision",
        "replaced_by_association_id",
    ]


def test_columns_use_postgresql_neutral_types_and_exact_nullability() -> None:
    expected = {
        "source_evidence_sources": {
            "source_id": (Text, False),
        },
        "source_evidence_source_versions": {
            "source_version_id": (Text, False),
            "source_id": (Text, False),
            "version_number": (BigInteger, False),
        },
        "source_evidence_source_version_processing": {
            "source_version_id": (Text, False),
            "status": (Text, False),
            "revision": (BigInteger, False),
            "failure_summary": (Text, True),
            "updated_at": (DateTime, False),
        },
        "source_evidence_task_source_associations": {
            "source_association_id": (Text, False),
            "task_id": (Text, False),
            "source_id": (Text, False),
            "source_version_id": (Text, False),
            "membership_state": (Text, False),
            "revision": (BigInteger, False),
            "replaced_by_association_id": (Text, True),
        },
    }
    for table_name, columns in expected.items():
        table = _TABLE_BY_NAME[table_name]
        for column_name, (type_, nullable) in columns.items():
            column = table.c[column_name]
            assert type(column.type) is type_
            assert column.nullable is nullable
    updated_at_type = cast(
        DateTime, tables.SOURCE_VERSION_PROCESSING_TABLE.c.updated_at.type
    )
    assert updated_at_type.timezone is True


def test_primary_unique_foreign_key_and_check_constraint_contracts_are_named() -> None:
    expected_columns = {
        "source_evidence_sources": {
            "pk_source_evidence_sources": ("source_id",),
        },
        "source_evidence_source_versions": {
            "pk_source_evidence_source_versions": ("source_version_id",),
            "uq_source_evidence_source_versions_source_version_number": (
                "source_id",
                "version_number",
            ),
            "uq_source_evidence_source_versions_version_source": (
                "source_version_id",
                "source_id",
            ),
            "fk_source_evidence_source_versions_source_owner": ("source_id",),
            "ck_source_evidence_source_versions_version_number_positive": (),
        },
        "source_evidence_source_version_processing": {
            "pk_source_evidence_source_version_processing": ("source_version_id",),
            "fk_source_evidence_source_version_processing_version_owner": (
                "source_version_id",
            ),
            "ck_source_evidence_source_version_processing_status": (),
            "ck_source_evidence_processing_revision_nonnegative": (),
        },
        "source_evidence_task_source_associations": {
            "pk_source_evidence_task_source_associations": ("source_association_id",),
            "uq_source_evidence_task_source_associations_association_owner": (
                "source_association_id",
                "task_id",
                "source_id",
            ),
            "fk_source_evidence_task_source_associations_task_owner": ("task_id",),
            "fk_source_evidence_task_source_associations_source_owner": ("source_id",),
            "fk_source_evidence_assoc_source_version_owner": (
                "source_version_id",
                "source_id",
            ),
            "fk_source_evidence_task_source_associations_replacement_owner": (
                "replaced_by_association_id",
                "task_id",
                "source_id",
            ),
            "ck_source_evidence_task_source_associations_membership_state": (),
            "ck_source_evidence_assoc_revision_nonnegative": (),
            "ck_source_evidence_assoc_replacement_distinct": (),
            "ck_source_evidence_assoc_replacement_link": (),
        },
    }
    for table_name, constraints in expected_columns.items():
        table = _TABLE_BY_NAME[table_name]
        actual = {constraint.name: constraint for constraint in table.constraints}
        assert set(actual) == set(constraints)
        for name, column_keys in constraints.items():
            constraint = actual[name]
            if isinstance(constraint, (ForeignKeyConstraint, CheckConstraint)):
                if isinstance(constraint, ForeignKeyConstraint):
                    assert tuple(constraint.column_keys) == column_keys
                else:
                    assert column_keys == ()
            elif isinstance(constraint, (PrimaryKeyConstraint, UniqueConstraint)):
                assert tuple(constraint.columns.keys()) == column_keys
            else:
                raise AssertionError(f"unexpected constraint type: {type(constraint)}")


def test_foreign_keys_preserve_source_version_and_replacement_ownership() -> None:
    token = tables.SOURCE_EVIDENCE_SCHEMA_TOKEN
    constraints = {
        constraint.name: constraint
        for constraint in tables.TASK_SOURCE_ASSOCIATIONS_TABLE.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert [
        element.target_fullname
        for element in constraints[
            "fk_source_evidence_assoc_source_version_owner"
        ].elements
    ] == [
        f"{token}.source_evidence_source_versions.source_version_id",
        f"{token}.source_evidence_source_versions.source_id",
    ]
    assert [
        element.target_fullname
        for element in constraints[
            "fk_source_evidence_task_source_associations_replacement_owner"
        ].elements
    ] == [
        f"{token}.source_evidence_task_source_associations.source_association_id",
        f"{token}.source_evidence_task_source_associations.task_id",
        f"{token}.source_evidence_task_source_associations.source_id",
    ]


def test_check_constraint_expressions_match_the_source_migration() -> None:
    expected = {
        "source_evidence_sources": {},
        "source_evidence_source_versions": {
            "ck_source_evidence_source_versions_version_number_positive": (
                "version_number >= 1"
            ),
        },
        "source_evidence_source_version_processing": {
            "ck_source_evidence_source_version_processing_status": (
                "status IN ('registered', 'processing', 'ready', "
                "'ready_with_rejections', 'failed', 'superseded')"
            ),
            "ck_source_evidence_processing_revision_nonnegative": "revision >= 0",
        },
        "source_evidence_task_source_associations": {
            "ck_source_evidence_task_source_associations_membership_state": (
                "membership_state IN ('active', 'removed', 'replaced')"
            ),
            "ck_source_evidence_assoc_revision_nonnegative": "revision >= 0",
            "ck_source_evidence_assoc_replacement_distinct": (
                "replaced_by_association_id IS NULL OR "
                "replaced_by_association_id <> source_association_id"
            ),
            "ck_source_evidence_assoc_replacement_link": (
                "(membership_state = 'replaced' AND "
                "replaced_by_association_id IS NOT NULL) OR "
                "(membership_state <> 'replaced' AND "
                "replaced_by_association_id IS NULL)"
            ),
        },
    }
    for table_name, expressions in expected.items():
        actual = {
            constraint.name: _normalize_sql(constraint.sqltext)
            for constraint in _TABLE_BY_NAME[table_name].constraints
            if isinstance(constraint, CheckConstraint)
        }
        assert actual == expressions


def test_schema_translation_is_explicit_and_does_not_mutate_metadata() -> None:
    before = {table.name: table.schema for table in _TABLES}
    assert tables.schema_translate_map("mvp0_010b2a") == {
        tables.SOURCE_EVIDENCE_SCHEMA_TOKEN: "mvp0_010b2a"
    }
    assert {table.name: table.schema for table in _TABLES} == before
    with pytest.raises(ValueError):
        tables.schema_translate_map("Public")
    with pytest.raises(ValueError):
        tables.schema_translate_map("business-schema")
