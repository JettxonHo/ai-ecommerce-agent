"""Exact public facade contract for Durable Dispatch."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.modules.durable_dispatch import public
from ai_ecommerce_agent.modules.durable_dispatch.application.completion_commands import (  # noqa: E501
    CompleteOwnedWorkIntent,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.completion_protocols import (  # noqa: E501
    DurableDispatchCommitFenceParticipant,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.completion_results import (
    WorkIntentCompletionResult,
)
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
    WorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.status import WorkIntentStatus

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = [
    "DispatchId",
    "DeliveryAttemptId",
    "FencingToken",
    "WorkIntentStatus",
    "WorkIntentEnvelope",
    "LeaseHolderId",
    "WorkIntentLease",
    "WorkIntentSnapshot",
    "ClaimNextWorkIntent",
    "HeartbeatWorkIntentLease",
    "DurableDispatchLeaseApplication",
    "DurableDispatchLeaseError",
    "CheckOwnedWorkIntentControl",
    "RequestWorkIntentCancellation",
    "SupersedeWorkIntent",
    "AcknowledgeWorkIntentStop",
    "WorkIntentControlDisposition",
    "OwnedWorkIntentControlCheck",
    "WorkIntentSupersessionResult",
    "DurableDispatchControlApplication",
    "DurableDispatchControlError",
    "CompleteOwnedWorkIntent",
    "WorkIntentCompletionResult",
    "DurableDispatchCommitFenceParticipant",
]

_EXPECTED_OBJECTS = {
    "DispatchId": DispatchId,
    "DeliveryAttemptId": DeliveryAttemptId,
    "FencingToken": FencingToken,
    "WorkIntentStatus": WorkIntentStatus,
    "WorkIntentEnvelope": WorkIntentEnvelope,
    "LeaseHolderId": LeaseHolderId,
    "WorkIntentLease": WorkIntentLease,
    "WorkIntentSnapshot": WorkIntentSnapshot,
    "ClaimNextWorkIntent": ClaimNextWorkIntent,
    "HeartbeatWorkIntentLease": HeartbeatWorkIntentLease,
    "DurableDispatchLeaseApplication": DurableDispatchLeaseApplication,
    "DurableDispatchLeaseError": DurableDispatchLeaseError,
    "CheckOwnedWorkIntentControl": CheckOwnedWorkIntentControl,
    "RequestWorkIntentCancellation": RequestWorkIntentCancellation,
    "SupersedeWorkIntent": SupersedeWorkIntent,
    "AcknowledgeWorkIntentStop": AcknowledgeWorkIntentStop,
    "WorkIntentControlDisposition": WorkIntentControlDisposition,
    "OwnedWorkIntentControlCheck": OwnedWorkIntentControlCheck,
    "WorkIntentSupersessionResult": WorkIntentSupersessionResult,
    "DurableDispatchControlApplication": DurableDispatchControlApplication,
    "DurableDispatchControlError": DurableDispatchControlError,
    "CompleteOwnedWorkIntent": CompleteOwnedWorkIntent,
    "WorkIntentCompletionResult": WorkIntentCompletionResult,
    "DurableDispatchCommitFenceParticipant": DurableDispatchCommitFenceParticipant,
}


def test_durable_dispatch_facade_has_exact_ordered_exports() -> None:
    assert public.__all__ == _EXPECTED_PUBLIC
    assert {name for name in public.__dict__ if not name.startswith("_")} == set(
        _EXPECTED_PUBLIC
    )
    assert [getattr(public, name) for name in _EXPECTED_PUBLIC] == [
        _EXPECTED_OBJECTS[name] for name in _EXPECTED_PUBLIC
    ]


def test_durable_dispatch_facade_exposes_no_technical_types() -> None:
    for private_name in (
        "WorkIntent",
        "Repository",
        "UnitOfWork",
        "Session",
        "Engine",
        "Worker",
        "Lease",
        "Payload",
        "SQLAlchemy",
        "FastAPI",
        "StateGraph",
    ):
        assert not hasattr(public, private_name)
