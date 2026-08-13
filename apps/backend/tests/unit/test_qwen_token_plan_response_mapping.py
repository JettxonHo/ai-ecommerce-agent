"""Behavioral tests for safe Qwen Token Plan response mapping."""

from __future__ import annotations

import pytest
from openai.types.chat import ChatCompletion

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelCallResult,
    ModelExecutionProfile,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    ModelTokenUsage,
    ProviderAttemptId,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.qwen_token_plan import _response_mapping
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit


def _request() -> ModelCallRequest:
    return ModelCallRequest(
        identity=ModelCallIdentity(ModelCallId("qwen-call-1")),
        instructions="Return JSON.",
        context=StructuredContent.from_mapping({"fixture": True}),
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


def _response(
    *,
    content: str | None = '{"value":"ok"}',
    finish_reason: str = "stop",
    choices: list[dict[str, object]] | None = None,
    response_id: str = "chatcmpl-qwen-1",
    model: str = "qwen3.8-max",
    usage: dict[str, object] | None = None,
) -> ChatCompletion:
    payload: dict[str, object] = {
        "id": response_id,
        "created": 1,
        "model": model,
        "object": "chat.completion",
        "choices": choices
        or [
            {
                "finish_reason": finish_reason,
                "index": 0,
                "message": {
                    "content": content,
                    "role": "assistant",
                    "refusal": None,
                },
            }
        ],
        "usage": usage
        or {
            "prompt_tokens": 3,
            "completion_tokens": 5,
            "total_tokens": 8,
        },
    }
    response = ChatCompletion.model_validate(payload)
    response._request_id = "req-qwen-1"  # type: ignore[attr-defined]
    return response


def _map(response: ChatCompletion) -> ModelCallResult:
    return _response_mapping.map_qwen_token_plan_response(
        request=_request(),
        response=response,
        provider_attempt_ids=(ProviderAttemptId("qwen-call-1-attempt-1"),),
        latency_ms=17,
    )


def test_completed_json_maps_provider_neutral_result_and_usage() -> None:
    result = _map(_response())
    assert result.output_envelope.payload_text == '{"value":"ok"}'  # type: ignore[attr-defined]
    metadata = result.provider_metadata  # type: ignore[attr-defined]
    assert metadata.version_tuple.provider_id == "qwen_token_plan"
    assert metadata.version_tuple.api_family == "chat_completions"
    assert metadata.version_tuple.configured_model_id == "qwen3.8-max"
    assert metadata.version_tuple.resolved_model_id == "qwen3.8-max"
    assert metadata.usage == ModelTokenUsage(3, 5, 8)
    assert metadata.provider_response_id == "chatcmpl-qwen-1"
    assert metadata.provider_request_id == "req-qwen-1"


@pytest.mark.parametrize(
    ("response", "category"),
    [
        (
            _response(content=" "),
            ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT,
        ),
        (
            _response(content="not-json"),
            ModelRuntimeErrorCategory.INVALID_CANDIDATE,
        ),
        (
            _response(content="[]"),
            ModelRuntimeErrorCategory.INVALID_CANDIDATE,
        ),
        (
            _response(finish_reason="length"),
            ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT,
        ),
        (
            _response(
                choices=[
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {
                            "content": '{"value":"one"}',
                            "role": "assistant",
                            "refusal": None,
                        },
                    },
                    {
                        "finish_reason": "stop",
                        "index": 1,
                        "message": {
                            "content": '{"value":"two"}',
                            "role": "assistant",
                            "refusal": None,
                        },
                    },
                ]
            ),
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
        ),
        (
            _response(
                choices=[
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {
                            "content": None,
                            "role": "assistant",
                            "refusal": "refusal-marker",
                        },
                    }
                ]
            ),
            ModelRuntimeErrorCategory.REFUSAL,
        ),
    ],
)
def test_malformed_or_non_success_responses_are_safe_typed_errors(
    response: ChatCompletion,
    category: ModelRuntimeErrorCategory,
) -> None:
    with pytest.raises(ModelRuntimeError) as caught:
        _map(response)
    assert caught.value.category is category
    assert "refusal-marker" not in caught.value.message
    assert "not-json" not in caught.value.message
