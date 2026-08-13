"""Behavioral tests for the private Qwen Token Plan runtime seam."""

from __future__ import annotations

import json

import httpx
import openai
import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelExecutionProfile,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.application.structured_output import (
    parse_and_validate_structured_output,
)
from ai_ecommerce_agent.platform.model_runtime.qwen_token_plan._runtime import (
    QwenTokenPlanModelRuntime,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit


def _request() -> ModelCallRequest:
    return ModelCallRequest(
        identity=ModelCallIdentity(ModelCallId("qwen-call-1")),
        instructions="Return JSON matching the project schema.",
        context=StructuredContent.from_mapping({"fixture": "qwen"}),
        structured_output=StructuredOutputSpec(
            "fixture_schema",
            "v1",
            StructuredContent.from_mapping(
                {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                }
            ),
        ),
        execution_profile=ModelExecutionProfile("product_intake_v1", "v1"),
        contract_versions=ModelCallContractVersions(
            "prompt-1", "v1", "skill-1", "domain-1", "context-1"
        ),
    )


def _response_payload() -> dict[str, object]:
    return {
        "id": "chatcmpl-qwen-1",
        "created": 1,
        "model": "qwen3.8-max",
        "object": "chat.completion",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": '{"value":"ok"}',
                    "role": "assistant",
                    "refusal": None,
                },
            }
        ],
        "usage": {
            "prompt_tokens": 3,
            "completion_tokens": 5,
            "total_tokens": 8,
        },
    }


def test_runtime_sends_one_non_stream_chat_completion_with_strict_schema() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200, headers={"x-request-id": "req-qwen-1"}, json=_response_payload()
        )

    client = openai.OpenAI(
        api_key="test-key",
        base_url="https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    runtime = QwenTokenPlanModelRuntime(client=client)
    try:
        result = runtime.execute(_request())
        body = json.loads(seen[0].content)
        assert seen[0].url.path.endswith("/chat/completions")
        assert body["model"] == "qwen3.8-max"
        assert body["stream"] is False
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][1]["role"] == "user"
        assert body["response_format"]["type"] == "json_schema"
        assert body["response_format"]["json_schema"]["strict"] is True
        assert result.output_envelope.payload_text == '{"value":"ok"}'
        assert runtime.retry_count == 0
        assert len(runtime.metadata_records) == 1
    finally:
        runtime.close()


def test_project_schema_validation_remains_the_authoritative_next_seam() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=_response_payload())

    client = openai.OpenAI(
        api_key="test-key",
        base_url="https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    runtime = QwenTokenPlanModelRuntime(client=client)
    try:
        result = runtime.execute(_request())
        candidate = parse_and_validate_structured_output(
            result=result,
            spec=_request().structured_output,
        )
        assert candidate.to_mapping() == {"value": "ok"}
    finally:
        runtime.close()
