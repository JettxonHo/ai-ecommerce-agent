"""Contract checks for the Durable Dispatch SQLAlchemy Core table."""

from __future__ import annotations

from typing import cast

import pytest
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    Text,
    UniqueConstraint,
)

from ai_ecommerce_agent.modules.durable_dispatch.infrastructure import tables

pytestmark = pytest.mark.contract

_TABLE = tables.WORK_INTENTS_TABLE
_COLUMN_ORDER = [
    "dispatch_id",
    "intent_type",
    "owning_operation",
    "target_resource_kind",
    "target_resource_id",
    "command_id",
    "stage_run_id",
    "input_fingerprint",
    "fingerprint_schema_version",
    "base_domain_version_id",
    "expected_revision",
    "payload_resource_kind",
    "payload_resource_id",
    "rerun_of_dispatch_id",
    "ordering_key",
    "created_at",
    "available_at",
    "status",
    "revision",
    "cancellation_requested",
    "delivery_attempt_id",
    "lease_holder_id",
    "fencing_token",
    "lease_expires_at",
    "superseded_by_dispatch_id",
]
_COLUMN_CONTRACT = {
    "dispatch_id": (Text, False),
    "intent_type": (Text, False),
    "owning_operation": (Text, False),
    "target_resource_kind": (Text, False),
    "target_resource_id": (Text, False),
    "command_id": (Text, False),
    "stage_run_id": (Text, True),
    "input_fingerprint": (Text, False),
    "fingerprint_schema_version": (Text, False),
    "base_domain_version_id": (Text, True),
    "expected_revision": (BigInteger, True),
    "payload_resource_kind": (Text, False),
    "payload_resource_id": (Text, False),
    "rerun_of_dispatch_id": (Text, True),
    "ordering_key": (Text, True),
    "created_at": (DateTime, False),
    "available_at": (DateTime, False),
    "status": (Text, False),
    "revision": (BigInteger, False),
    "cancellation_requested": (Boolean, False),
    "delivery_attempt_id": (Text, True),
    "lease_holder_id": (Text, True),
    "fencing_token": (BigInteger, False),
    "lease_expires_at": (DateTime, True),
    "superseded_by_dispatch_id": (Text, True),
}
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
_CHECK_NAMES = {
    "pk_durable_dispatch_work_intents",
    "fk_durable_dispatch_work_intents_rerun_of",
    "fk_durable_dispatch_work_intents_superseded_by",
    "ck_durable_dispatch_work_intents_dispatch_id_nonempty",
    "ck_durable_dispatch_work_intents_intent_type_nonempty",
    "ck_durable_dispatch_work_intents_owning_operation_nonempty",
    "ck_durable_dispatch_work_intents_target_resource_kind_nonempty",
    "ck_durable_dispatch_work_intents_target_resource_id_nonempty",
    "ck_durable_dispatch_work_intents_command_id_nonempty",
    "ck_durable_dispatch_work_intents_input_fingerprint_nonempty",
    "ck_durable_dispatch_work_intents_fp_schema_version_nonempty",
    "ck_durable_dispatch_work_intents_payload_resource_kind_nonempty",
    "ck_durable_dispatch_work_intents_payload_resource_id_nonempty",
    "ck_durable_dispatch_work_intents_stage_run_id_nonempty",
    "ck_durable_dispatch_work_intents_base_version_nonempty",
    "ck_durable_dispatch_work_intents_rerun_of_dispatch_id_nonempty",
    "ck_durable_dispatch_work_intents_ordering_key_nonempty",
    "ck_durable_dispatch_work_intents_delivery_attempt_id_nonempty",
    "ck_durable_dispatch_work_intents_lease_holder_id_nonempty",
    "ck_durable_dispatch_work_intents_status",
    "ck_durable_dispatch_work_intents_revision_nonnegative",
    "ck_durable_dispatch_work_intents_expected_revision_nonnegative",
    "ck_durable_dispatch_work_intents_fencing_token_nonnegative",
    "ck_durable_dispatch_work_intents_available_not_before_created",
    "ck_durable_dispatch_work_intents_rerun_distinct",
    "ck_durable_dispatch_work_intents_lease_tuple",
    "ck_durable_dispatch_work_intents_leased_fencing_token",
    "ck_durable_dispatch_work_intents_superseded_by_nonempty",
    "ck_durable_dispatch_work_intents_superseded_by_distinct",
}


