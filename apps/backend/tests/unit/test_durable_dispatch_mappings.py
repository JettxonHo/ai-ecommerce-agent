"""Unit contracts for Durable Dispatch primitive row mappings."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from ai_ecommerce_agent.modules.durable_dispatch.domain.envelope import (
    WorkIntentEnvelope,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.identity import (
    DeliveryAttemptId,
    DispatchId,
    FencingToken,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.ownership import (
    LeaseHolderId,
    WorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import (
    WorkIntentStatus,
)
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure.mappings import (
    work_intent_row_to_snapshot,
    work_intent_snapshot_to_insert_row,
    work_intent_snapshot_to_update_values,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
)

pytestmark = pytest.mark.unit

_CREATED_AT = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
_AVAILABLE_AT = _CREATED_AT + timedelta(minutes=5)
_LEASE_EXPIRES_AT = _AVAILABLE_AT + timedelta(minutes=15)
_INSERT_KEYS = [
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
]


def _build_snapshot(
    *,
    current_lease: WorkIntentLease | None = None,
    optional_fields: bool = True,
) -> WorkIntentSnapshot:
    envelope = WorkIntentEnvelope(
        DispatchId("dispatch-01"),
        " process_source ",
        " operation ",
        ResourceReference(" task ", " task-01 "),
        " command-01 ",
        RunId("run-01") if optional_fields else None,
        " fingerprint-01 ",
        " schema-1 ",
        DomainVersionId("domain-version-01") if optional_fields else None,
        Revision(2) if optional_fields else None,
        ResourceReference(" payload ", " payload-01 "),
        DispatchId("dispatch-previous") if optional_fields else None,
        " ordering-01 " if optional_fields else None,
        _CREATED_AT,
        _AVAILABLE_AT,
    )
    return WorkIntentSnapshot(
        envelope,
        WorkIntentStatus.IN_PROGRESS,
        Revision(3),
        True,
        current_lease,
    )


def _build_leased_snapshot() -> WorkIntentSnapshot:
    dispatch_id = DispatchId("dispatch-01")
    lease = WorkIntentLease(
        dispatch_id,
        DeliveryAttemptId("attempt-01"),
        LeaseHolderId(" holder-01 "),
        FencingToken(7),
        _LEASE_EXPIRES_AT,
    )
    return _build_snapshot(current_lease=lease)


def test_no_lease_insert_uses_exact_24_keys_and_initial_fencing_token() -> None:
    snapshot = _build_snapshot(optional_fields=False)

    row = work_intent_snapshot_to_insert_row(snapshot)

    assert list(row) == _INSERT_KEYS
    assert row == {
        "dispatch_id": "dispatch-01",
        "intent_type": " process_source ",
        "owning_operation": " operation ",
        "target_resource_kind": " task ",
        "target_resource_id": " task-01 ",
        "command_id": " command-01 ",
        "stage_run_id": None,
        "input_fingerprint": " fingerprint-01 ",
        "fingerprint_schema_version": " schema-1 ",
        "base_domain_version_id": None,
        "expected_revision": None,
        "payload_resource_kind": " payload ",
        "payload_resource_id": " payload-01 ",
        "rerun_of_dispatch_id": None,
        "ordering_key": None,
        "created_at": _CREATED_AT,
        "available_at": _AVAILABLE_AT,
        "status": "in_progress",
        "revision": 3,
        "cancellation_requested": True,
        "delivery_attempt_id": None,
        "lease_holder_id": None,
        "fencing_token": 0,
        "lease_expires_at": None,
    }
    assert work_intent_row_to_snapshot(row) == snapshot


def test_leased_insert_preserves_lease_primitives_and_round_trips() -> None:
    snapshot = _build_leased_snapshot()

    row = work_intent_snapshot_to_insert_row(snapshot)

    assert row["delivery_attempt_id"] == "attempt-01"
    assert row["lease_holder_id"] == " holder-01 "
    assert row["fencing_token"] == 7
    assert row["lease_expires_at"] is _LEASE_EXPIRES_AT
    restored = work_intent_row_to_snapshot(row)
    assert restored == snapshot
    assert restored.current_lease is not None
    assert restored.current_lease.dispatch_id == restored.envelope.dispatch_id


def test_retained_fencing_token_is_validated_but_hidden_from_no_lease_snapshot() -> (
    None
):
    snapshot = _build_snapshot()
    row = work_intent_snapshot_to_insert_row(snapshot)
    row["fencing_token"] = 11

    restored = work_intent_row_to_snapshot(row)

    assert restored == snapshot
    assert restored.current_lease is None
    update_values = work_intent_snapshot_to_update_values(restored)
    assert "fencing_token" not in update_values
    assert update_values["delivery_attempt_id"] is None
    assert update_values["lease_holder_id"] is None
    assert update_values["lease_expires_at"] is None


def test_no_lease_update_values_clear_only_mutable_lease_columns() -> None:
    values = work_intent_snapshot_to_update_values(_build_snapshot())

    assert values == {
        "status": "in_progress",
        "revision": 3,
        "cancellation_requested": True,
        "delivery_attempt_id": None,
        "lease_holder_id": None,
        "lease_expires_at": None,
    }
    assert "fencing_token" not in values
    assert (
        not {
            "dispatch_id",
            "intent_type",
            "owning_operation",
            "target_resource_kind",
            "target_resource_id",
            "command_id",
            "created_at",
            "available_at",
            "ordering_key",
            "expected_revision",
        }
        & values.keys()
    )


def test_leased_update_values_include_current_fencing_token() -> None:
    values = work_intent_snapshot_to_update_values(_build_leased_snapshot())

    assert values == {
        "status": "in_progress",
        "revision": 3,
        "cancellation_requested": True,
        "delivery_attempt_id": "attempt-01",
        "lease_holder_id": " holder-01 ",
        "lease_expires_at": _LEASE_EXPIRES_AT,
        "fencing_token": 7,
    }


def test_optional_envelope_fields_round_trip_as_nulls() -> None:
    snapshot = _build_snapshot(optional_fields=False)
    restored = work_intent_row_to_snapshot(work_intent_snapshot_to_insert_row(snapshot))

    assert restored.envelope.stage_run_id is None
    assert restored.envelope.base_domain_version_id is None
    assert restored.envelope.expected_revision is None
    assert restored.envelope.rerun_of is None
    assert restored.envelope.ordering_key is None


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("delivery_attempt_id", "attempt-01"),
        ("lease_holder_id", "holder-01"),
        ("lease_expires_at", _LEASE_EXPIRES_AT),
    ],
)
def test_partial_lease_tuple_is_rejected_with_stable_value_error(
    column: str, value: object
) -> None:
    row = work_intent_snapshot_to_insert_row(_build_snapshot())
    row[column] = value

    with pytest.raises(
        ValueError, match="lease columns must be all null or all non-null"
    ):
        work_intent_row_to_snapshot(row)


@pytest.mark.parametrize(
    ("column", "value", "error"),
    [
        ("status", "unknown", ValueError),
        ("revision", -1, ValueError),
        ("expected_revision", -1, ValueError),
        ("fencing_token", -1, ValueError),
        ("rerun_of_dispatch_id", "dispatch-01", ValueError),
        (
            "available_at",
            _CREATED_AT - timedelta(seconds=1),
            ValueError,
        ),
    ],
)
def test_invalid_persisted_primitives_propagate_existing_invariants(
    column: str, value: object, error: type[Exception]
) -> None:
    row = work_intent_snapshot_to_insert_row(_build_snapshot())
    row[column] = value

    with pytest.raises(error):
        work_intent_row_to_snapshot(row)


def test_mapping_interface_has_exact_three_symbols_without_generic_alias() -> None:
    from ai_ecommerce_agent.modules.durable_dispatch.infrastructure import mappings

    assert mappings.__all__ == [
        "work_intent_row_to_snapshot",
        "work_intent_snapshot_to_insert_row",
        "work_intent_snapshot_to_update_values",
    ]
    assert not hasattr(mappings, "work_intent_snapshot_to_row")
