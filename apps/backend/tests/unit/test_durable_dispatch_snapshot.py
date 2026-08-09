"""Unit contracts for the immutable Durable Dispatch current-state projection."""

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
    WorkIntentEnvelope,
    WorkIntentLease,
    WorkIntentSnapshot,
    WorkIntentStatus,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
)

pytestmark = pytest.mark.unit


def _build_envelope(dispatch_id: DispatchId | None = None) -> WorkIntentEnvelope:
    timestamp = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
    return WorkIntentEnvelope(
        dispatch_id or DispatchId("dispatch-01"),
        "process_source",
        "operation",
        ResourceReference("task", "task-01"),
        "command-01",
        RunId("run-01"),
        "fingerprint-01",
        "schema-1",
        DomainVersionId("domain-version-01"),
        Revision(2),
        ResourceReference("payload", "payload-01"),
        None,
        None,
        timestamp,
        timestamp,
    )


def _build_lease(dispatch_id: DispatchId) -> WorkIntentLease:
    return WorkIntentLease(
        dispatch_id,
        DeliveryAttemptId("attempt-01"),
        LeaseHolderId("holder-01"),
        FencingToken(3),
        datetime(2026, 8, 9, 13, 0, tzinfo=UTC),
    )


def test_work_intent_snapshot_has_exact_fields_and_immutable_shape() -> None:
    expected_fields = (
        "envelope",
        "status",
        "revision",
        "cancellation_requested",
        "current_lease",
    )
    expected_types = {
        "envelope": WorkIntentEnvelope,
        "status": WorkIntentStatus,
        "revision": Revision,
        "cancellation_requested": bool,
        "current_lease": WorkIntentLease | None,
    }
    snapshot = WorkIntentSnapshot(
        _build_envelope(),
        WorkIntentStatus.AVAILABLE,
        Revision(2),
        False,
        None,
    )

    assert is_dataclass(WorkIntentSnapshot)
    assert tuple(field.name for field in fields(WorkIntentSnapshot)) == expected_fields
    assert WorkIntentSnapshot.__slots__ == expected_fields
    assert get_type_hints(WorkIntentSnapshot) == expected_types
    assert not hasattr(snapshot, "__dict__")

    with pytest.raises(FrozenInstanceError):
        snapshot.status = WorkIntentStatus.SUCCEEDED  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del snapshot.status  # type: ignore[misc]


def test_snapshot_preserves_supplied_values_and_accepts_absent_lease() -> None:
    envelope = _build_envelope()
    status = WorkIntentStatus.SUCCEEDED
    revision = Revision(4)

    snapshot = WorkIntentSnapshot(envelope, status, revision, True, None)

    assert snapshot.envelope is envelope
    assert snapshot.status is status
    assert snapshot.revision is revision
    assert snapshot.cancellation_requested is True
    assert snapshot.current_lease is None


def test_snapshot_accepts_equal_dispatch_id_without_object_identity() -> None:
    envelope = _build_envelope()
    equal_dispatch_id = DispatchId(envelope.dispatch_id.value)
    lease = _build_lease(equal_dispatch_id)

    assert equal_dispatch_id == envelope.dispatch_id
    assert equal_dispatch_id is not envelope.dispatch_id
    snapshot = WorkIntentSnapshot(
        envelope,
        WorkIntentStatus.LEASED,
        Revision(2),
        False,
        lease,
    )

    assert snapshot.current_lease is lease


def test_snapshot_rejects_different_lease_dispatch_identity() -> None:
    envelope = _build_envelope()
    lease = _build_lease(DispatchId("dispatch-other"))

    with pytest.raises(ValueError, match="dispatch"):
        WorkIntentSnapshot(
            envelope,
            WorkIntentStatus.LEASED,
            Revision(2),
            False,
            lease,
        )


@pytest.mark.parametrize(
    ("field_name", "invalid"),
    [
        ("envelope", {"dispatch_id": "dispatch-01"}),
        ("status", "available"),
        ("revision", 2),
        ("cancellation_requested", 1),
        ("current_lease", {"holder_id": "holder-01"}),
    ],
)
def test_snapshot_rejects_raw_values_without_coercion(
    field_name: str, invalid: object
) -> None:
    snapshot = WorkIntentSnapshot(
        _build_envelope(),
        WorkIntentStatus.AVAILABLE,
        Revision(2),
        False,
        None,
    )

    with pytest.raises(TypeError):
        replace(snapshot, **{field_name: invalid})


def test_snapshot_does_not_infer_lifecycle_or_expose_runtime_behavior() -> None:
    for status in (
        WorkIntentStatus.PENDING,
        WorkIntentStatus.SUCCEEDED,
        WorkIntentStatus.CANCELLED,
    ):
        snapshot = WorkIntentSnapshot(
            _build_envelope(), status, Revision(2), False, None
        )
        assert snapshot.current_lease is None

    for forbidden_name in (
        "available",
        "claim",
        "heartbeat",
        "renew",
        "release",
        "takeover",
        "start",
        "complete",
        "fail",
        "retry",
        "cancel",
        "supersede",
        "commit_fence",
    ):
        assert not hasattr(snapshot, forbidden_name)

    with pytest.raises(TypeError):
        replace(snapshot, cancellation_requested=cast(Any, 0))
