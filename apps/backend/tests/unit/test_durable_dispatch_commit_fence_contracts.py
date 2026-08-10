"""Unit contracts for the transaction-neutral completion participant seam."""

from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import UTC, datetime
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.durable_dispatch.application.completion_commands import (  # noqa: E501
    CompleteOwnedWorkIntent,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.completion_protocols import (  # noqa: E501
    DurableDispatchCommitFenceParticipant,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.completion_results import (
    WorkIntentCompletionResult,
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
    WorkIntentLease,
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

_NOW = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)


class _PoisonStr(str):
    def strip(self, *args: object, **kwargs: object) -> str:
        del args, kwargs
        raise AssertionError("string subclass methods must not be invoked")


class _DateTimeSubclass(datetime):
    pass


def _envelope(dispatch_id: DispatchId | None = None) -> WorkIntentEnvelope:
    return WorkIntentEnvelope(
        dispatch_id or DispatchId("dispatch-completion"),
        "process_source",
        "source_processing",
        ResourceReference("task", "task-completion"),
        "command-completion",
        RunId("run-completion"),
        "fingerprint-completion",
        "schema-1",
        DomainVersionId("domain-version-completion"),
        Revision(2),
        ResourceReference("source_version", "source-completion"),
        None,
        "ordering-completion",
        _NOW,
        _NOW,
    )


def _snapshot(
    *,
    status: WorkIntentStatus = WorkIntentStatus.SUCCEEDED,
    current_lease: WorkIntentLease | None = None,
) -> WorkIntentSnapshot:
    return WorkIntentSnapshot(
        _envelope(),
        status,
        Revision(4),
        False,
        current_lease,
    )


def _lease() -> WorkIntentLease:
    return WorkIntentLease(
        DispatchId("dispatch-completion"),
        DeliveryAttemptId("attempt-completion"),
        LeaseHolderId("holder-completion"),
        FencingToken(7),
        _NOW,
    )


def _command() -> CompleteOwnedWorkIntent:
    return CompleteOwnedWorkIntent(
        DispatchId("dispatch-completion"),
        DeliveryAttemptId("attempt-completion"),
        LeaseHolderId("holder-completion"),
        FencingToken(7),
        Revision(4),
        "command-completion",
        "fingerprint-completion",
        "schema-1",
        ResourceReference("result", "result-completion"),
        _NOW,
    )


def test_completion_command_has_exact_frozen_slotted_fields_and_preserves_values() -> (
    None
):
    dispatch_id = DispatchId("dispatch-preserved")
    attempt_id = DeliveryAttemptId("attempt-preserved")
    holder_id = LeaseHolderId("holder-preserved")
    token = FencingToken(8)
    revision = Revision(5)
    result_reference = ResourceReference("result", "result-preserved")
    now = datetime(2026, 8, 10, 13, 0, tzinfo=UTC)
    command = CompleteOwnedWorkIntent(
        dispatch_id,
        attempt_id,
        holder_id,
        token,
        revision,
        "command-preserved",
        "fingerprint-preserved",
        "schema-preserved",
        result_reference,
        now,
    )
    expected_fields = (
        "dispatch_id",
        "delivery_attempt_id",
        "holder_id",
        "fencing_token",
        "expected_work_intent_revision",
        "expected_command_id",
        "expected_input_fingerprint",
        "expected_fingerprint_schema_version",
        "result_reference",
        "now",
    )
    expected_hints = {
        "dispatch_id": DispatchId,
        "delivery_attempt_id": DeliveryAttemptId,
        "holder_id": LeaseHolderId,
        "fencing_token": FencingToken,
        "expected_work_intent_revision": Revision,
        "expected_command_id": str,
        "expected_input_fingerprint": str,
        "expected_fingerprint_schema_version": str,
        "result_reference": ResourceReference,
        "now": datetime,
    }
    assert type(command) is CompleteOwnedWorkIntent
    assert is_dataclass(CompleteOwnedWorkIntent)
    assert (
        tuple(field.name for field in fields(CompleteOwnedWorkIntent))
        == expected_fields
    )
    assert CompleteOwnedWorkIntent.__slots__ == expected_fields
    assert get_type_hints(CompleteOwnedWorkIntent) == expected_hints
    assert not hasattr(command, "__dict__")
    assert command.dispatch_id is dispatch_id
    assert command.delivery_attempt_id is attempt_id
    assert command.holder_id is holder_id
    assert command.fencing_token is token
    assert command.expected_work_intent_revision is revision
    assert command.result_reference is result_reference
    assert command.now is now
    with pytest.raises(FrozenInstanceError):
        command.now = _NOW  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del command.result_reference  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name",
    [
        "expected_command_id",
        "expected_input_fingerprint",
        "expected_fingerprint_schema_version",
    ],
)
def test_completion_command_rejects_blank_and_string_subclasses(
    field_name: str,
) -> None:
    command = _command()
    with pytest.raises(ValueError):
        replace(command, **{field_name: "   "})  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        replace(command, **{field_name: _PoisonStr("subclass")})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "factory",
    [
        lambda: CompleteOwnedWorkIntent(
            cast(DispatchId, "raw"),
            DeliveryAttemptId("attempt-completion"),
            LeaseHolderId("holder-completion"),
            FencingToken(7),
            Revision(4),
            "command-completion",
            "fingerprint-completion",
            "schema-1",
            ResourceReference("result", "result-completion"),
            _NOW,
        ),
        lambda: CompleteOwnedWorkIntent(
            DispatchId("dispatch-completion"),
            cast(DeliveryAttemptId, "raw"),
            LeaseHolderId("holder-completion"),
            FencingToken(7),
            Revision(4),
            "command-completion",
            "fingerprint-completion",
            "schema-1",
            ResourceReference("result", "result-completion"),
            _NOW,
        ),
        lambda: CompleteOwnedWorkIntent(
            DispatchId("dispatch-completion"),
            DeliveryAttemptId("attempt-completion"),
            cast(LeaseHolderId, "raw"),
            FencingToken(7),
            Revision(4),
            "command-completion",
            "fingerprint-completion",
            "schema-1",
            ResourceReference("result", "result-completion"),
            _NOW,
        ),
        lambda: CompleteOwnedWorkIntent(
            DispatchId("dispatch-completion"),
            DeliveryAttemptId("attempt-completion"),
            LeaseHolderId("holder-completion"),
            cast(FencingToken, 7),
            Revision(4),
            "command-completion",
            "fingerprint-completion",
            "schema-1",
            ResourceReference("result", "result-completion"),
            _NOW,
        ),
        lambda: CompleteOwnedWorkIntent(
            DispatchId("dispatch-completion"),
            DeliveryAttemptId("attempt-completion"),
            LeaseHolderId("holder-completion"),
            FencingToken(7),
            cast(Revision, 4),
            "command-completion",
            "fingerprint-completion",
            "schema-1",
            ResourceReference("result", "result-completion"),
            _NOW,
        ),
        lambda: CompleteOwnedWorkIntent(
            DispatchId("dispatch-completion"),
            DeliveryAttemptId("attempt-completion"),
            LeaseHolderId("holder-completion"),
            FencingToken(7),
            Revision(4),
            "command-completion",
            "fingerprint-completion",
            "schema-1",
            cast(ResourceReference, "raw"),
            _NOW,
        ),
        lambda: CompleteOwnedWorkIntent(
            DispatchId("dispatch-completion"),
            DeliveryAttemptId("attempt-completion"),
            LeaseHolderId("holder-completion"),
            FencingToken(7),
            Revision(4),
            "command-completion",
            "fingerprint-completion",
            "schema-1",
            ResourceReference("result", "result-completion"),
            _DateTimeSubclass(2026, 8, 10, 12, tzinfo=UTC),
        ),
    ],
)
def test_completion_command_rejects_raw_typed_values(factory: object) -> None:
    with pytest.raises(TypeError):
        factory()  # type: ignore[operator]


