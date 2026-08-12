"""Representative application-seam tests for the deterministic result pipeline."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.application.model_runtime import ModelCallRequest
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
        request.structured_output.output_schema_id for request in recorder.requests
    ] == [
        "product_intake_fact_candidate",
        "customer_insight_candidate",
        "product_positioning_candidate",
        "marketing_brief_candidate",
        "xiaohongshu_brief_candidate",
    ]
    assert recorder.requests[1].context.to_mapping()["upstream_candidate"] is not None


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
