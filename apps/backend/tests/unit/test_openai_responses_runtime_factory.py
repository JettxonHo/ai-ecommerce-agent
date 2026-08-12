"""Tests-first contract for the FL-2 OpenAI runtime composition seam."""

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
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses._runtime import (
    OPENAI_RESPONSES_PROFILE_CATALOG,
    OpenAIResponsesConfigurationError,
    OpenAIResponsesModelRuntime,
    create_openai_responses_runtime,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit


def _request(profile_id: str = "product_intake_v1") -> ModelCallRequest:
    return ModelCallRequest(
        identity=ModelCallIdentity(ModelCallId("live-call-1")),
        instructions="instruction-marker",
        context=StructuredContent.from_mapping({"source": "fixture"}),
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
        execution_profile=ModelExecutionProfile(profile_id, "v1"),
        contract_versions=ModelCallContractVersions(
            "prompt-1", "v1", "skill-1", "domain-1", "context-1"
        ),
    )


def _response_payload() -> dict[str, object]:
    return {
        "id": "response-1",
        "created_at": 0.0,
        "model": "gpt-5.6-terra",
        "object": "response",
        "output": [
            {
                "id": "message-1",
                "content": [
                    {"annotations": [], "text": '{"value":"ok"}', "type": "output_text"}
                ],
                "role": "assistant",
                "status": "completed",
                "type": "message",
            }
        ],
        "parallel_tool_calls": False,
        "tool_choice": "none",
        "tools": [],
        "status": "completed",
        "usage": {
            "input_tokens": 3,
            "input_tokens_details": {"cache_write_tokens": 0, "cached_tokens": 0},
            "output_tokens": 5,
            "output_tokens_details": {"reasoning_tokens": 0},
            "total_tokens": 8,
        },
    }


def test_profile_catalog_is_the_frozen_five_stage_order() -> None:
    assert [
        item.execution_profile.execution_profile_id
        for item in OPENAI_RESPONSES_PROFILE_CATALOG
    ] == [
        "product_intake_v1",
        "customer_insight_v1",
        "product_positioning_v1",
        "marketing_brief_v1",
        "xiaohongshu_mapping_v1",
    ]
    assert [
        item.reasoning_effort.value for item in OPENAI_RESPONSES_PROFILE_CATALOG
    ] == [
        "low",
        "medium",
        "high",
        "medium",
        "low",
    ]
    assert [item.max_output_tokens for item in OPENAI_RESPONSES_PROFILE_CATALOG] == [
        8192,
        12288,
        16384,
        16384,
        12288,
    ]
    assert [item.timeout_seconds for item in OPENAI_RESPONSES_PROFILE_CATALOG] == [
        120,
        180,
        240,
        180,
        120,
    ]


def test_missing_or_wrong_credential_fails_without_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(OpenAIResponsesConfigurationError, match="configuration/access"):
        create_openai_responses_runtime()
    with pytest.raises(ValueError, match="openai_primary"):
        create_openai_responses_runtime(credential_ref="other")


@pytest.mark.parametrize("secret", [None, "", " ", "\t\n"])
def test_factory_rejects_missing_or_whitespace_secret_before_sdk_constructor(
    monkeypatch: pytest.MonkeyPatch, secret: str | None
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    if secret is not None:
        monkeypatch.setenv("OPENAI_API_KEY", secret)
    constructor_called = False

    def forbidden_constructor(*_args: object, **_kwargs: object) -> None:
        nonlocal constructor_called
        constructor_called = True
        raise AssertionError("SDK constructor must not run for a blank Secret")

    monkeypatch.setattr(openai, "OpenAI", forbidden_constructor)
    with pytest.raises(OpenAIResponsesConfigurationError) as caught:
        create_openai_responses_runtime()
    assert str(caught.value) == "OpenAI Responses configuration/access failure"
    assert not constructor_called


def test_factory_constructs_exact_sdk_client_with_sdk_retry_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    runtime = create_openai_responses_runtime()
    assert type(runtime) is OpenAIResponsesModelRuntime
    assert runtime.sdk_max_retries == 0
    runtime.close()


def test_runtime_rejects_unregistered_profile_without_network() -> None:
    # The concrete client is only constructed for the test; profile rejection
    # occurs before the adapter's transport seam is entered.
    import openai

    runtime = OpenAIResponsesModelRuntime(
        client=openai.OpenAI(api_key="test-key", max_retries=0)
    )
    try:
        request = object()
        with pytest.raises(TypeError):
            runtime.execute(request)  # type: ignore[arg-type]
    finally:
        runtime.close()


def test_runtime_executes_exact_profile_parameters_and_retains_safe_metadata() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200,
            headers={"x-request-id": "request-1"},
            json=_response_payload(),
        )

    client = openai.OpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    runtime = OpenAIResponsesModelRuntime(client=client)
    try:
        result = runtime.execute(_request())
        body = json.loads(seen[0].content)
        assert body["reasoning"] == {"effort": "low"}
        assert body["max_output_tokens"] == 8192
        assert body["store"] is False
        assert result.provider_metadata.provider_response_id == "response-1"
        assert len(runtime.metadata_records) == 1
        assert runtime.retry_count == 0
    finally:
        runtime.close()


def test_runtime_unknown_profile_is_a_provider_neutral_invalid_request() -> None:
    client = openai.OpenAI(api_key="test-key", max_retries=0)
    runtime = OpenAIResponsesModelRuntime(client=client)
    try:
        with pytest.raises(ModelRuntimeError) as caught:
            runtime.execute(_request("not_accepted"))
        assert caught.value.category is ModelRuntimeErrorCategory.INVALID_REQUEST
        assert caught.value.model_call_id.value == "live-call-1"
        assert runtime.metadata_records == ()
    finally:
        runtime.close()
