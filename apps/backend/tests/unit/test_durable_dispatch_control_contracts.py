"""Unit contracts for Durable Dispatch cancellation and supersession controls."""

from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.durable_dispatch.application.control_commands import (
    AcknowledgeWorkIntentStop,
    RequestWorkIntentCancellation,
    SupersedeWorkIntent,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_errors import (
    DurableDispatchControlError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_protocols import (
    DurableDispatchControlApplication,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_queries import (
    CheckOwnedWorkIntentControl,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_results import (
    OwnedWorkIntentControlCheck,
    WorkIntentControlDisposition,
    WorkIntentSupersessionResult,
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

_AWARE_NOW = datetime(2026, 8, 10, 12, 0, tzinfo=UTC)
_NAIVE_NOW = datetime(2026, 8, 10, 12, 0)


def _envelope(
    dispatch_id: DispatchId | None = None,
    *,
    rerun_of: DispatchId | None = None,
) -> WorkIntentEnvelope:
    dispatch_id = dispatch_id or DispatchId("dispatch-control")
    return WorkIntentEnvelope(
        dispatch_id,
        "process_source",
        "source_processing",
        ResourceReference("task", "task-control"),
        "command-control",
        RunId("run-control"),
        "fingerprint-control",
        "schema-1",
        DomainVersionId("domain-version-control"),
        Revision(2),
        ResourceReference("source_version", "source-control"),
        rerun_of,
        "ordering-control",
        _AWARE_NOW,
        _AWARE_NOW,
    )


def _snapshot(
    *,
    status: WorkIntentStatus = WorkIntentStatus.LEASED,
    cancellation_requested: bool = False,
    superseded_by: DispatchId | None = None,
    revision: int = 3,
    lease: WorkIntentLease | None = None,
    dispatch_id: DispatchId | None = None,
) -> WorkIntentSnapshot:
    dispatch_id = dispatch_id or DispatchId("dispatch-control")
    if lease is None and status in {
        WorkIntentStatus.LEASED,
        WorkIntentStatus.IN_PROGRESS,
    }:
        lease = WorkIntentLease(
            dispatch_id,
            DeliveryAttemptId("attempt-control"),
            LeaseHolderId("holder-control"),
            FencingToken(3),
            _AWARE_NOW,
        )
    return WorkIntentSnapshot(
        _envelope(dispatch_id),
        status,
        Revision(revision),
        cancellation_requested,
        lease,
        superseded_by,
    )


def _stop_ack(*, now: datetime = _AWARE_NOW) -> AcknowledgeWorkIntentStop:
    return AcknowledgeWorkIntentStop(
        DispatchId("dispatch-control"),
        DeliveryAttemptId("attempt-control"),
        LeaseHolderId("holder-control"),
        FencingToken(3),
        Revision(3),
        now,
    )


def test_control_commands_have_exact_frozen_slotted_fields_and_preserve_values() -> (
    None
):
    dispatch_id = DispatchId("dispatch-control")
    attempt_id = DeliveryAttemptId("attempt-control")
    holder_id = LeaseHolderId("holder-control")
    token = FencingToken(3)
    revision = Revision(3)
    successor_id = DispatchId("dispatch-successor")
    successor = _envelope(successor_id, rerun_of=dispatch_id)

    owned_query = CheckOwnedWorkIntentControl(
        dispatch_id, attempt_id, holder_id, token, revision, _NAIVE_NOW
    )
    values = (
        owned_query,
        RequestWorkIntentCancellation(dispatch_id, revision, _NAIVE_NOW),
        SupersedeWorkIntent(dispatch_id, successor, revision, _NAIVE_NOW),
        _stop_ack(now=_NAIVE_NOW),
    )
    expected = (
        (
            CheckOwnedWorkIntentControl,
            (
                "dispatch_id",
                "delivery_attempt_id",
                "holder_id",
                "fencing_token",
                "expected_revision",
                "now",
            ),
        ),
        (
            RequestWorkIntentCancellation,
            ("dispatch_id", "expected_revision", "now"),
        ),
        (
            SupersedeWorkIntent,
            ("dispatch_id", "successor_envelope", "expected_revision", "now"),
        ),
        (
            AcknowledgeWorkIntentStop,
            (
                "dispatch_id",
                "delivery_attempt_id",
                "holder_id",
                "fencing_token",
                "expected_revision",
                "now",
            ),
        ),
    )
    expected_annotations = (
        {
            "dispatch_id": DispatchId,
            "delivery_attempt_id": DeliveryAttemptId,
            "holder_id": LeaseHolderId,
            "fencing_token": FencingToken,
            "expected_revision": Revision,
            "now": datetime,
        },
        {"dispatch_id": DispatchId, "expected_revision": Revision, "now": datetime},
        {
            "dispatch_id": DispatchId,
            "successor_envelope": WorkIntentEnvelope,
            "expected_revision": Revision,
            "now": datetime,
        },
        {
            "dispatch_id": DispatchId,
            "delivery_attempt_id": DeliveryAttemptId,
            "holder_id": LeaseHolderId,
            "fencing_token": FencingToken,
            "expected_revision": Revision,
            "now": datetime,
        },
    )
    for value, (expected_type, expected_fields), expected_hints in zip(
        values, expected, expected_annotations, strict=True
    ):
        assert type(value) is expected_type
        assert is_dataclass(expected_type)
        assert tuple(field.name for field in fields(expected_type)) == expected_fields
        assert get_type_hints(expected_type) == expected_hints
        assert expected_type.__slots__ == expected_fields
        assert not hasattr(value, "__dict__")
        with pytest.raises(FrozenInstanceError):
            value.now = _AWARE_NOW  # type: ignore[misc]

    assert values[0].dispatch_id is dispatch_id
    assert values[0].delivery_attempt_id is attempt_id
    assert values[0].holder_id is holder_id
    assert values[0].fencing_token is token
    assert values[0].expected_revision is revision
    assert values[0].now is _NAIVE_NOW
    assert values[2].successor_envelope is successor


@pytest.mark.parametrize(
    "factory",
    [
        lambda: CheckOwnedWorkIntentControl(
            cast(DispatchId, "dispatch-control"),
            DeliveryAttemptId("attempt-control"),
            LeaseHolderId("holder-control"),
            FencingToken(3),
            Revision(3),
            _AWARE_NOW,
        ),
        lambda: RequestWorkIntentCancellation(
            cast(DispatchId, "dispatch-control"), Revision(3), _AWARE_NOW
        ),
        lambda: SupersedeWorkIntent(
            cast(DispatchId, "dispatch-control"),
            _envelope(DispatchId("successor"), rerun_of=DispatchId("dispatch-control")),
            Revision(3),
            _AWARE_NOW,
        ),
        lambda: AcknowledgeWorkIntentStop(
            cast(DispatchId, "dispatch-control"),
            DeliveryAttemptId("attempt-control"),
            LeaseHolderId("holder-control"),
            FencingToken(3),
            Revision(3),
            _AWARE_NOW,
        ),
    ],
)
def test_control_commands_reject_raw_values(factory: object) -> None:
    with pytest.raises(TypeError):
        factory()  # type: ignore[operator]


def test_supersede_requires_distinct_dispatch_and_matching_rerun() -> None:
    dispatch_id = DispatchId("dispatch-control")
    revision = Revision(3)

    with pytest.raises(ValueError, match="successor"):
        SupersedeWorkIntent(dispatch_id, _envelope(dispatch_id), revision, _AWARE_NOW)

    with pytest.raises(ValueError, match="rerun_of"):
        SupersedeWorkIntent(
            dispatch_id,
            _envelope(DispatchId("successor"), rerun_of=DispatchId("other")),
            revision,
            _AWARE_NOW,
        )


def test_disposition_is_exact_lowercase_str_enum() -> None:
    assert issubclass(WorkIntentControlDisposition, StrEnum)
    assert list(WorkIntentControlDisposition) == [
        WorkIntentControlDisposition.CONTINUE_EXECUTION,
        WorkIntentControlDisposition.STOP_FOR_CANCELLATION,
        WorkIntentControlDisposition.STOP_FOR_SUPERSESSION,
    ]
    assert [item.value for item in WorkIntentControlDisposition] == [
        "continue_execution",
        "stop_for_cancellation",
        "stop_for_supersession",
    ]


def test_control_results_have_exact_frozen_slotted_annotations() -> None:
    expected = {
        OwnedWorkIntentControlCheck: (
            ("snapshot", "disposition"),
            {
                "snapshot": WorkIntentSnapshot,
                "disposition": WorkIntentControlDisposition,
            },
        ),
        WorkIntentSupersessionResult: (
            ("superseded", "successor"),
            {
                "superseded": WorkIntentSnapshot,
                "successor": WorkIntentSnapshot,
            },
        ),
    }
    for result_type, (expected_fields, expected_hints) in expected.items():
        assert is_dataclass(result_type)
        assert tuple(field.name for field in fields(result_type)) == expected_fields
        assert result_type.__slots__ == expected_fields
        assert get_type_hints(result_type) == expected_hints
        assert result_type.__dataclass_params__.frozen is True  # type: ignore[attr-defined]


def test_owned_control_check_enforces_disposition_observable_state() -> None:
    continue_snapshot = _snapshot()
    cancelled_snapshot = _snapshot(cancellation_requested=True)
    superseded_snapshot = _snapshot(
        cancellation_requested=True,
        superseded_by=DispatchId("dispatch-successor"),
    )

    assert (
        OwnedWorkIntentControlCheck(
            continue_snapshot,
            WorkIntentControlDisposition.CONTINUE_EXECUTION,
        ).snapshot
        is continue_snapshot
    )
    assert (
        OwnedWorkIntentControlCheck(
            cancelled_snapshot,
            WorkIntentControlDisposition.STOP_FOR_CANCELLATION,
        ).snapshot
        is cancelled_snapshot
    )
    supersession = OwnedWorkIntentControlCheck(
        superseded_snapshot,
        WorkIntentControlDisposition.STOP_FOR_SUPERSESSION,
    )
    assert supersession.snapshot is superseded_snapshot
    with pytest.raises(FrozenInstanceError):
        supersession.disposition = WorkIntentControlDisposition.CONTINUE_EXECUTION  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del supersession.snapshot  # type: ignore[misc]

    invalid = (
        (cancelled_snapshot, WorkIntentControlDisposition.CONTINUE_EXECUTION),
        (superseded_snapshot, WorkIntentControlDisposition.STOP_FOR_CANCELLATION),
        (
            _snapshot(status=WorkIntentStatus.AVAILABLE),
            WorkIntentControlDisposition.CONTINUE_EXECUTION,
        ),
        (
            _snapshot(status=WorkIntentStatus.SUCCEEDED),
            WorkIntentControlDisposition.STOP_FOR_SUPERSESSION,
        ),
        (
            _snapshot(superseded_by=DispatchId("dispatch-successor")),
            WorkIntentControlDisposition.CONTINUE_EXECUTION,
        ),
    )
    for snapshot, disposition in invalid:
        with pytest.raises(ValueError):
            OwnedWorkIntentControlCheck(snapshot, disposition)


def test_supersession_result_enforces_successor_and_old_snapshot_relations() -> None:
    old = _snapshot(
        superseded_by=DispatchId("dispatch-successor"),
    )
    successor_id = DispatchId("dispatch-successor")
    successor = _snapshot(
        status=WorkIntentStatus.AVAILABLE,
        revision=0,
        lease=None,
        dispatch_id=successor_id,
    )
    successor = replace(
        successor,
        envelope=_envelope(successor_id, rerun_of=old.envelope.dispatch_id),
    )
    result = WorkIntentSupersessionResult(old, successor)
    assert result.superseded is old
    assert result.successor is successor
    with pytest.raises(FrozenInstanceError):
        result.successor = old  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del result.superseded  # type: ignore[misc]

    assert WorkIntentSupersessionResult(
        _snapshot(
            status=WorkIntentStatus.SUPERSEDED,
            superseded_by=successor_id,
            lease=None,
        ),
        successor,
    )

    invalid_successors = (
        replace(successor, status=WorkIntentStatus.LEASED),
        replace(successor, revision=Revision(1)),
        replace(successor, cancellation_requested=True),
        replace(successor, superseded_by=DispatchId("another-successor")),
        replace(
            successor,
            current_lease=WorkIntentLease(
                successor_id,
                DeliveryAttemptId("attempt-successor"),
                LeaseHolderId("holder-successor"),
                FencingToken(1),
                _AWARE_NOW,
            ),
        ),
    )
    for invalid_successor in invalid_successors:
        with pytest.raises(ValueError):
            WorkIntentSupersessionResult(old, invalid_successor)

    with pytest.raises(ValueError):
        WorkIntentSupersessionResult(
            _snapshot(status=WorkIntentStatus.SUCCEEDED, superseded_by=successor_id),
            successor,
        )


class _ControlApplicationDouble:
    def check_owned_work_intent_control(
        self, query: CheckOwnedWorkIntentControl
    ) -> OwnedWorkIntentControlCheck:
        raise NotImplementedError(query)

    def request_work_intent_cancellation(
        self, command: RequestWorkIntentCancellation
    ) -> WorkIntentSnapshot:
        raise NotImplementedError(command)

    def supersede_work_intent(
        self, command: SupersedeWorkIntent
    ) -> WorkIntentSupersessionResult:
        raise NotImplementedError(command)

    def acknowledge_work_intent_stop(
        self, command: AcknowledgeWorkIntentStop
    ) -> WorkIntentSnapshot:
        raise NotImplementedError(command)


def test_control_protocol_is_sync_runtime_checkable_with_exact_methods() -> None:
    assert isinstance(_ControlApplicationDouble(), DurableDispatchControlApplication)
    expected = {
        "check_owned_work_intent_control": (
            ["self", "query"],
            {
                "query": CheckOwnedWorkIntentControl,
                "return": OwnedWorkIntentControlCheck,
            },
        ),
        "request_work_intent_cancellation": (
            ["self", "command"],
            {"command": RequestWorkIntentCancellation, "return": WorkIntentSnapshot},
        ),
        "supersede_work_intent": (
            ["self", "command"],
            {
                "command": SupersedeWorkIntent,
                "return": WorkIntentSupersessionResult,
            },
        ),
        "acknowledge_work_intent_stop": (
            ["self", "command"],
            {"command": AcknowledgeWorkIntentStop, "return": WorkIntentSnapshot},
        ),
    }
    names = {
        name
        for name in DurableDispatchControlApplication.__dict__
        if not name.startswith("_")
    }
    assert names == set(expected)
    for name, (parameters, expected_hints) in expected.items():
        method = getattr(DurableDispatchControlApplication, name)
        assert list(inspect.signature(method).parameters) == parameters
        assert get_type_hints(method) == expected_hints
        assert not inspect.iscoroutinefunction(method)


def test_control_error_is_slotted_catchable_non_frozen_and_safe() -> None:
    dispatch_id = DispatchId("dispatch-control")
    error = DurableDispatchControlError(
        "control_conflict",
        "ownership",
        "Control request is no longer current",
        False,
        dispatch_id,
        DeliveryAttemptId("attempt-control"),
        Revision(3),
        WorkIntentStatus.LEASED,
        "reclaim",
    )
    assert is_dataclass(DurableDispatchControlError)
    assert DurableDispatchControlError.__slots__ == (
        "error_code",
        "category",
        "message",
        "retryability",
        "relevant_dispatch_id",
        "delivery_attempt_id",
        "expected_revision",
        "conflicting_state",
        "recovery_hint",
    )
    assert get_type_hints(DurableDispatchControlError) == {
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
    assert str(error) == error.message
    error.message = "updated"
    assert error.message == "updated"

    with pytest.raises(TypeError):
        DurableDispatchControlError("code", "category", "message", cast(bool, 0), None)
    with pytest.raises(TypeError):
        DurableDispatchControlError(
            "code", "category", "message", False, cast(DispatchId, "raw")
        )
    with pytest.raises(ValueError):
        DurableDispatchControlError(" ", "category", "message", False, None)
