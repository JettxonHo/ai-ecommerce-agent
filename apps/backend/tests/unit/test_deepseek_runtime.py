"""Behavioral tests for the private DeepSeek runtime execution seam."""

from __future__ import annotations

import json

import httpx
import openai
import pytest

import ai_ecommerce_agent.platform.model_runtime as _runtime_package
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelExecutionProfile,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._runtime import (
    DEEPSEEK_BASE_URL,
    DeepSeekModelRuntime,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

_runtime_package.__dict__.pop("deepseek", None)

pytestmark = pytest.mark.unit


def _request() -> ModelCallRequest:
    return ModelCallRequest(
        identity=ModelCallIdentity(ModelCallId("deepseek-call-1")),
        instructions="Return JSON matching the project schema.",
        context=StructuredContent.from_mapping({"fixture": "deepseek"}),
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
        "id": "chatcmpl-deepseek-1",
        "created": 1,
        "model": "deepseek-v4-pro",
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


def test_runtime_sends_one_nonstream_chat_completion_json_mode() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200, headers={"x-request-id": "req-deepseek-1"}, json=_response_payload()
        )

    client = openai.OpenAI(
        api_key="test-key",
        base_url=DEEPSEEK_BASE_URL,
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    runtime = DeepSeekModelRuntime(client=client)
    try:
        result = runtime.execute(_request())
        body = json.loads(seen[0].content)
        assert seen[0].url.path.endswith("/chat/completions")
        assert body["model"] == "deepseek-v4-pro"
        assert body["stream"] is False
        assert body["response_format"] == {"type": "json_object"}
        # The SDK merges ``extra_body`` into the wire JSON body.
        assert body["thinking"] == {"type": "enabled"}
        assert body["reasoning_effort"] == "high"
        assert body["max_tokens"] == 8192
        assert "json_schema" not in json.dumps(body)
        assert "strict" not in json.dumps(body)
        assert result.output_envelope.payload_text == '{"value":"ok"}'
        assert runtime.retry_count == 0
        assert len(runtime.metadata_records) == 1
    finally:
        runtime.close()


def test_transient_provider_error_is_one_attempt_without_runtime_retry() -> None:
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503, json={"error": "provider marker must not escape"})

    client = openai.OpenAI(
        api_key="test-key",
        base_url=DEEPSEEK_BASE_URL,
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    runtime = DeepSeekModelRuntime(client=client)
    try:
        with pytest.raises(ModelRuntimeError) as caught:
            runtime.execute(_request())
        assert (
            caught.value.category
            is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
        )
        assert caught.value.retryability is True
        assert calls == 1
        assert runtime.retry_count == 0
        assert "provider marker" not in str(caught.value)
    finally:
        runtime.close()


@pytest.mark.parametrize(
    ("status_code", "category"),
    [
        (401, ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS),
        (422, ModelRuntimeErrorCategory.INVALID_REQUEST),
        (503, ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE),
    ],
)
def test_provider_statuses_map_to_safe_categories(
    status_code: int,
    category: ModelRuntimeErrorCategory,
) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "raw-provider-marker"})

    client = openai.OpenAI(
        api_key="test-key",
        base_url=DEEPSEEK_BASE_URL,
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    runtime = DeepSeekModelRuntime(client=client)
    try:
        with pytest.raises(ModelRuntimeError) as caught:
            runtime.execute(_request())
        assert caught.value.category is category
        assert "raw-provider-marker" not in str(caught.value)
    finally:
        runtime.close()
