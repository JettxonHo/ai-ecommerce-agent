"""Provider-free P2 composition behavior for the first permitted sample."""

from __future__ import annotations

from typing import NoReturn

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelCallResult,
)
from ai_ecommerce_agent.bootstrap import pilot_p2
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
    DEEPSEEK_P2_RESERVATION_MICRO_USD,
    DEEPSEEK_PRICING_RECORD,
    DeepSeekRuntimeAdmissionGate,
)

pytestmark = pytest.mark.unit

P01_SANITIZED_INPUT = """\
sample_id: P01
attempt_id: P2-P01-A1
product: Anker Nano Power Bank
model/designation: A1259
color: Black Stone
variant: 42733233766550
category: A
sanitized permitted public product identity only
"""

SPEC_FACTORIES: tuple[SpecFactory, ...] = (
    product_intake_fact_extraction.product_intake_candidate_output_spec,
    customer_insight_analysis.customer_insight_candidate_output_spec,
    product_positioning.product_positioning_candidate_output_spec,
    marketing_brief_generation.marketing_brief_candidate_output_spec,
    xiaohongshu_brief_mapping.xiaohongshu_brief_candidate_output_spec,
)


class _FakeDeepSeekRuntime:
    """Interface-shaped fake that records ordered calls without network I/O."""

    def __init__(
        self,
        requests: tuple[ModelCallRequest, ...],
        payloads: tuple[str, ...],
    ) -> None:
        self._delegate = build_scripted_runtime(requests, payloads)
        self.requests: list[ModelCallRequest] = []

    def execute(self, request: ModelCallRequest) -> ModelCallResult:
        self.requests.append(request)
        return self._delegate.execute(request)