def _normalize_sql(expression: object) -> str:
    """Compare SQL text while ignoring only formatting whitespace."""

    return " ".join(str(expression).split())


def test_metadata_contains_exactly_the_logical_work_intent_table() -> None:
    assert set(tables.DURABLE_DISPATCH_METADATA.tables) == {_TABLE.fullname}
    assert _TABLE.metadata is tables.DURABLE_DISPATCH_METADATA
    assert _TABLE.schema == tables.DURABLE_DISPATCH_SCHEMA_TOKEN
    assert tables.__all__ == [
        "DURABLE_DISPATCH_SCHEMA_TOKEN",
        "DURABLE_DISPATCH_METADATA",
        "WORK_INTENTS_TABLE",
        "schema_translate_map",
    ]


def test_columns_match_migration_order_types_and_nullability() -> None:
    assert [column.name for column in _TABLE.columns] == _COLUMN_ORDER
    for name, (type_, nullable) in _COLUMN_CONTRACT.items():
        column = _TABLE.c[name]
        assert type(column.type) is type_
        assert column.nullable is nullable

    for name in ("created_at", "available_at", "lease_expires_at"):
        date_type = cast(DateTime, _TABLE.c[name].type)
        assert date_type.timezone is True


def test_constraints_match_names_targets_and_exact_sql() -> None:
    constraints = {constraint.name: constraint for constraint in _TABLE.constraints}
    assert set(constraints) == _CHECK_NAMES
    assert all(isinstance(name, str) and len(name) <= 63 for name in constraints)

    primary_key = constraints["pk_durable_dispatch_work_intents"]
    assert isinstance(primary_key, PrimaryKeyConstraint)
    assert tuple(primary_key.columns.keys()) == ("dispatch_id",)

    foreign_key = constraints["fk_durable_dispatch_work_intents_rerun_of"]
    assert isinstance(foreign_key, ForeignKeyConstraint)
    assert tuple(foreign_key.column_keys) == ("rerun_of_dispatch_id",)
    assert [element.target_fullname for element in foreign_key.elements] == [
        f"{tables.DURABLE_DISPATCH_SCHEMA_TOKEN}."
        "durable_dispatch_work_intents.dispatch_id"
    ]

    superseded_by = constraints["fk_durable_dispatch_work_intents_superseded_by"]
    assert isinstance(superseded_by, ForeignKeyConstraint)
    assert tuple(superseded_by.column_keys) == ("superseded_by_dispatch_id",)
    assert [element.target_fullname for element in superseded_by.elements] == [
        f"{tables.DURABLE_DISPATCH_SCHEMA_TOKEN}."
        "durable_dispatch_work_intents.dispatch_id"
    ]

    expected_checks = {
        "ck_durable_dispatch_work_intents_dispatch_id_nonempty": (
            "length(btrim(dispatch_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_intent_type_nonempty": (
            "length(btrim(intent_type)) > 0"
        ),
        "ck_durable_dispatch_work_intents_owning_operation_nonempty": (
            "length(btrim(owning_operation)) > 0"
        ),
        "ck_durable_dispatch_work_intents_target_resource_kind_nonempty": (
            "length(btrim(target_resource_kind)) > 0"
        ),
        "ck_durable_dispatch_work_intents_target_resource_id_nonempty": (
            "length(btrim(target_resource_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_command_id_nonempty": (
            "length(btrim(command_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_input_fingerprint_nonempty": (
            "length(btrim(input_fingerprint)) > 0"
        ),
        "ck_durable_dispatch_work_intents_fp_schema_version_nonempty": (
            "length(btrim(fingerprint_schema_version)) > 0"
        ),
        "ck_durable_dispatch_work_intents_payload_resource_kind_nonempty": (
            "length(btrim(payload_resource_kind)) > 0"
        ),
        "ck_durable_dispatch_work_intents_payload_resource_id_nonempty": (
            "length(btrim(payload_resource_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_stage_run_id_nonempty": (
            "stage_run_id IS NULL OR length(btrim(stage_run_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_base_version_nonempty": (
            "base_domain_version_id IS NULL OR "
            "length(btrim(base_domain_version_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_rerun_of_dispatch_id_nonempty": (
            "rerun_of_dispatch_id IS NULL OR length(btrim(rerun_of_dispatch_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_ordering_key_nonempty": (
            "ordering_key IS NULL OR length(btrim(ordering_key)) > 0"
        ),
        "ck_durable_dispatch_work_intents_delivery_attempt_id_nonempty": (
            "delivery_attempt_id IS NULL OR length(btrim(delivery_attempt_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_lease_holder_id_nonempty": (
            "lease_holder_id IS NULL OR length(btrim(lease_holder_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_status": (
            "status IN (" + ", ".join(repr(value) for value in _STATUS_VALUES) + ")"
        ),
        "ck_durable_dispatch_work_intents_revision_nonnegative": "revision >= 0",
        "ck_durable_dispatch_work_intents_expected_revision_nonnegative": (
            "expected_revision IS NULL OR expected_revision >= 0"
        ),
        "ck_durable_dispatch_work_intents_fencing_token_nonnegative": (
            "fencing_token >= 0"
        ),
        "ck_durable_dispatch_work_intents_available_not_before_created": (
            "available_at >= created_at"
        ),
        "ck_durable_dispatch_work_intents_rerun_distinct": (
            "rerun_of_dispatch_id IS NULL OR rerun_of_dispatch_id <> dispatch_id"
        ),
        "ck_durable_dispatch_work_intents_lease_tuple": (
            "(delivery_attempt_id IS NULL AND lease_holder_id IS NULL AND "
            "lease_expires_at IS NULL) OR "
            "(delivery_attempt_id IS NOT NULL AND lease_holder_id IS NOT NULL AND "
            "lease_expires_at IS NOT NULL)"
        ),
        "ck_durable_dispatch_work_intents_leased_fencing_token": (
            "(delivery_attempt_id IS NULL AND lease_holder_id IS NULL AND "
            "lease_expires_at IS NULL) OR fencing_token >= 1"
        ),
        "ck_durable_dispatch_work_intents_superseded_by_nonempty": (
            "superseded_by_dispatch_id IS NULL OR "
            "length(btrim(superseded_by_dispatch_id)) > 0"
        ),
        "ck_durable_dispatch_work_intents_superseded_by_distinct": (
            "superseded_by_dispatch_id IS NULL OR "
            "superseded_by_dispatch_id <> dispatch_id"
        ),
    }
    actual_checks = {
        constraint.name: _normalize_sql(constraint.sqltext)
        for constraint in _TABLE.constraints
        if isinstance(constraint, CheckConstraint)
    }
    assert actual_checks == {
        name: _normalize_sql(expression) for name, expression in expected_checks.items()
    }


def test_no_semantic_unique_constraint_or_non_primary_index_exists() -> None:
    assert _TABLE.indexes == set()
    assert not any(
        isinstance(constraint, UniqueConstraint)
        and not isinstance(constraint, PrimaryKeyConstraint)
        for constraint in _TABLE.constraints
    )


def test_schema_translation_is_explicit_fresh_and_validated() -> None:
    before = _TABLE.schema
    first = tables.schema_translate_map("mvp0_018g")
    second = tables.schema_translate_map("business_42")
    assert first == {tables.DURABLE_DISPATCH_SCHEMA_TOKEN: "mvp0_018g"}
    assert second == {tables.DURABLE_DISPATCH_SCHEMA_TOKEN: "business_42"}
    assert first is not second
    assert _TABLE.schema == before
    for invalid in ("", "Public", "business-schema", "business.schema", "foo;drop"):
        with pytest.raises(ValueError):
            tables.schema_translate_map(invalid)
