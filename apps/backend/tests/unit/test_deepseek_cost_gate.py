"""Provider-free DeepSeek P2 cost and call-boundary tests."""

from __future__ import annotations

from dataclasses import replace
from typing import NoReturn

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelCallResult,
    ModelRecoveryKind,
)
from ai_ecommerce_agent.modules.customer_insight.application.skills import (
    customer_insight_analysis,
)
from ai_ecommerce_agent.modules.marketing_brief.application.skills import (
    marketing_brief_generation,
)
from ai_ecommerce_agent.modules.product_intake.application.skills import (
    product_intake_fact_extraction,
)
from ai_ecommerce_agent.modules.product_positioning.application.skills import (
    product_positioning,
)
from ai_ecommerce_agent.modules.xiaohongshu_adapter.application.skills import (
    xiaohongshu_brief_mapping,
)
from ai_ecommerce_agent.orchestration.deterministic_pipeline import (
    DeterministicPipelineCoordinator,
    PipelineInvocation,
    SpecFactory,
    build_scripted_runtime,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._cost_gate import (
    DEEPSEEK_P2_COST_RESERVATION,
    DEEPSEEK_P2_RESERVATION_MICRO_USD,
    DEEPSEEK_P2_STAGE_BUDGETS,
    DEEPSEEK_PRICING_RECORD,
    REQUEST_FRAMING_RESERVE_BYTES,
    TOKEN_PROXY_BYTES_PER_TOKEN,
    DeepSeekCostGateError,
    DeepSeekPricingRecord,
    DeepSeekRuntimeAdmissionGate,
    calculate_peak_cache_miss_reservation,
    canonical_request_body_utf8_bytes,
    conservative_request_input_tokens,
)

pytestmark = pytest.mark.unit

P01_INPUT = """\
sample_id: P01
attempt_id: P2-P01-A1
product: Anker Nano Power Bank
model/designation: A1259
color: Black Stone
variant: 42733233766550
category: A
sanitized public identity note: 界
"""

SPEC_FACTORIES: tuple[SpecFactory, ...] = (
    product_intake_fact_extraction.product_intake_candidate_output_spec,
    customer_insight_analysis.customer_insight_candidate_output_spec,
    product_positioning.product_positioning_candidate_output_spec,
    marketing_brief_generation.marketing_brief_candidate_output_spec,
    xiaohongshu_brief_mapping.xiaohongshu_brief_candidate_output_spec,
)


class _PlanningCaptured(Exception):
    """Stop a coordinator after exposing its five planned requests."""


def _planned_requests() -> tuple[ModelCallRequest, ...]:
    planned: tuple[ModelCallRequest, ...] | None = None

    def capture(requests: tuple[ModelCallRequest, ...]) -> None:
        nonlocal planned
        planned = requests
        raise _PlanningCaptured()

    def never_factory(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> NoReturn:
        raise AssertionError("runtime factory must not run while capturing plans")

    coordinator = DeterministicPipelineCoordinator(
        SPEC_FACTORIES,
        runtime_factory=never_factory,
        input_preflight=lambda _input_text: (),
        pipeline_invocation=PipelineInvocation("P01", "P2-P01-A1", "pilot-p2-v1"),
        runtime_admission_gate=capture,
    )
    with pytest.raises(_PlanningCaptured):
        coordinator.generate(input_text=P01_INPUT)
    assert planned is not None
    return planned


class _RecordingDelegate:
    def __init__(self, requests: tuple[ModelCallRequest, ...]) -> None:
        self._delegate = build_scripted_runtime(requests, ("{}",) * 5)
        self.requests: list[ModelCallRequest] = []

    def execute(self, request: ModelCallRequest) -> ModelCallResult:
        self.requests.append(request)
        return self._delegate.execute(request)


def _gate(
    owner_cap_micro_usd: int | None,
    pricing_record_id: str | None = DEEPSEEK_PRICING_RECORD.record_id,
    pricing_record: DeepSeekPricingRecord = DEEPSEEK_PRICING_RECORD,
) -> tuple[DeepSeekRuntimeAdmissionGate, list[int], list[_RecordingDelegate]]:
    factory_calls: list[int] = []
    delegates: list[_RecordingDelegate] = []

    def factory(
        requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> _RecordingDelegate:
        factory_calls.append(1)
        delegate = _RecordingDelegate(requests)
        delegates.append(delegate)
        return delegate

    return (
        DeepSeekRuntimeAdmissionGate(
            runtime_factory=factory,
            owner_cap_micro_usd=owner_cap_micro_usd,
            pricing_record_id=pricing_record_id,
            pricing_record=pricing_record,
        ),
        factory_calls,
        delegates,
    )


def test_official_peak_cache_miss_reservation_is_exact_integer_micro_usd() -> None:
    reservation = calculate_peak_cache_miss_reservation()

    assert DEEPSEEK_PRICING_RECORD.record_id == "deepseek-v4-pro-2026-08-30-peak-v1"
    assert DEEPSEEK_PRICING_RECORD.source_url == (
        "https://api-docs.deepseek.com/quick_start/pricing/"
    )
    assert reservation.input_token_ceilings == (
        991_808,
        987_712,
        983_616,
        983_616,
        983_616,
    )
    assert reservation.output_token_ceilings == (8_192, 12_288, 16_384, 16_384, 16_384)
    assert reservation.per_stage_micro_usd == (
        1_341_628,
        1_352_441,
        1_363_255,
        1_363_255,
        1_363_255,
    )
    assert reservation.reserved_micro_usd == 6_783_834
    assert reservation == DEEPSEEK_P2_COST_RESERVATION
    assert DEEPSEEK_P2_RESERVATION_MICRO_USD == 6_783_834


def test_exact_owner_cap_authorizes_one_guarded_five_call_attempt() -> None:
    requests = _planned_requests()
    gate, factory_calls, delegates = _gate(DEEPSEEK_P2_RESERVATION_MICRO_USD)

    gate.authorize(requests)
    guarded = gate.runtime_factory(requests, ("{}",) * 5)
    for request in requests:
        guarded.execute(request)

    assert factory_calls == [1]
    assert delegates[0].requests == list(requests)
    assert [budget.model_call_id for budget in DEEPSEEK_P2_STAGE_BUDGETS] == [
        "P2-P01-A1-stage-1",
        "P2-P01-A1-stage-2",
        "P2-P01-A1-stage-3",
        "P2-P01-A1-stage-4",
        "P2-P01-A1-stage-5",
    ]


def test_owner_cap_one_micro_usd_under_reservation_fails_before_factory() -> None:
    gate, factory_calls, _delegates = _gate(DEEPSEEK_P2_RESERVATION_MICRO_USD - 1)

    with pytest.raises(DeepSeekCostGateError, match="underfunded"):
        gate.authorize(_planned_requests())

    assert factory_calls == []


@pytest.mark.parametrize(
    ("owner_cap", "pricing_record_id"),
    (
        (None, DEEPSEEK_PRICING_RECORD.record_id),
        (DEEPSEEK_P2_RESERVATION_MICRO_USD, None),
        (DEEPSEEK_P2_RESERVATION_MICRO_USD, "wrong-pricing-record"),
    ),
)
def test_missing_or_mismatched_owner_pricing_reference_fails_closed(
    owner_cap: int | None,
    pricing_record_id: str | None,
) -> None:
    gate, factory_calls, _delegates = _gate(owner_cap, pricing_record_id)

    with pytest.raises(DeepSeekCostGateError):
        gate.authorize(_planned_requests())

    assert factory_calls == []


def test_runtime_factory_is_not_invoked_before_authorize() -> None:
    requests = _planned_requests()
    gate, factory_calls, _delegates = _gate(DEEPSEEK_P2_RESERVATION_MICRO_USD)

    with pytest.raises(DeepSeekCostGateError, match="not authorized"):
        gate.runtime_factory(requests, ("{}",) * 5)

    assert factory_calls == []


@pytest.mark.parametrize(
    "injected",
    (
        replace(
            DEEPSEEK_PRICING_RECORD,
            record_id="deepseek-v4-pro-tampered",
        ),
        replace(
            DEEPSEEK_PRICING_RECORD,
            context_window_tokens=1,
        ),
        replace(
            DEEPSEEK_PRICING_RECORD,
            input_cache_miss_micro_usd_per_million=1,
        ),
        replace(
            DEEPSEEK_PRICING_RECORD,
            output_micro_usd_per_million=1,
        ),
        replace(
            DEEPSEEK_PRICING_RECORD,
            input_cache_hit_micro_usd_per_million=1,
        ),
    ),
    ids=(
        "record-id",
        "context-window",
        "cache-miss-rate",
        "output-rate",
        "cache-hit-rate",
    ),
)
def test_injected_pricing_record_must_match_frozen_official_record(
    injected: DeepSeekPricingRecord,
) -> None:
    with pytest.raises(ValueError, match="official DeepSeek record"):
        _gate(
            DEEPSEEK_P2_RESERVATION_MICRO_USD,
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
            pricing_record=injected,
        )


def test_out_of_order_recovery_and_sixth_calls_never_reach_delegate() -> None:
    requests = _planned_requests()
    gate, factory_calls, delegates = _gate(DEEPSEEK_P2_RESERVATION_MICRO_USD)
    gate.authorize(requests)
    guarded = gate.runtime_factory(requests, ("{}",) * 5)

    with pytest.raises(DeepSeekCostGateError, match="order"):
        guarded.execute(requests[1])
    assert factory_calls == [1]
    assert delegates[0].requests == []

    gate, factory_calls, delegates = _gate(DEEPSEEK_P2_RESERVATION_MICRO_USD)
    gate.authorize(requests)
    guarded = gate.runtime_factory(requests, ("{}",) * 5)
    recovery = replace(
        requests[0],
        identity=ModelCallIdentity(
            ModelCallId("P2-P01-A1-stage-1-recovery"),
            requests[0].identity.model_call_id,
            ModelRecoveryKind.REGENERATION,
        ),
    )
    with pytest.raises(DeepSeekCostGateError, match="order"):
        guarded.execute(recovery)
    assert delegates[0].requests == []

    gate, factory_calls, delegates = _gate(DEEPSEEK_P2_RESERVATION_MICRO_USD)
    gate.authorize(requests)
    guarded = gate.runtime_factory(requests, ("{}",) * 5)
    for request in requests:
        guarded.execute(request)
    with pytest.raises(DeepSeekCostGateError, match="maximum"):
        guarded.execute(requests[0])
    assert factory_calls == [1]
    assert len(delegates[0].requests) == 5


def test_request_budget_uses_canonical_utf8_bytes_and_versioned_framing() -> None:
    request = _planned_requests()[0]
    budget = DEEPSEEK_P2_STAGE_BUDGETS[0]
    body_bytes = canonical_request_body_utf8_bytes(request, budget.parameters)

    assert b"\xe7\x95\x8c" in body_bytes
    assert len(body_bytes) > len(body_bytes.decode("utf-8"))
    expected = (
        len(body_bytes)
        + REQUEST_FRAMING_RESERVE_BYTES
        + TOKEN_PROXY_BYTES_PER_TOKEN
        - 1
    ) // TOKEN_PROXY_BYTES_PER_TOKEN
    estimated = conservative_request_input_tokens(request, budget.parameters)
    assert estimated == expected
    assert estimated >= len(body_bytes) + REQUEST_FRAMING_RESERVE_BYTES


def test_delegate_failure_is_terminal_and_not_retried() -> None:
    requests = _planned_requests()
    delegate_calls = 0

    class FailingDelegate:
        def execute(self, request: ModelCallRequest) -> ModelCallResult:
            nonlocal delegate_calls
            del request
            delegate_calls += 1
            raise RuntimeError("delegate failure")

    def factory(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> FailingDelegate:
        return FailingDelegate()

    gate = DeepSeekRuntimeAdmissionGate(
        runtime_factory=factory,
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )
    gate.authorize(requests)
    guarded = gate.runtime_factory(requests, ("{}",) * 5)

    with pytest.raises(RuntimeError, match="delegate failure"):
        guarded.execute(requests[0])
    with pytest.raises(DeepSeekCostGateError, match="terminal"):
        guarded.execute(requests[1])
    assert delegate_calls == 1
    assert getattr(guarded, "call_count") == 1  # noqa: B009
