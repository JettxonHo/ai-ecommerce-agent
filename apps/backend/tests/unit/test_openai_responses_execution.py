"""Offline behavioral coverage for one injected Responses transport attempt."""

from __future__ import annotations

import json
from typing import Any, cast

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
    ProviderAttemptId,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _execution,
    _response_mapping,
    request_preparation,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit

_PROFILE = ModelExecutionProfile("profile-1", "v1")
_CALL_ID = ModelCallId("call-1")
_ATTEMPTS = (ProviderAttemptId("attempt-1"), ProviderAttemptId("attempt-2"))


class _RequestSubclass(ModelCallRequest):
    pass


class _ParametersSubclass(request_preparation.OpenAIResponsesCallParameters):
    pass


class _AttemptSubclass(ProviderAttemptId):
    pass


class _ClientSubclass(openai.OpenAI):
    pass


def _request() -> ModelCallRequest:
    return ModelCallRequest(
        ModelCallIdentity(_CALL_ID),
        "instruction-marker",
        StructuredContent.from_mapping({"context": ["value"]}),
        StructuredOutputSpec(
            "schema-1",
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
        _PROFILE,
        ModelCallContractVersions("prompt-1", "v1", "skill-1", "domain-1", "context-1"),
    )


def _parameters() -> request_preparation.OpenAIResponsesCallParameters:
    return request_preparation.OpenAIResponsesCallParameters(
        _PROFILE, request_preparation.OpenAIReasoningEffort.LOW, 32, 19
    )


def _response_payload(text: str = "mapped output") -> dict[str, object]:
    return {
        "id": "response-id",
        "created_at": 0.0,
        "model": "gpt-5.6-terra",
        "object": "response",
        "output": [
            {
                "id": "message-1",
                "content": [{"annotations": [], "text": text, "type": "output_text"}],
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
            "input_tokens_details": {"cache_write_tokens": 0, "cached_tokens": 1},
            "output_tokens": 5,
            "output_tokens_details": {"reasoning_tokens": 2},
            "total_tokens": 8,
        },
    }


def _client(handler: Any, *, max_retries: int = 0) -> openai.OpenAI:
    return openai.OpenAI(
        api_key="test-key",
        max_retries=max_retries,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def _success(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200, headers={"x-request-id": "request-id"}, json=_response_payload()
    )


def _execute(client: openai.OpenAI, *, request: object = _CALL_ID) -> object:
    actual_request = (
        _request() if request is _CALL_ID else cast(ModelCallRequest, request)
    )
    return _execution.execute_openai_responses_attempt(
        client=client,
        request=actual_request,
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
    )


def test_real_sdk_success_uses_exact_body_timeout_once_and_preserves_client() -> None:
    seen: list[tuple[dict[str, object], httpx.Request]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(({}, request))
        return httpx.Response(
            200,
            headers={"x-request-id": "request-id"},
            json=_response_payload(),
        )

    client = _client(handler)
    retries_before = client.max_retries
    result = cast(Any, _execute(client))
    assert len(seen) == 1
    request_body = json.loads(seen[0][1].content)
    assert request_body["model"] == "gpt-5.6-terra"
    assert request_body["instructions"] == "instruction-marker"
    assert request_body["max_output_tokens"] == 32
    assert request_body["store"] is False
    timeout = seen[0][1].extensions["timeout"]
    assert timeout == {"connect": 19, "read": 19, "write": 19, "pool": 19}
    assert result.output_envelope.payload_text == "mapped output"
    assert result.provider_metadata.provider_request_id == "request-id"
    assert client.max_retries == retries_before == 0
    assert not client.is_closed()
    client.close()


def test_prepare_precedes_io_and_mapper_receives_exact_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    original_prepare = request_preparation.prepare_openai_responses_call
    original_map = _response_mapping.map_openai_responses_response

    def prepare(
        *,
        request: ModelCallRequest,
        parameters: request_preparation.OpenAIResponsesCallParameters,
    ) -> object:
        events.append("prepare")
        return original_prepare(request=request, parameters=parameters)

    def map_response(**kwargs: object) -> object:
        events.append("map")
        return original_map(**kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(_execution, "prepare_openai_responses_call", prepare)
    monkeypatch.setattr(_execution, "map_openai_responses_response", map_response)

    def handler(request: httpx.Request) -> httpx.Response:
        events.append("io")
        return httpx.Response(
            200, headers={"x-request-id": "request-id"}, json=_response_payload()
        )

    client = _client(handler)
    _execute(client)
    client.close()
    assert events == ["prepare", "io", "map"]


def test_existing_preparation_and_mapper_errors_propagate_by_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prepare_marker = ModelRuntimeError(
        ModelRuntimeErrorCategory.INVALID_REQUEST,
        "prepare marker",
        False,
        _CALL_ID,
    )

    def fail_prepare(*, request: ModelCallRequest, parameters: object) -> object:
        raise prepare_marker

    monkeypatch.setattr(_execution, "prepare_openai_responses_call", fail_prepare)
    client = _client(_success)
    with pytest.raises(ModelRuntimeError) as caught:
        _execute(client)
    assert caught.value is prepare_marker
    client.close()

    map_marker = ModelRuntimeError(
        ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
        "map marker",
        True,
        _CALL_ID,
    )

    def fail_map(**kwargs: object) -> object:
        raise map_marker

    monkeypatch.setattr(
        _execution,
        "prepare_openai_responses_call",
        request_preparation.prepare_openai_responses_call,
    )
    monkeypatch.setattr(_execution, "map_openai_responses_response", fail_map)
    client = _client(_success)
    with pytest.raises(ModelRuntimeError) as caught:
        _execute(client)
    assert caught.value is map_marker
    client.close()


@pytest.mark.parametrize(
    "candidate", [None, object(), _RequestSubclass.__new__(_RequestSubclass)]
)
def test_invalid_request_makes_zero_requests(candidate: object) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200, headers={"x-request-id": "request-id"}, json=_response_payload()
        )

    client = _client(handler)
    with pytest.raises((TypeError, ValueError)):
        _execute(client, request=candidate)
    assert calls == 0
    client.close()


def test_invalid_parameters_attempt_tuple_client_or_retries_make_zero_requests() -> (
    None
):
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=_response_payload())

    client = _client(handler)
    for parameters, attempts, candidate_client in (
        (None, _ATTEMPTS, client),
        (
            _ParametersSubclass(
                _PROFILE, request_preparation.OpenAIReasoningEffort.LOW, 32, 19
            ),
            _ATTEMPTS,
            client,
        ),
        (_parameters(), (), client),
        (_parameters(), (_AttemptSubclass("bad"),), client),
        (_parameters(), _ATTEMPTS, _ClientSubclass(api_key="test-key", max_retries=0)),
    ):
        with pytest.raises((TypeError, ValueError)):
            _execution.execute_openai_responses_attempt(
                client=candidate_client,
                request=_request(),
                parameters=cast(Any, parameters),
                provider_attempt_ids=attempts,
            )
    client.close()
    assert calls == 0

    retry_client = _client(_success, max_retries=1)
    with pytest.raises(ModelRuntimeError) as caught:
        _execute(retry_client)
    assert caught.value.category is ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS
    assert caught.value.retryability is False
    assert caught.value.provider_metadata is None
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    retry_client.close()


@pytest.mark.parametrize(
    ("status", "category", "retryability", "message"),
    [
        (
            400,
            ModelRuntimeErrorCategory.INVALID_REQUEST,
            False,
            "OpenAI Responses request was invalid",
        ),
        (
            401,
            ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS,
            False,
            "OpenAI Responses configuration/access failure",
        ),
        (
            403,
            ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS,
            False,
            "OpenAI Responses configuration/access failure",
        ),
        (
            404,
            ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS,
            False,
            "OpenAI Responses configuration/access failure",
        ),
        (
            408,
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            "OpenAI Responses provider transport failed",
        ),
        (
            409,
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            "OpenAI Responses provider transport failed",
        ),
        (
            422,
            ModelRuntimeErrorCategory.INVALID_REQUEST,
            False,
            "OpenAI Responses request was invalid",
        ),
        (
            429,
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            "OpenAI Responses provider transport failed",
        ),
        (
            500,
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            "OpenAI Responses provider transport failed",
        ),
    ],
)
def test_status_errors_are_provider_neutral_and_metadata_safe(
    status: int,
    category: ModelRuntimeErrorCategory,
    retryability: bool,
    message: str,
) -> None:
    secret = "secret-response-body"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status,
            headers={"x-request-id": "error-request-id"},
            json={"error": {"message": secret, "type": "invalid_request_error"}},
        )

    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execute(client)
    error = caught.value
    assert error.category is category
    assert error.retryability is retryability
    assert error.message == message
    assert secret not in error.message
    assert error.model_call_id is _CALL_ID
    assert error.provider_metadata is not None
    assert error.provider_metadata.provider_request_id == "error-request-id"
    assert error.provider_metadata.provider_attempt_ids is _ATTEMPTS
    assert error.provider_metadata.latency_ms >= 0
    assert error.__cause__ is None
    assert error.__context__ is None
    client.close()


@pytest.mark.parametrize("exception_kind", ["timeout", "connection", "malformed"])
def test_transport_and_malformed_sdk_failures_map_to_transient(
    exception_kind: str,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if exception_kind == "timeout":
            raise httpx.ReadTimeout("provider timeout", request=request)
        if exception_kind == "connection":
            raise httpx.ConnectError("provider connection", request=request)
        return httpx.Response(200, json={"id": "broken"})

    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execute(client)
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.retryability is True
    expected_message = (
        "OpenAI Responses provider response was transient"
        if exception_kind == "malformed"
        else "OpenAI Responses provider transport failed"
    )
    assert caught.value.message == expected_message
    if exception_kind == "malformed":
        assert caught.value.provider_metadata is None
    else:
        assert caught.value.provider_metadata is not None
    assert caught.value.__cause__ is None
    assert caught.value.__context__ is None
    client.close()


def test_non_openai_exception_propagates_by_identity() -> None:
    marker = RuntimeError("marker")

    client = _client(_success)

    def raise_marker(**kwargs: object) -> object:
        raise marker

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(cast(Any, client.responses), "create", raise_marker)
    with pytest.raises(RuntimeError) as caught:
        _execute(client)
    assert caught.value is marker
    monkeypatch.undo()
    client.close()


def test_monotonic_latency_wraps_only_sdk_call(monkeypatch: pytest.MonkeyPatch) -> None:
    ticks = iter((10.0, 10.125))
    monkeypatch.setattr(_execution, "monotonic", lambda: next(ticks))
    client = _client(_success)
    result = cast(Any, _execute(client))
    assert result.provider_metadata.latency_ms == 125
    client.close()
