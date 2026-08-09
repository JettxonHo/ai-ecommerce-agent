"""Unit contracts for the Durable Dispatch claim/heartbeat application seam."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import UTC, datetime
from inspect import iscoroutinefunction, signature
from typing import get_type_hints

import pytest

from ai_ecommerce_agent.modules.durable_dispatch.application.lease_commands import (
    ClaimNextWorkIntent,
    HeartbeatWorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_errors import (
    DurableDispatchLeaseError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_protocols import (
    DurableDispatchLeaseApplication,
)
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
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import WorkIntentStatus
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ResourceReference,
    Revision,
    RunId,
)

pytestmark = pytest.mark.unit


class _StrSubclass(str):
    pass


def _times() -> tuple[datetime, datetime]:
    return (
        datetime(2026, 8, 10, 12, 0, tzinfo=UTC),
        datetime(2026, 8, 10, 13, 0, tzinfo=UTC),
    )


def _claim_command() -> ClaimNextWorkIntent:
    now, expires = _times()
    return ClaimNextWorkIntent(
        LeaseHolderId("holder-one"),
        DeliveryAttemptId("attempt-one"),
        now,
        expires,
    )


def _heartbeat_command() -> HeartbeatWorkIntentLease:
    now, expires = _times()
    return HeartbeatWorkIntentLease(
        DispatchId("dispatch-one"),
        DeliveryAttemptId("attempt-one"),
        LeaseHolderId("holder-one"),
        FencingToken(1),
        Revision(3),
        now,
        expires,
    )


def _snapshot() -> WorkIntentSnapshot:
    now, _ = _times()
    dispatch_id = DispatchId("dispatch-one")
    return WorkIntentSnapshot(
        WorkIntentEnvelope(
            dispatch_id,
            "process_source",
            "source_processing",
            ResourceReference("task", "task-one"),
            "command-one",
            RunId("run-one"),
            "fingerprint-one",
            "schema-1",
            DomainVersionId("domain-version-one"),
            Revision(2),
            ResourceReference("source_version", "source-version-one"),
            None,
            "ordering-one",
            now,
            now,
        ),
        WorkIntentStatus.AVAILABLE,
        Revision(0),
        False,
        None,
    )


def test_commands_are_frozen_slotted_and_preserve_supplied_values() -> None:
    claim = _claim_command()
    heartbeat = _heartbeat_command()

    assert [field.name for field in fields(claim)] == [
        "holder_id",
        "delivery_attempt_id",
        "now",
        "lease_expires_at",
    ]
    assert [field.name for field in fields(heartbeat)] == [
        "dispatch_id",
        "delivery_attempt_id",
        "holder_id",
        "fencing_token",
        "expected_revision",
        "now",
        "lease_expires_at",
    ]
    assert not hasattr(claim, "__dict__")
    assert not hasattr(heartbeat, "__dict__")
    with pytest.raises(FrozenInstanceError):
        claim.now = claim.now  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        heartbeat.fencing_token = heartbeat.fencing_token  # type: ignore[misc]

    holder = LeaseHolderId("holder-preserved")
    attempt = DeliveryAttemptId("attempt-preserved")
    now, expires = _times()
    command = ClaimNextWorkIntent(holder, attempt, now, expires)
    assert command.holder_id is holder
    assert command.delivery_attempt_id is attempt
    assert command.now is now
    assert command.lease_expires_at is expires
    assert get_type_hints(ClaimNextWorkIntent) == {
        "holder_id": LeaseHolderId,
        "delivery_attempt_id": DeliveryAttemptId,
        "now": datetime,
        "lease_expires_at": datetime,
    }
    assert get_type_hints(HeartbeatWorkIntentLease) == {
        "dispatch_id": DispatchId,
        "delivery_attempt_id": DeliveryAttemptId,
        "holder_id": LeaseHolderId,
        "fencing_token": FencingToken,
        "expected_revision": Revision,
        "now": datetime,
        "lease_expires_at": datetime,
    }


def test_commands_validate_expiry_without_inventing_timezone_policy() -> None:
    now, expires = _times()
    with pytest.raises(ValueError, match="lease_expires_at must be later than now"):
        ClaimNextWorkIntent(
            LeaseHolderId("holder"), DeliveryAttemptId("attempt"), now, now
        )
    with pytest.raises(ValueError, match="lease_expires_at must be later than now"):
        HeartbeatWorkIntentLease(
            DispatchId("dispatch"),
            DeliveryAttemptId("attempt"),
            LeaseHolderId("holder"),
            FencingToken(1),
            Revision(0),
            now,
            now,
        )
    with pytest.raises(ValueError, match="lease datetimes must be comparable"):
        ClaimNextWorkIntent(
            LeaseHolderId("holder"),
            DeliveryAttemptId("attempt"),
            now.replace(tzinfo=None),
            expires,
        )
    with pytest.raises(ValueError, match="lease datetimes must be comparable"):
        HeartbeatWorkIntentLease(
            DispatchId("dispatch"),
            DeliveryAttemptId("attempt"),
            LeaseHolderId("holder"),
            FencingToken(1),
            Revision(0),
            now,
            expires.replace(tzinfo=None),
        )


def test_commands_reject_wrong_typed_values_and_zero_heartbeat_token() -> None:
    now, expires = _times()
    with pytest.raises(TypeError):
        ClaimNextWorkIntent("holder", DeliveryAttemptId("attempt"), now, expires)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        HeartbeatWorkIntentLease(
            DispatchId("dispatch"),
            DeliveryAttemptId("attempt"),
            LeaseHolderId("holder"),
            1,  # type: ignore[arg-type]
            Revision(0),
            now,
            expires,
        )
    with pytest.raises(ValueError, match="fencing token must be greater than zero"):
        HeartbeatWorkIntentLease(
            DispatchId("dispatch"),
            DeliveryAttemptId("attempt"),
            LeaseHolderId("holder"),
            FencingToken.initial(),
            Revision(0),
            now,
            expires,
        )


class _ConformingApplication:
    def claim_next_work_intent(
        self, command: ClaimNextWorkIntent
    ) -> WorkIntentSnapshot | None:
        del command
        return None

    def heartbeat_work_intent_lease(
        self, command: HeartbeatWorkIntentLease
    ) -> WorkIntentSnapshot:
        del command
        return _snapshot()


def test_lease_protocol_is_runtime_checkable_sync_and_exactly_two_methods() -> None:
    assert isinstance(_ConformingApplication(), DurableDispatchLeaseApplication)
    assert not iscoroutinefunction(
        DurableDispatchLeaseApplication.claim_next_work_intent
    )
    assert not iscoroutinefunction(
        DurableDispatchLeaseApplication.heartbeat_work_intent_lease
    )
    assert [
        name
        for name in DurableDispatchLeaseApplication.__dict__
        if not name.startswith("_")
    ] == ["claim_next_work_intent", "heartbeat_work_intent_lease"]
    assert get_type_hints(DurableDispatchLeaseApplication.claim_next_work_intent) == {
        "command": ClaimNextWorkIntent,
        "return": WorkIntentSnapshot | None,
    }
    assert get_type_hints(
        DurableDispatchLeaseApplication.heartbeat_work_intent_lease
    ) == {
        "command": HeartbeatWorkIntentLease,
        "return": WorkIntentSnapshot,
    }
    assert list(
        signature(DurableDispatchLeaseApplication.claim_next_work_intent).parameters
    ) == [
        "self",
        "command",
    ]
    assert list(
        signature(
            DurableDispatchLeaseApplication.heartbeat_work_intent_lease
        ).parameters
    ) == [
        "self",
        "command",
    ]


def test_lease_error_is_slotted_catchable_mutable_and_exactly_typed() -> None:
    dispatch_id = DispatchId("dispatch-error")
    attempt_id = DeliveryAttemptId("attempt-error")
    revision = Revision(4)
    state = WorkIntentStatus.LEASED
    error = DurableDispatchLeaseError(
        "lease_lost",
        "ownership",
        "lease is no longer current",
        True,
        dispatch_id,
        attempt_id,
        revision,
        state,
        "reclaim",
    )

    assert [field.name for field in fields(error)] == [
        "error_code",
        "category",
        "message",
        "retryability",
        "relevant_dispatch_id",
        "delivery_attempt_id",
        "expected_revision",
        "conflicting_state",
        "recovery_hint",
    ]
    assert all(
        name in DurableDispatchLeaseError.__slots__
        for name in (
            "error_code",
            "category",
            "message",
            "retryability",
        )
    )
    assert error.relevant_dispatch_id is dispatch_id
    assert error.delivery_attempt_id is attempt_id
    assert error.expected_revision is revision
    assert error.conflicting_state is state
    assert error.recovery_hint == "reclaim"
    assert str(error) == "lease is no longer current"
    error.message = "updated"
    assert error.message == "updated"
    with pytest.raises(DurableDispatchLeaseError):
        raise error
    assert get_type_hints(DurableDispatchLeaseError) == {
        "error_code": str,
        "category": str,
        "message": str,
        "retryability": bool,
        "relevant_dispatch_id": DispatchId | None,
        "delivery_attempt_id": DeliveryAttemptId | None,
        "expected_revision": Revision | None,
        "conflicting_state": WorkIntentStatus | None,
        "recovery_hint": str | None,
    }


@pytest.mark.parametrize("field", ["error_code", "category", "message"])
def test_lease_error_requires_exact_non_empty_builtin_strings(field: str) -> None:
    values: dict[str, object] = {
        "error_code": "code",
        "category": "category",
        "message": "message",
        "retryability": False,
        "relevant_dispatch_id": None,
    }
    values[field] = ""
    with pytest.raises(ValueError):
        DurableDispatchLeaseError(**values)  # type: ignore[arg-type]
    values[field] = _StrSubclass("subclass")
    with pytest.raises(TypeError):
        DurableDispatchLeaseError(**values)  # type: ignore[arg-type]


def test_lease_error_validates_bool_and_optional_typed_values() -> None:
    base: dict[str, object] = {
        "error_code": "code",
        "category": "category",
        "message": "message",
        "retryability": False,
        "relevant_dispatch_id": None,
    }
    with pytest.raises(TypeError):
        DurableDispatchLeaseError(**(base | {"retryability": 0}))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        DurableDispatchLeaseError(
            **(base | {"relevant_dispatch_id": "dispatch"})  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError):
        DurableDispatchLeaseError(**(base | {"recovery_hint": 1}))  # type: ignore[arg-type]
