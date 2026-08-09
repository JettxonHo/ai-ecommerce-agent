"""Unit contracts for the immutable Durable Work Intent envelope."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.durable_dispatch.public import (
    DispatchId,
    WorkIntentEnvelope,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
)

pytestmark = pytest.mark.unit


class _StringSubclass(str):
    """Adversarial string subclass that must not cross exact string fields."""

    def strip(self, chars: str | None = None) -> str:
        raise AssertionError("str subclass methods must not be invoked")


def _build_envelope(
    *,
    dispatch_id: DispatchId | None = None,
    intent_type: str = " process_source ",
    owning_operation: str = " operation ",
    target_scope: ResourceReference | None = None,
    command_id: str = " command-1 ",
    stage_run_id: RunId | None = None,
    input_fingerprint: str = " opaque-fingerprint ",
    fingerprint_schema_version: str = " schema-1 ",
    base_domain_version_id: DomainVersionId | None = None,
    expected_revision: Revision | None = None,
    payload_reference: ResourceReference | None = None,
    rerun_of: DispatchId | None = None,
    ordering_key: str | None = " order-1 ",
    created_at: datetime | None = None,
    available_at: datetime | None = None,
) -> WorkIntentEnvelope:
    created = created_at or datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
    available = available_at or created
    return WorkIntentEnvelope(
        dispatch_id or DispatchId("dispatch-1"),
        intent_type,
        owning_operation,
        target_scope or ResourceReference("task", " task-1 "),
        command_id,
        stage_run_id if stage_run_id is not None else RunId("run-1"),
        input_fingerprint,
        fingerprint_schema_version,
        base_domain_version_id
        if base_domain_version_id is not None
        else DomainVersionId("domain-version-1"),
        expected_revision if expected_revision is not None else Revision(2),
        payload_reference or ResourceReference("payload", " payload-1 "),
        rerun_of,
        ordering_key,
        created,
        available,
    )


def test_work_intent_envelope_is_exactly_typed_frozen_and_slotted() -> None:
    expected_fields = (
        "dispatch_id",
        "intent_type",
        "owning_operation",
        "target_scope",
        "command_id",
        "stage_run_id",
        "input_fingerprint",
        "fingerprint_schema_version",
        "base_domain_version_id",
        "expected_revision",
        "payload_reference",
        "rerun_of",
        "ordering_key",
        "created_at",
        "available_at",
    )
    expected_types = {
        "dispatch_id": DispatchId,
        "intent_type": str,
        "owning_operation": str,
        "target_scope": ResourceReference,
        "command_id": str,
        "stage_run_id": RunId | None,
        "input_fingerprint": str,
        "fingerprint_schema_version": str,
        "base_domain_version_id": DomainVersionId | None,
        "expected_revision": Revision | None,
        "payload_reference": ResourceReference,
        "rerun_of": DispatchId | None,
        "ordering_key": str | None,
        "created_at": datetime,
        "available_at": datetime,
    }
    value = _build_envelope()

    assert is_dataclass(WorkIntentEnvelope)
    assert tuple(field.name for field in fields(WorkIntentEnvelope)) == expected_fields
    assert WorkIntentEnvelope.__slots__ == expected_fields
    assert get_type_hints(WorkIntentEnvelope) == expected_types
    assert not hasattr(value, "__dict__")

    field_name = "intent_type"
    with pytest.raises(FrozenInstanceError):
        setattr(value, field_name, "changed")
    with pytest.raises(FrozenInstanceError):
        delattr(value, field_name)


def test_work_intent_envelope_preserves_supplied_values_without_normalization() -> None:
    dispatch_id = DispatchId("dispatch-1")
    target_scope = ResourceReference(" task ", " task-1 ")
    stage_run_id = RunId("run-1")
    base_domain_version_id = DomainVersionId("domain-version-1")
    expected_revision = Revision(2)
    payload_reference = ResourceReference(" payload ", " payload-1 ")
    created_at = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
    available_at = created_at + timedelta(minutes=5)

    value = WorkIntentEnvelope(
        dispatch_id,
        " process_source ",
        " operation ",
        target_scope,
        " command-1 ",
        stage_run_id,
        " opaque-fingerprint ",
        " schema-1 ",
        base_domain_version_id,
        expected_revision,
        payload_reference,
        None,
        " order-1 ",
        created_at,
        available_at,
    )

    assert value.dispatch_id is dispatch_id
    assert value.intent_type == " process_source "
    assert value.owning_operation == " operation "
    assert value.target_scope is target_scope
    assert value.command_id == " command-1 "
    assert value.stage_run_id is stage_run_id
    assert value.input_fingerprint == " opaque-fingerprint "
    assert value.fingerprint_schema_version == " schema-1 "
    assert value.base_domain_version_id is base_domain_version_id
    assert value.expected_revision is expected_revision
    assert value.payload_reference is payload_reference
    assert value.rerun_of is None
    assert value.ordering_key == " order-1 "
    assert value.created_at is created_at
    assert value.available_at is available_at
    assert not hasattr(value, "payload")
    assert not hasattr(value, "fingerprint_algorithm")
    assert not hasattr(value, "status")


def test_optional_context_fields_can_be_absent() -> None:
    value = replace(
        _build_envelope(),
        stage_run_id=None,
        base_domain_version_id=None,
        expected_revision=None,
        rerun_of=None,
        ordering_key=None,
    )

    assert value.stage_run_id is None
    assert value.base_domain_version_id is None
    assert value.expected_revision is None
    assert value.rerun_of is None
    assert value.ordering_key is None


@pytest.mark.parametrize(
    "field_name",
    [
        "intent_type",
        "owning_operation",
        "command_id",
        "input_fingerprint",
        "fingerprint_schema_version",
    ],
)
def test_required_strings_reject_empty_values_and_subclasses(field_name: str) -> None:
    value = _build_envelope()

    for invalid in ("", "   ", _StringSubclass("valid"), cast(Any, 1)):
        with pytest.raises((TypeError, ValueError)):
            replace(value, **{field_name: invalid})


def test_optional_ordering_key_rejects_invalid_values_and_preserves_valid_strings() -> (
    None
):
    value = _build_envelope(ordering_key=None)

    assert value.ordering_key is None
    assert replace(value, ordering_key=" order-2 ").ordering_key == " order-2 "
    with pytest.raises(ValueError):
        replace(value, ordering_key="")
    with pytest.raises(ValueError):
        replace(value, ordering_key="   ")
    with pytest.raises(TypeError):
        replace(value, ordering_key=cast(Any, _StringSubclass("order")))
    with pytest.raises(TypeError):
        replace(value, ordering_key=cast(Any, 1))


@pytest.mark.parametrize(
    ("field_name", "invalid"),
    [
        ("dispatch_id", "dispatch-1"),
        ("target_scope", {"resource_kind": "task"}),
        ("stage_run_id", "run-1"),
        ("base_domain_version_id", "domain-version-1"),
        ("expected_revision", 2),
        ("payload_reference", {"resource_id": "payload-1"}),
        ("rerun_of", "dispatch-previous"),
        ("created_at", "2026-08-09T12:00:00Z"),
        ("available_at", "2026-08-09T12:00:00Z"),
    ],
)
def test_typed_fields_reject_raw_values_without_coercion(
    field_name: str, invalid: object
) -> None:
    value = _build_envelope()

    with pytest.raises(TypeError):
        replace(value, **{field_name: invalid})


def test_rerun_reference_must_be_a_distinct_dispatch_identity() -> None:
    value = _build_envelope()
    previous_dispatch = DispatchId("dispatch-previous")
    equal_dispatch = DispatchId(value.dispatch_id.value)

    assert replace(value, rerun_of=previous_dispatch).rerun_of is previous_dispatch
    with pytest.raises(ValueError, match="rerun_of"):
        replace(value, rerun_of=value.dispatch_id)
    assert equal_dispatch == value.dispatch_id
    assert equal_dispatch is not value.dispatch_id
    with pytest.raises(ValueError, match="rerun_of"):
        replace(value, rerun_of=equal_dispatch)


def test_available_at_must_not_precede_created_at() -> None:
    created_at = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
    value = _build_envelope(created_at=created_at, available_at=created_at)

    assert value.available_at == value.created_at
    with pytest.raises(ValueError, match="available_at"):
        replace(value, available_at=created_at - timedelta(seconds=1))


def test_mixed_aware_and_naive_datetimes_fail_with_stable_validation_error() -> None:
    aware = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
    naive = datetime(2026, 8, 9, 12, 0)
    value = _build_envelope(created_at=aware, available_at=aware)

    with pytest.raises(ValueError, match="comparable datetimes"):
        replace(value, available_at=naive)
    with pytest.raises(ValueError, match="comparable datetimes"):
        replace(value, created_at=naive)
