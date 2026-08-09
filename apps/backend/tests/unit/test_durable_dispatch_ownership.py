"""Unit contracts for Durable Dispatch lease ownership values."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import UTC, datetime
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.durable_dispatch.public import (
    DeliveryAttemptId,
    DispatchId,
    FencingToken,
    LeaseHolderId,
    WorkIntentLease,
)

pytestmark = pytest.mark.unit


class _StringSubclass(str):
    """Adversarial string subclass that must not cross the holder boundary."""

    def strip(self, chars: str | None = None) -> str:
        raise AssertionError("str subclass methods must not be invoked")


def _build_lease(
    *,
    dispatch_id: DispatchId | None = None,
    delivery_attempt_id: DeliveryAttemptId | None = None,
    holder_id: LeaseHolderId | None = None,
    fencing_token: FencingToken | None = None,
    lease_expires_at: datetime | None = None,
) -> WorkIntentLease:
    return WorkIntentLease(
        dispatch_id or DispatchId("dispatch-01"),
        delivery_attempt_id or DeliveryAttemptId("attempt-01"),
        holder_id or LeaseHolderId(" holder-01 "),
        fencing_token or FencingToken(3),
        lease_expires_at or datetime(2026, 8, 9, 12, 0, tzinfo=UTC),
    )


def test_lease_holder_id_is_exactly_typed_frozen_and_slotted() -> None:
    holder_type = LeaseHolderId
    holder = holder_type(" holder-01 ")

    assert is_dataclass(holder_type)
    assert [field.name for field in fields(holder_type)] == ["value"]
    assert get_type_hints(holder_type) == {"value": str}
    assert holder_type.__slots__ == ("value",)
    assert not hasattr(holder, "__dict__")
    assert holder.value == " holder-01 "

    with pytest.raises(FrozenInstanceError):
        holder.value = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del holder.value  # type: ignore[misc]


def test_lease_holder_id_rejects_empty_values_and_string_subclasses() -> None:
    for invalid in ("", "   ", _StringSubclass("holder-01"), cast(Any, 1)):
        with pytest.raises((TypeError, ValueError)):
            LeaseHolderId(invalid)

    assert LeaseHolderId(" holder-02 ").value == " holder-02 "


def test_work_intent_lease_has_exact_fields_and_immutable_shape() -> None:
    expected_fields = (
        "dispatch_id",
        "delivery_attempt_id",
        "holder_id",
        "fencing_token",
        "lease_expires_at",
    )
    expected_types = {
        "dispatch_id": DispatchId,
        "delivery_attempt_id": DeliveryAttemptId,
        "holder_id": LeaseHolderId,
        "fencing_token": FencingToken,
        "lease_expires_at": datetime,
    }
    lease = _build_lease()

    assert is_dataclass(WorkIntentLease)
    assert tuple(field.name for field in fields(WorkIntentLease)) == expected_fields
    assert WorkIntentLease.__slots__ == expected_fields
    assert get_type_hints(WorkIntentLease) == expected_types
    assert not hasattr(lease, "__dict__")

    with pytest.raises(FrozenInstanceError):
        lease.holder_id = LeaseHolderId("changed")  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del lease.holder_id  # type: ignore[misc]


def test_work_intent_lease_preserves_supplied_typed_values_by_identity() -> None:
    dispatch_id = DispatchId("dispatch-01")
    delivery_attempt_id = DeliveryAttemptId("attempt-01")
    holder_id = LeaseHolderId("holder-01")
    fencing_token = FencingToken(3)
    lease_expires_at = datetime(2026, 8, 9, 12, 0)

    lease = WorkIntentLease(
        dispatch_id,
        delivery_attempt_id,
        holder_id,
        fencing_token,
        lease_expires_at,
    )

    assert lease.dispatch_id is dispatch_id
    assert lease.delivery_attempt_id is delivery_attempt_id
    assert lease.holder_id is holder_id
    assert lease.fencing_token is fencing_token
    assert lease.lease_expires_at is lease_expires_at


@pytest.mark.parametrize(
    ("field_name", "invalid"),
    [
        ("dispatch_id", "dispatch-01"),
        ("delivery_attempt_id", "attempt-01"),
        ("holder_id", "holder-01"),
        ("fencing_token", 3),
        ("lease_expires_at", "2026-08-09T12:00:00Z"),
        ("lease_expires_at", {"timestamp": "2026-08-09T12:00:00Z"}),
    ],
)
def test_work_intent_lease_rejects_raw_typed_values_without_coercion(
    field_name: str, invalid: object
) -> None:
    lease = _build_lease()

    with pytest.raises(TypeError):
        replace(lease, **{field_name: invalid})


def test_work_intent_lease_does_not_compare_or_normalize_timestamps() -> None:
    aware = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
    naive = datetime(2026, 8, 9, 11, 0)

    lease = _build_lease(lease_expires_at=naive)
    assert lease.lease_expires_at is naive
    assert replace(lease, lease_expires_at=aware).lease_expires_at is aware
