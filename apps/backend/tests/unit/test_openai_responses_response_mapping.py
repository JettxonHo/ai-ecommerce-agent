"""Behavioral tests for typed OpenAI Responses outcome mapping."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest
from openai.types.responses import Response

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelExecutionProfile,
    ModelOutputEnvelope,
    ModelRecoveryKind,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    ModelRuntimeVersionTuple,
    ModelTokenUsage,
    ProviderAttemptId,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import _response_mapping
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit


_PROFILE = ModelExecutionProfile("profile-1", "v1")
_CALL_ID = ModelCallId("call-1")
_ATTEMPTS = (ProviderAttemptId("attempt-1"), ProviderAttemptId("attempt-2"))
_MISSING = object()


class _RequestSubclass(ModelCallRequest):
    pass


class _ResponseSubclass(Response):
    pass


class _TupleSubclass(tuple[ProviderAttemptId, ...]):
    pass


class _IntSubclass(int):
    pass


class _TextSubclass(str):
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
                {"type": "object", "properties": {"value": {"type": "string"}}}
            ),
        ),
        _PROFILE,
        ModelCallContractVersions("prompt-1", "v1", "skill-1", "domain-1", "context-1"),
    )


def _response(
    output: list[dict[str, object]],
    *,
    status: str | None = "completed",
    usage: dict[str, object] | None = None,
    response_id: str = "response-id",
    model: str = "gpt-5.6-terra",
    request_id: str = "request-id",
) -> Response:
    payload: dict[str, object] = {
        "id": response_id,
        "created_at": 0.0,
        "model": model,
        "object": "response",
        "output": output,
        "parallel_tool_calls": False,
        "tool_choice": "none",
        "tools": [],
        "status": status,
    }
    payload["usage"] = usage or {
        "input_tokens": 3,
        "input_tokens_details": {"cache_write_tokens": 0, "cached_tokens": 1},
        "output_tokens": 5,
        "output_tokens_details": {"reasoning_tokens": 2},
        "total_tokens": 8,
    }
    response = Response.model_validate(payload)
    response._request_id = request_id  # type: ignore[attr-defined]
    return response


def _message(
    *content: dict[str, object], message_id: str = "message-1"
) -> dict[str, object]:
    return {
        "id": message_id,
        "content": list(content),
        "role": "assistant",
        "status": "completed",
        "type": "message",
    }


def _text(value: str, *, annotation: list[object] | None = None) -> dict[str, object]:
    return {
        "annotations": annotation or [],
        "text": value,
        "type": "output_text",
    }


def _refusal(value: str) -> dict[str, object]:
    return {"refusal": value, "type": "refusal"}


def _reasoning() -> dict[str, object]:
    return {"id": "reasoning-1", "summary": [], "type": "reasoning"}


def _tool_call() -> dict[str, object]:
    return {
        "arguments": "{}",
        "call_id": "tool-call-1",
        "name": "lookup",
        "type": "function_call",
    }


def _map(
    response: Response | object,
    *,
    request: ModelCallRequest | object = _MISSING,
    attempts: tuple[ProviderAttemptId, ...] | object = _ATTEMPTS,
    latency_ms: int | object = 17,
) -> object:
    return _response_mapping.map_openai_responses_response(
        request=cast(ModelCallRequest, _request() if request is _MISSING else request),
        response=cast(Response, response),
        provider_attempt_ids=cast(tuple[ProviderAttemptId, ...], attempts),
        latency_ms=cast(int, latency_ms),
    )


def test_completed_text_maps_exact_metadata_and_preserves_attempt_identity() -> None:
    response = _response(
        [_reasoning(), _message(_text("hello ")), _message(_text("world"))]
    )
    result = cast(Any, _map(response))
    assert result.output_envelope is not None
    assert result.output_envelope.payload_text == "hello world"
    metadata = result.provider_metadata
    assert metadata.model_call_id is _CALL_ID
    assert metadata.provider_attempt_ids is _ATTEMPTS
    assert metadata.provider_attempt_ids == _ATTEMPTS
    assert metadata.provider_response_id == "response-id"
    assert metadata.provider_request_id == "request-id"
    assert metadata.version_tuple.provider_id == "openai"
    assert metadata.version_tuple.api_family == "responses"
    assert metadata.version_tuple.configured_model_id == "gpt-5.6-terra"
    assert metadata.version_tuple.resolved_model_id == "gpt-5.6-terra"
    assert metadata.version_tuple == ModelRuntimeVersionTuple(
        "openai",
        "responses",
        "2.53.0",
        "gpt-5.6-terra",
        "gpt-5.6-terra",
        "prompt-1",
        "v1",
        "schema-1",
        "v1",
        "skill-1",
        "domain-1",
        "profile-1",
        "v1",
        "context-1",
    )
    assert metadata.usage == ModelTokenUsage(3, 5, 8)
    assert metadata.latency_ms == 17


def test_response_and_request_are_not_mutated() -> None:
    response = _response([_message(_text("immutable"))])
    before = response.model_dump()
    request = _request()
    context_before = request.context.to_mapping()
    schema_before = request.structured_output.schema.to_mapping()
    _map(response, request=request)
    assert response.model_dump() == before
    assert request.context.to_mapping() == context_before
    assert request.structured_output.schema.to_mapping() == schema_before


@pytest.mark.parametrize(
    ("status", "category", "retryability", "message"),
    [
        (
            "incomplete",
            ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT,
            False,
            "OpenAI Responses output is incomplete",
        ),
        (
            "cancelled",
            ModelRuntimeErrorCategory.CANCELLED_OR_SUPERSEDED,
            False,
            "OpenAI Responses call was cancelled or superseded",
        ),
        (
            "failed",
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            "OpenAI Responses provider response was transient",
        ),
        (
            "queued",
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            "OpenAI Responses provider response was transient",
        ),
        (
            "in_progress",
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            "OpenAI Responses provider response was transient",
        ),
        (
            None,
            ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            "OpenAI Responses provider response was transient",
        ),
    ],
)
def test_status_precedence_maps_non_completed_responses(
    status: str | None,
    category: ModelRuntimeErrorCategory,
    retryability: bool,
    message: str,
) -> None:
    with pytest.raises(ModelRuntimeError) as caught:
        _map(_response([], status=status))
    assert caught.value.category is category
    assert caught.value.retryability is retryability
    assert caught.value.model_call_id is _CALL_ID
    assert caught.value.message == message
    assert "response-id" not in caught.value.message


@pytest.mark.parametrize("status", ["incomplete", "cancelled", "failed", "queued"])
def test_status_errors_attach_complete_metadata_when_available(status: str) -> None:
    response = _response([_message(_text("ignored"))], status=status)
    with pytest.raises(ModelRuntimeError) as caught:
        _map(response)
    assert caught.value.provider_metadata is not None
    assert caught.value.provider_metadata.provider_attempt_ids is _ATTEMPTS


@pytest.mark.parametrize("field", ["usage", "model", "request_id"])
def test_missing_required_metadata_keeps_status_error_safe(field: str) -> None:
    response = _response([_message(_text("text"))])
    if field == "usage":
        object.__setattr__(response, "usage", None)
    elif field == "model":
        object.__setattr__(response, "model", "")
    else:
        object.__setattr__(response, "_request_id", None)
    with pytest.raises(ModelRuntimeError) as caught:
        _map(response)
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.provider_metadata is None


def test_unknown_status_is_a_safe_transient_error() -> None:
    response = _response([])
    object.__setattr__(response, "status", "future-status")
    with pytest.raises(ModelRuntimeError) as caught:
        _map(response)
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.retryability is True
    assert "future-status" not in caught.value.message


def test_subclassed_status_is_malformed_not_a_known_status() -> None:
    response = _response([])
    object.__setattr__(response, "status", _TextSubclass("incomplete"))
    with pytest.raises(ModelRuntimeError) as caught:
        _map(response)
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.retryability is True


def test_refusal_wins_over_text_and_redacts_provider_content() -> None:
    refusal = "private refusal instructions"
    with pytest.raises(ModelRuntimeError) as caught:
        _map(_response([_message(_text("ignored"), _refusal(refusal))]))
    assert caught.value.category is ModelRuntimeErrorCategory.REFUSAL
    assert caught.value.retryability is False
    assert caught.value.message == "OpenAI Responses provider refused the request"
    assert refusal not in caught.value.message


@pytest.mark.parametrize(
    "output",
    [
        [_message(_refusal("refusal-marker")), _tool_call()],
        [_tool_call(), _message(_refusal("refusal-marker"))],
    ],
)
def test_refusal_wins_after_full_scan_over_unsupported_tool_output(
    output: list[dict[str, object]],
) -> None:
    with pytest.raises(ModelRuntimeError) as caught:
        _map(_response(output))
    assert caught.value.category is ModelRuntimeErrorCategory.REFUSAL
    assert caught.value.retryability is False
    assert caught.value.message == "OpenAI Responses provider refused the request"
    assert "refusal-marker" not in caught.value.message


def test_empty_completed_output_is_incomplete() -> None:
    with pytest.raises(ModelRuntimeError) as caught:
        _map(_response([_reasoning()]))
    assert caught.value.category is ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT
    assert caught.value.retryability is False
    assert caught.value.message == "OpenAI Responses output is incomplete"


def test_whitespace_only_completed_output_is_incomplete_without_trimming_success() -> (
    None
):
    with pytest.raises(ModelRuntimeError) as caught:
        _map(_response([_message(_text(" \n\t "))]))
    assert caught.value.category is ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT
    assert caught.value.retryability is False
    assert caught.value.message == "OpenAI Responses output is incomplete"


def test_nonempty_payload_preserves_provider_whitespace() -> None:
    result = cast(Any, _map(_response([_message(_text("  text  "))])))
    assert result.output_envelope.payload_text == "  text  "


def test_unsupported_tool_output_is_transient_and_redacted() -> None:
    with pytest.raises(ModelRuntimeError) as caught:
        _map(_response([_tool_call()]))
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.retryability is True
    assert caught.value.message == "OpenAI Responses provider response was transient"
    assert "lookup" not in caught.value.message


@pytest.mark.parametrize("field", ["error", "incomplete_details"])
def test_completed_contradictory_status_fields_are_transient(field: str) -> None:
    response = _response([_message(_text("text"))])
    object.__setattr__(response, field, object())
    with pytest.raises(ModelRuntimeError) as caught:
        _map(response)
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.retryability is True
    assert caught.value.provider_metadata is not None
    assert caught.value.message == "OpenAI Responses provider response was transient"


def test_malformed_metadata_is_a_safe_transient_error() -> None:
    response = _response([_message(_text("text"))], response_id="")
    with pytest.raises(ModelRuntimeError) as caught:
        _map(response)
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.retryability is True
    assert caught.value.provider_metadata is None


@pytest.mark.parametrize(
    ("request_value", "response", "attempts", "latency"),
    [
        (None, _response([_message(_text("x"))]), _ATTEMPTS, 1),
        (object(), _response([_message(_text("x"))]), _ATTEMPTS, 1),
        (_request(), object(), _ATTEMPTS, 1),
        (_request(), _response([_message(_text("x"))]), None, 1),
        (_request(), _response([_message(_text("x"))]), (), 1),
        (_request(), _response([_message(_text("x"))]), [_ATTEMPTS[0]], 1),
        (_request(), _response([_message(_text("x"))]), _TupleSubclass(_ATTEMPTS), 1),
        (_request(), _response([_message(_text("x"))]), (object(),), 1),
        (_request(), _response([_message(_text("x"))]), _ATTEMPTS, True),
        (_request(), _response([_message(_text("x"))]), _ATTEMPTS, -1),
        (_request(), _response([_message(_text("x"))]), _ATTEMPTS, 1.0),
        (_request(), _response([_message(_text("x"))]), _ATTEMPTS, _IntSubclass(1)),
    ],
)
def test_mapper_rejects_raw_none_subclass_and_invalid_inputs(
    request_value: object,
    response: object,
    attempts: object,
    latency: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _map(response, request=request_value, attempts=attempts, latency_ms=latency)


def test_mapper_rejects_subclassed_request_and_response() -> None:
    request = _request()
    response = _response([_message(_text("x"))])
    subclass_request = _RequestSubclass(
        request.identity,
        request.instructions,
        request.context,
        request.structured_output,
        request.execution_profile,
        request.contract_versions,
    )
    subclass_response = _ResponseSubclass.model_validate(response.model_dump())
    subclass_response._request_id = "request-id"  # type: ignore[attr-defined]
    with pytest.raises(TypeError):
        _map(response, request=subclass_request)
    with pytest.raises(TypeError):
        _map(subclass_response)


def test_mapper_result_is_a_provider_neutral_immutable_dto() -> None:
    result = cast(Any, _map(_response([_message(_text("x"))])))
    assert isinstance(result.output_envelope, ModelOutputEnvelope)
    with pytest.raises(FrozenInstanceError):
        result.output_envelope = None
    with pytest.raises(FrozenInstanceError):
        del result.provider_metadata


def test_recovery_identity_remains_request_owned_and_errors_do_not_leak_attempts() -> (
    None
):
    request = ModelCallRequest(
        ModelCallIdentity(
            _CALL_ID,
            ModelCallId("recovered-from"),
            ModelRecoveryKind.REPAIR,
        ),
        "instruction-marker",
        StructuredContent.from_mapping({"context": ["value"]}),
        StructuredOutputSpec(
            "schema-1",
            "v1",
            StructuredContent.from_mapping({"type": "object"}),
        ),
        _PROFILE,
        ModelCallContractVersions("prompt-1", "v1", "skill-1", "domain-1", "context-1"),
    )
    with pytest.raises(ModelRuntimeError) as caught:
        _map(_response([_tool_call()]), request=request)
    assert caught.value.model_call_id is _CALL_ID
    for marker in (
        "instruction-marker",
        "context",
        "schema-1",
        "attempt-1",
        "attempt-2",
        "tool-call-1",
    ):
        assert marker not in caught.value.message