def test_completion_result_has_exact_frozen_slotted_fields_and_preserves_values() -> (
    None
):
    snapshot = _snapshot()
    result_reference = ResourceReference("result", "result-preserved")
    result = WorkIntentCompletionResult(snapshot, result_reference)
    expected_fields = ("completed_work_intent", "result_reference")
    assert is_dataclass(WorkIntentCompletionResult)
    assert (
        tuple(field.name for field in fields(WorkIntentCompletionResult))
        == expected_fields
    )
    assert WorkIntentCompletionResult.__slots__ == expected_fields
    assert get_type_hints(WorkIntentCompletionResult) == {
        "completed_work_intent": WorkIntentSnapshot,
        "result_reference": ResourceReference,
    }
    assert not hasattr(result, "__dict__")
    assert result.completed_work_intent is snapshot
    assert result.result_reference is result_reference
    with pytest.raises(FrozenInstanceError):
        result.result_reference = ResourceReference("result", "other")  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del result.completed_work_intent  # type: ignore[misc]


@pytest.mark.parametrize(
    ("snapshot", "result_reference"),
    [
        (cast(WorkIntentSnapshot, "raw"), ResourceReference("result", "raw-snapshot")),
        (_snapshot(), cast(ResourceReference, "raw")),
    ],
)
def test_completion_result_rejects_raw_typed_values(
    snapshot: WorkIntentSnapshot,
    result_reference: ResourceReference,
) -> None:
    with pytest.raises(TypeError):
        WorkIntentCompletionResult(snapshot, result_reference)


@pytest.mark.parametrize("status", list(WorkIntentStatus))
def test_completion_result_accepts_only_succeeded_without_lease(
    status: WorkIntentStatus,
) -> None:
    snapshot = _snapshot(status=status)
    if status is WorkIntentStatus.SUCCEEDED:
        assert (
            WorkIntentCompletionResult(
                snapshot, ResourceReference("result", "result-status")
            ).completed_work_intent
            is snapshot
        )
    else:
        with pytest.raises(ValueError):
            WorkIntentCompletionResult(
                snapshot, ResourceReference("result", "result-status")
            )

    leased = replace(snapshot, current_lease=_lease())
    with pytest.raises(ValueError):
        WorkIntentCompletionResult(leased, ResourceReference("result", "result-leased"))


class _ParticipantDouble:
    def complete_owned_work_intent(
        self, command: CompleteOwnedWorkIntent
    ) -> WorkIntentCompletionResult:
        raise NotImplementedError(command)


def test_participant_protocol_is_sync_runtime_checkable_with_exact_signature() -> None:
    assert isinstance(_ParticipantDouble(), DurableDispatchCommitFenceParticipant)
    assert {
        name
        for name in DurableDispatchCommitFenceParticipant.__dict__
        if not name.startswith("_")
    } == {"complete_owned_work_intent"}
    method = DurableDispatchCommitFenceParticipant.complete_owned_work_intent
    assert list(inspect.signature(method).parameters) == ["self", "command"]
    assert get_type_hints(method) == {
        "command": CompleteOwnedWorkIntent,
        "return": WorkIntentCompletionResult,
    }
    assert not inspect.iscoroutinefunction(method)