def test_p2_p01_non_anchor_input_reaches_five_ordered_deepseek_calls() -> None:
    runtime: _FakeDeepSeekRuntime | None = None

    def runtime_factory(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _FakeDeepSeekRuntime:
        nonlocal runtime
        runtime = _FakeDeepSeekRuntime(requests, payloads)
        return runtime

    cost_gate = DeepSeekRuntimeAdmissionGate(
        runtime_factory=runtime_factory,
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )

    result = DeterministicPipelineCoordinator(
        SPEC_FACTORIES,
        runtime_factory=cost_gate.runtime_factory,
        input_preflight=lambda _input_text: (),
        pipeline_invocation=PipelineInvocation(
            sample_id="P01",
            attempt_id="P2-P01-A1",
            context_assembly_version="pilot-p2-v1",
        ),
        runtime_admission_gate=cost_gate.authorize,
    ).generate(input_text=P01_SANITIZED_INPUT)

    assert result.status == "awaiting_review"
    assert result.missing_information == ()
    assert [name for name, _ in result.candidates] == [
        "productIntake",
        "customerInsight",
        "productPositioning",
        "marketingBrief",
        "xiaohongshuBrief",
    ]
    assert runtime is not None
    assert [request.identity.model_call_id.value for request in runtime.requests] == [
        "P2-P01-A1-stage-1",
        "P2-P01-A1-stage-2",
        "P2-P01-A1-stage-3",
        "P2-P01-A1-stage-4",
        "P2-P01-A1-stage-5",
    ]
    assert [
        request.execution_profile.execution_profile_id for request in runtime.requests
    ] == [
        "product_intake_v1",
        "customer_insight_v1",
        "product_positioning_v1",
        "marketing_brief_v1",
        "xiaohongshu_mapping_v1",
    ]
    assert [
        request.execution_profile.execution_profile_version
        for request in runtime.requests
    ] == ["v1", "v1", "v1", "v1", "v2"]
    assert [
        request.contract_versions.context_assembly_version
        for request in runtime.requests
    ] == ["pilot-p2-v1"] * 5
    assert all(
        P01_SANITIZED_INPUT == request.context.to_mapping()["primary_input"]
        for request in runtime.requests
    )
    assert all(
        request.context.to_mapping()["pipeline_invocation"]
        == {
            "sample_id": "P01",
            "attempt_id": "P2-P01-A1",
            "context_assembly_version": "pilot-p2-v1",
        }
        for request in runtime.requests
    )


def test_p2_bootstrap_is_lazy_and_runs_exact_deepseek_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory_calls = 0
    close_calls = 0
    runtime: _FakeDeepSeekRuntime | None = None

    class _ClosableFakeRuntime(_FakeDeepSeekRuntime):
        def close(self) -> None:
            nonlocal close_calls
            close_calls += 1

    def fake_create(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _ClosableFakeRuntime:
        nonlocal factory_calls, runtime
        factory_calls += 1
        runtime = _ClosableFakeRuntime(requests, payloads)
        return runtime

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", fake_create)
    composition = pilot_p2.compose_pilot_p2_pipeline(
        sample_id="P01",
        attempt_id="P2-P01-A1",
        input_text=P01_SANITIZED_INPUT,
        owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
        pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
    )

    assert factory_calls == 0
    assert close_calls == 0
    result = composition.generate()

    assert result.status == "awaiting_review"
    assert result.missing_information == ()
    assert len(result.candidates) == 5
    assert factory_calls == 1
    assert close_calls == 1
    assert runtime is not None
    assert [request.identity.model_call_id.value for request in runtime.requests] == [
        "P2-P01-A1-stage-1",
        "P2-P01-A1-stage-2",
        "P2-P01-A1-stage-3",
        "P2-P01-A1-stage-4",
        "P2-P01-A1-stage-5",
    ]
    assert [
        request.contract_versions.context_assembly_version
        for request in runtime.requests
    ] == ["pilot-p2-v1"] * 5
    assert all(
        request.context.to_mapping()["pipeline_invocation"]
        == {
            "sample_id": "P01",
            "attempt_id": "P2-P01-A1",
            "context_assembly_version": "pilot-p2-v1",
        }
        for request in runtime.requests
    )


def test_p2_bootstrap_rejects_identity_or_cost_before_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory_calls = 0

    def never_create(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> NoReturn:
        nonlocal factory_calls
        factory_calls += 1
        raise AssertionError("DeepSeek factory must not run after bootstrap rejection")

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", never_create)
    invalid_inputs: tuple[tuple[str, str, str, int, str], ...] = (
        (
            "P02",
            "P2-P01-A1",
            P01_SANITIZED_INPUT,
            DEEPSEEK_P2_RESERVATION_MICRO_USD,
            DEEPSEEK_PRICING_RECORD.record_id,
        ),
        (
            "P01",
            "P2-P02-A1",
            P01_SANITIZED_INPUT,
            DEEPSEEK_P2_RESERVATION_MICRO_USD,
            DEEPSEEK_PRICING_RECORD.record_id,
        ),
        (
            "P01",
            "P2-P01-A1",
            P01_SANITIZED_INPUT,
            DEEPSEEK_P2_RESERVATION_MICRO_USD - 1,
            DEEPSEEK_PRICING_RECORD.record_id,
        ),
    )
    for (
        sample_id,
        attempt_id,
        input_text,
        owner_cap,
        pricing_record_id,
    ) in invalid_inputs:
        with pytest.raises((ValueError, TypeError)):
            pilot_p2.compose_pilot_p2_pipeline(
                sample_id=sample_id,
                attempt_id=attempt_id,
                input_text=input_text,
                owner_cap_micro_usd=owner_cap,
                pricing_record_id=pricing_record_id,
            )

    assert factory_calls == 0


@pytest.mark.parametrize(
    ("label", "wrong_line"),
    (
        ("product", "product: Anker Nano Power Bankx"),
        ("model", "model/designation: A1258"),
        ("color", "color: White"),
        ("variant", "variant: 42733233766551"),
        ("category", "category: B"),
    ),
)
def test_p2_rejects_wrong_frozen_product_identity_before_cost_gate(
    monkeypatch: pytest.MonkeyPatch, label: str, wrong_line: str
) -> None:
    """The P01 content contract is checked before any cost/runtime seam."""

    del label
    factory_calls = 0

    def never_create(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> NoReturn:
        nonlocal factory_calls
        factory_calls += 1
        raise AssertionError("runtime factory must not run for an identity mismatch")

    monkeypatch.setattr(pilot_p2, "_create_deepseek_runtime", never_create)
    input_text = P01_SANITIZED_INPUT
    original_line = next(
        line
        for line in input_text.splitlines()
        if line.split(":", 1)[0] in wrong_line.split(":", 1)[0]
    )
    invalid_input = input_text.replace(original_line, wrong_line)

    with pytest.raises(ValueError, match="P2 input identity"):
        pilot_p2.compose_pilot_p2_pipeline(
            sample_id="P01",
            attempt_id="P2-P01-A1",
            input_text=invalid_input,
            owner_cap_micro_usd=DEEPSEEK_P2_RESERVATION_MICRO_USD,
            pricing_record_id=DEEPSEEK_PRICING_RECORD.record_id,
        )

    assert factory_calls == 0


def test_non_pilot_scripted_coordinator_remains_valid() -> None:
    result = DeterministicPipelineCoordinator(
        SPEC_FACTORIES,
        runtime_factory=build_scripted_runtime,
        input_preflight=lambda _input_text: (),
    ).generate(input_text=P01_SANITIZED_INPUT)

    assert result.status == "awaiting_review"
    assert result.missing_information == ()
    assert len(result.candidates) == 5


def test_default_coordinator_keeps_anchor_preflight_for_non_anchor_p01() -> None:
    result = DeterministicPipelineCoordinator(SPEC_FACTORIES).generate(
        input_text=P01_SANITIZED_INPUT
    )

    assert result.status == "insufficient_input"
    assert result.candidates == ()


class _RuntimeAdmissionRejected(RuntimeError):
    """Safe fake rejection for the provider-admission seam."""


def test_p2_runtime_admission_rejects_before_factory_or_client() -> None:
    events: list[str] = []
    planned_request_counts: list[int] = []
    runtime_factory_calls = 0
    secret_resolution_calls = 0
    client_construction_calls = 0

    def runtime_admission_gate(requests: tuple[ModelCallRequest, ...]) -> None:
        events.append("runtime_admission_gate")
        planned_request_counts.append(len(requests))
        raise _RuntimeAdmissionRejected("P2 runtime admission rejected")

    def runtime_factory(
        _requests: tuple[ModelCallRequest, ...], _payloads: tuple[str, ...]
    ) -> NoReturn:
        nonlocal runtime_factory_calls, secret_resolution_calls
        nonlocal client_construction_calls
        runtime_factory_calls += 1
        secret_resolution_calls += 1
        client_construction_calls += 1
        raise AssertionError("runtime factory must not run after admission rejection")

    coordinator = DeterministicPipelineCoordinator(
        SPEC_FACTORIES,
        runtime_factory=runtime_factory,
        input_preflight=lambda _input_text: (),
        pipeline_invocation=PipelineInvocation(
            sample_id="P01",
            attempt_id="P2-P01-A1",
            context_assembly_version="pilot-p2-v1",
        ),
        runtime_admission_gate=runtime_admission_gate,
    )

    with pytest.raises(_RuntimeAdmissionRejected, match="P2 runtime admission"):
        coordinator.generate(input_text=P01_SANITIZED_INPUT)

    assert events == ["runtime_admission_gate"]
    assert planned_request_counts == [5]
    assert runtime_factory_calls == 0
    assert secret_resolution_calls == 0
    assert client_construction_calls == 0


def test_p2_missing_runtime_admission_fails_closed_before_factory_or_calls() -> None:
    runtime: _FakeDeepSeekRuntime | None = None
    runtime_factory_calls = 0

    def runtime_factory(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> _FakeDeepSeekRuntime:
        nonlocal runtime, runtime_factory_calls
        runtime_factory_calls += 1
        runtime = _FakeDeepSeekRuntime(requests, payloads)
        return runtime

    try:
        result = DeterministicPipelineCoordinator(
            SPEC_FACTORIES,
            runtime_factory=runtime_factory,
            input_preflight=lambda _input_text: (),
            pipeline_invocation=PipelineInvocation(
                sample_id="P01",
                attempt_id="P2-P01-A1",
                context_assembly_version="pilot-p2-v1",
            ),
        ).generate(input_text=P01_SANITIZED_INPUT)
    except Exception:
        completed_without_error = False
    else:
        completed_without_error = result.status == "awaiting_review"

    runtime_calls = 0 if runtime is None else len(runtime.requests)
    assert (completed_without_error, runtime_factory_calls, runtime_calls) == (
        False,
        0,
        0,
    )


def test_p2_composition_preserves_generation_error_when_runtime_close_also_fails() -> (
    None
):
    class _FailingCoordinator:
        def generate(self, *, input_text: str) -> object:
            del input_text
            raise RuntimeError("generation-primary")

    class _FailingRuntime:
        def close(self) -> None:
            raise RuntimeError("close-secondary")

    composition = pilot_p2.PilotP2Composition(
        sample_id="P01",
        attempt_id="P2-P01-A1",
        input_text=P01_SANITIZED_INPUT,
        _coordinator=_FailingCoordinator(),  # type: ignore[arg-type]
        _runtime_holder=[_FailingRuntime()],  # type: ignore[list-item]
    )
    with pytest.raises(RuntimeError, match="generation-primary"):
        composition.generate()
