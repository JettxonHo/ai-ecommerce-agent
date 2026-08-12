"""Representative application-seam tests for the deterministic result pipeline."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import replace

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelOutputEnvelope,
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
    build_scripted_runtime,
)

pytestmark = pytest.mark.unit

SUFFICIENT = """
fixture-sufficient-v1 fictional synthetic non-regulated
anchor-city-commuter-backpack CBP-SYN-001 城市通勤双肩包
工作日城市通勤时携带电脑、文件和日常随身物品，约 18 升，可放入 14 英寸级别笔记本电脑。
表面有防泼水处理。source-sufficient-product-v1 product.json direct_source。
"""
SPEC_FACTORIES = (
    product_intake_fact_extraction.product_intake_candidate_output_spec,
    customer_insight_analysis.customer_insight_candidate_output_spec,
    product_positioning.product_positioning_candidate_output_spec,
    marketing_brief_generation.marketing_brief_candidate_output_spec,
    xiaohongshu_brief_mapping.xiaohongshu_brief_candidate_output_spec,
)


class _RecordingRuntime:
    def __init__(
        self, requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ):
        self._delegate = build_scripted_runtime(requests, payloads)
        self.requests: list[ModelCallRequest] = []

    def execute(self, request: ModelCallRequest):
        self.requests.append(request)
        return self._delegate.execute(request)


def test_sufficient_anchor_runs_five_ordered_validated_stages_and_carries_context():
    recorder: _RecordingRuntime | None = None

    def factory(requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]):
        nonlocal recorder
        recorder = _RecordingRuntime(requests, payloads)
        return recorder

    result = DeterministicPipelineCoordinator(SPEC_FACTORIES, factory).generate(
        input_text=SUFFICIENT
    )

    assert result.status == "awaiting_review"
    assert [name for name, _ in result.candidates] == [
        "productIntake",
        "customerInsight",
        "productPositioning",
        "marketingBrief",
        "xiaohongshuBrief",
    ]
    assert recorder is not None
    assert len(recorder.requests) == 5
    assert [
        request.identity.model_call_id.value for request in recorder.requests
    ] == [
        "deterministic-stage-1",
        "deterministic-stage-2",
        "deterministic-stage-3",
        "deterministic-stage-4",
        "deterministic-stage-5",
    ]
    assert [
        request.execution_profile.execution_profile_id
        for request in recorder.requests
    ] == [
        "product_intake_v1",
        "customer_insight_v1",
        "product_positioning_v1",
        "marketing_brief_v1",
        "xiaohongshu_mapping_v1",
    ]
    assert [
        request.structured_output.output_schema_id for request in recorder.requests
    ] == [
        "product_intake_fact_candidate",
        "customer_insight_candidate",
        "product_positioning_candidate",
        "marketing_brief_candidate",
        "xiaohongshu_brief_candidate",
    ]
    assert recorder.requests[1].context.to_mapping()["upstream_candidate"] is not None


def test_each_candidate_stays_grounded_in_supplied_anchor_text() -> None:
    result = DeterministicPipelineCoordinator(SPEC_FACTORIES).generate(
        input_text=SUFFICIENT
    )

    serialized = json.dumps(
        {name: candidate.to_mapping() for name, candidate in result.candidates},
        ensure_ascii=False,
    )
    assert "城市通勤双肩包" in serialized
    assert "约 18 升" in serialized
    assert "可放入 14 英寸级别笔记本电脑" in serialized
    assert "表面有防泼水处理" in serialized
    assert "product.json#product_identity" in serialized
    assert "product.json#attributes[0]" in serialized
    assert "product.json#attributes[1]" in serialized
    assert "product.json#attributes[2]" in serialized
    assert "肩带采用分散受力设计" not in serialized
    assert "独立电脑夹层" not in serialized
    assert "synthetic-comments.csv" not in serialized
    assert "Awareness" not in serialized
    assert "promotion_goal" not in serialized


def test_each_stage_receives_the_validated_predecessor_exactly() -> None:
    class MutatingRuntime:
        def __init__(
            self, requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
        ):
            self._delegate = build_scripted_runtime(requests, payloads)
            self.contexts: list[Mapping[str, object]] = []
            self.calls = 0

        def execute(self, request: ModelCallRequest):
            self.contexts.append(request.context.to_mapping())
            result = self._delegate.execute(request)
            self.calls += 1
            if self.calls != 1:
                return result
            payload = json.loads(result.output_envelope.payload_text)
            payload["fact_candidates"][0]["raw_value"] = "mutation-sensitive-value"
            return replace(
                result,
                output_envelope=ModelOutputEnvelope(
                    json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
                ),
            )

    runtime: MutatingRuntime | None = None

    def factory(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> MutatingRuntime:
        nonlocal runtime
        runtime = MutatingRuntime(requests, payloads)
        return runtime

    result = DeterministicPipelineCoordinator(SPEC_FACTORIES, factory).generate(
        input_text=SUFFICIENT
    )

    assert result.status == "awaiting_review"
    assert runtime is not None
    assert runtime.calls == 5
    assert runtime.contexts[0]["upstream_candidate"] is None
    assert (
        runtime.contexts[1]["upstream_candidate"]["fact_candidates"][0]["raw_value"]
        == "mutation-sensitive-value"
    )
    assert (
        runtime.contexts[2]["upstream_candidate"]
        == result.candidates[1][1].to_mapping()
    )


@pytest.mark.parametrize(
    ("label", "removed_text", "expected_missing"),
    (
        ("capacity", "约 18 升，", "Provide Anchor SKU capacity evidence."),
        (
            "laptop fit",
            "可放入 14 英寸级别笔记本电脑。",
            "Provide Anchor SKU laptop fit evidence.",
        ),
        (
            "weather cover",
            "表面有防泼水处理。",
            "Provide Anchor SKU weather cover evidence.",
        ),
    ),
)
def test_missing_fixed_fact_fails_preflight_without_runtime_calls(
    label: str, removed_text: str, expected_missing: str
) -> None:
    calls = 0

    def factory(requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]):
        nonlocal calls
        calls += 1
        return build_scripted_runtime(requests, payloads)

    result = DeterministicPipelineCoordinator(SPEC_FACTORIES, factory).generate(
        input_text=SUFFICIENT.replace(removed_text, "")
    )

    assert result.status == "insufficient_input", label
    assert expected_missing in result.missing_information
    assert result.candidates == ()
    assert calls == 0


def test_insufficient_preflight_makes_zero_runtime_calls_and_no_candidates():
    calls = 0

    def factory(requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]):
        nonlocal calls
        calls += 1
        return build_scripted_runtime(requests, payloads)

    result = DeterministicPipelineCoordinator(SPEC_FACTORIES, factory).generate(
        input_text="A generic backpack with no accepted Anchor SKU evidence."
    )

    assert result.status == "insufficient_input"
    assert result.missing_information
    assert result.candidates == ()
    assert calls == 0


def test_stage_failure_is_propagated_without_a_partial_pipeline_result():
    class FailingRuntime:
        def __init__(
            self, requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
        ):
            self._delegate = build_scripted_runtime(requests, payloads)
            self.calls = 0

        def execute(self, request: ModelCallRequest):
            self.calls += 1
            if self.calls == 3:
                raise RuntimeError("scripted stage failure")
            return self._delegate.execute(request)

    runtime: FailingRuntime | None = None

    def factory(requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]):
        nonlocal runtime
        runtime = FailingRuntime(requests, payloads)
        return runtime

    with pytest.raises(RuntimeError, match="scripted stage failure"):
        DeterministicPipelineCoordinator(SPEC_FACTORIES, factory).generate(
            input_text=SUFFICIENT
        )
    assert runtime is not None
    assert runtime.calls == 3
