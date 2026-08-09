"""Exact public facade contract for Durable Dispatch."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.modules.durable_dispatch import public

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = [
    "DispatchId",
    "DeliveryAttemptId",
    "FencingToken",
    "WorkIntentStatus",
    "WorkIntentEnvelope",
    "LeaseHolderId",
    "WorkIntentLease",
]


def test_durable_dispatch_facade_has_exact_ordered_exports() -> None:
    assert public.__all__ == _EXPECTED_PUBLIC
    assert {name for name in public.__dict__ if not name.startswith("_")} == set(
        _EXPECTED_PUBLIC
    )


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
