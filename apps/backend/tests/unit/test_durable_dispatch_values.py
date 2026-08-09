"""Unit contracts for Durable Dispatch identity and lifecycle values."""

from __future__ import annotations

from typing import Any, cast

import pytest

from ai_ecommerce_agent.modules.durable_dispatch.public import (
    DeliveryAttemptId,
    DispatchId,
    FencingToken,
    WorkIntentStatus,
)

pytestmark = pytest.mark.unit


class _StringSubclass(str):
    """Adversarial str subclass that must not cross the value boundary."""

    def strip(self, chars: str | None = None) -> str:
        raise AssertionError("str subclass methods must not be invoked")


class _IntegerSubclass(int):
    """Adversarial int subclass that must not cross the value boundary."""


def test_dispatch_and_delivery_attempt_identities_are_distinct_and_opaque() -> None:
    dispatch_id = DispatchId("dispatch-01")
    same_dispatch_id = DispatchId("dispatch-01")
    attempt_id = DeliveryAttemptId("dispatch-01")

    assert dispatch_id == same_dispatch_id
    assert dispatch_id != attempt_id
    assert str(dispatch_id) == "dispatch-01"
    assert dispatch_id.value == "dispatch-01"
    assert DispatchId.new() != DispatchId.new()
    assert DeliveryAttemptId.new() != DeliveryAttemptId.new()


def test_identity_values_reject_empty_values_without_coercing_valid_strings() -> None:
    assert DispatchId(" dispatch-01 ").value == " dispatch-01 "

    for identity_type in (DispatchId, DeliveryAttemptId):
        with pytest.raises(ValueError):
            identity_type("")
        with pytest.raises(ValueError):
            identity_type("   ")
        with pytest.raises(TypeError):
            identity_type(cast(Any, 1))
        with pytest.raises(TypeError):
            identity_type(cast(Any, _StringSubclass("dispatch-01")))


def test_fencing_token_is_ordered_non_negative_and_monotonic() -> None:
    initial = FencingToken.initial()

    assert initial.value == 0
    assert initial.next() == FencingToken(1)
    assert initial.next() > initial
    assert FencingToken(2) > FencingToken(1)

    with pytest.raises(ValueError):
        FencingToken(-1)
    with pytest.raises(TypeError):
        FencingToken(cast(Any, True))
    with pytest.raises(TypeError):
        FencingToken(cast(Any, 1.0))
    with pytest.raises(TypeError):
        FencingToken(cast(Any, _IntegerSubclass(0)))


def test_work_intent_status_catalog_is_exact_and_alias_free() -> None:
    assert [status.value for status in WorkIntentStatus] == [
        "pending",
        "available",
        "leased",
        "in_progress",
        "succeeded",
        "failed_retryable",
        "failed_terminal",
        "cancelled",
        "superseded",
    ]
    assert len(WorkIntentStatus.__members__) == len(WorkIntentStatus)
