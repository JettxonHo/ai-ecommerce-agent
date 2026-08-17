"""Offline Phase-A probe for the first DeepSeek Product Intake boundary."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass

import httpx
import openai
import pytest

import ai_ecommerce_agent.platform.model_runtime.deepseek._runtime as _deepseek_runtime
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
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
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._runtime import (
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    DeepSeekModelRuntime,
)

pytestmark = pytest.mark.integration

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


def _unchanged(payload: str) -> str:
    return payload


def _empty(_payload: str) -> str:
    return " "


def _malformed(_payload: str) -> str:
    return "{not-json"


def _empty_object(_payload: str) -> str:
    return "{}"


def _waiting_input(payload: str) -> str:
    candidate = json.loads(payload)
    candidate["workflow_stage_decision"] = "waiting_input"
    return json.dumps(candidate, ensure_ascii=False, separators=(",", ":"))


@dataclass(frozen=True)
class _DiagnosticCase:
    name: str
    finish_reason: str
    content: Callable[[str], str]


@dataclass(frozen=True)
class _SafeSignature:
    provider_id: str
    api_family: str
    configured_model_id: str
    resolved_model_id: str | None
    execution_profile_id: str
    execution_profile_version: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
    provider_attempt_count: int
    runtime_call_count: int
    retry_count: int


@dataclass(frozen=True)
class _Observation:
    safe_signature: _SafeSignature
    actual_category: ModelRuntimeErrorCategory


CASES = (
    _DiagnosticCase("length", "length", _unchanged),
    _DiagnosticCase("empty_content", "stop", _empty),
    _DiagnosticCase("malformed_json", "stop", _malformed),
    _DiagnosticCase("non_success_finish", "content_filter", _unchanged),
    _DiagnosticCase("schema_rejection", "stop", _empty_object),
    _DiagnosticCase("domain_rejection", "stop", _waiting_input),
)


def _signature(
    runtime: DeepSeekModelRuntime, runtime_call_count: int
) -> _SafeSignature:
    metadata_records = runtime.metadata_records
    assert len(metadata_records) == 1
    metadata = metadata_records[0]
    assert metadata.usage is not None
    versions = metadata.version_tuple
    return _SafeSignature(
        provider_id=versions.provider_id,
        api_family=versions.api_family,
        configured_model_id=versions.configured_model_id,
        resolved_model_id=versions.resolved_model_id,
        execution_profile_id=versions.execution_profile_id,
        execution_profile_version=versions.execution_profile_version,
        prompt_tokens=metadata.usage.input_tokens,
        completion_tokens=metadata.usage.output_tokens,
        total_tokens=metadata.usage.total_tokens,
        latency_ms=metadata.latency_ms,
        provider_attempt_count=len(metadata.provider_attempt_ids),
        runtime_call_count=runtime_call_count,
        retry_count=runtime.retry_count,
    )


def _observe_case(
    diagnostic_case: _DiagnosticCase, monkeypatch: pytest.MonkeyPatch
) -> _Observation:
    runtimes: list[DeepSeekModelRuntime] = []
    request_count = 0

    def factory(
        requests: tuple[ModelCallRequest, ...], payloads: tuple[str, ...]
    ) -> DeepSeekModelRuntime:
        assert len(requests) == 5
        assert len(payloads) == 5
        first_request = requests[0]
        assert (
            first_request.execution_profile.execution_profile_id == "product_intake_v1"
        )
        assert first_request.execution_profile.execution_profile_version == "v1"

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal request_count
            request_count += 1
            request_body = json.loads(request.content)
            assert request.url == httpx.URL(f"{DEEPSEEK_BASE_URL}/chat/completions")
            assert request_body["model"] == DEEPSEEK_MODEL
            assert request_body["max_tokens"] == 8192
            assert request_body["response_format"] == {"type": "json_object"}
            assert request_body["thinking"] == {"type": "enabled"}
            assert request_body["reasoning_effort"] == "high"
            return httpx.Response(
                200,
                headers={"x-request-id": "req-offline-diagnosis"},
                json={
                    "id": "chatcmpl-offline-diagnosis",
                    "created": 1,
                    "model": request_body["model"],
                    "object": "chat.completion",
                    "choices": [
                        {
                            "finish_reason": diagnostic_case.finish_reason,
                            "index": 0,
                            "message": {
                                "content": diagnostic_case.content(payloads[0]),
                                "role": "assistant",
                                "refusal": None,
                            },
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 2353,
                        "completion_tokens": 8192,
                        "total_tokens": 10545,
                    },
                },
            )

        client = openai.OpenAI(
            api_key="offline-diagnosis-fixture",
            base_url=DEEPSEEK_BASE_URL,
            max_retries=0,
            http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        )
        runtime = DeepSeekModelRuntime(client=client)
        runtimes.append(runtime)
        return runtime

    clock_values = iter((0.0, 0.0, 0.0, 106.434))
    monkeypatch.setattr(_deepseek_runtime, "_monotonic", lambda: next(clock_values))

    with pytest.raises(ModelRuntimeError) as caught:
        DeterministicPipelineCoordinator(SPEC_FACTORIES, factory).generate(
            input_text=SUFFICIENT
        )

    assert len(runtimes) == 1
    runtime = runtimes[0]
    try:
        return _Observation(
            safe_signature=_signature(runtime, request_count),
            actual_category=caught.value.category,
        )
    finally:
        runtime.close()


def test_historical_safe_signature_is_observationally_ambiguous(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observations = tuple(_observe_case(case, monkeypatch) for case in CASES)

    assert len({observation.safe_signature for observation in observations}) == 1
    assert len({observation.actual_category for observation in observations}) >= 2
