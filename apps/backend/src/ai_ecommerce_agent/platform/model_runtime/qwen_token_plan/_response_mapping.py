"""Private mapping from one Qwen Chat Completion to model contracts."""

from __future__ import annotations

import json as _json
from typing import NoReturn
from typing import cast as _cast

import openai as _openai
from openai.types.chat.chat_completion import ChatCompletion as _ChatCompletion
from openai.types.chat.chat_completion import Choice as _Choice
from openai.types.chat.chat_completion_message import (
    ChatCompletionMessage as _ChatCompletionMessage,
)
from openai.types.completion_usage import CompletionUsage as _CompletionUsage

import ai_ecommerce_agent.application.model_runtime as _contracts

_INCOMPLETE_MESSAGE = "Qwen Token Plan output is incomplete"
_CANCELLED_MESSAGE = "Qwen Token Plan call was cancelled or superseded"
_TRANSIENT_MESSAGE = "Qwen Token Plan provider response was transient"
_REFUSAL_MESSAGE = "Qwen Token Plan provider refused the request"
_INVALID_CANDIDATE_MESSAGE = "Qwen Token Plan output was not valid JSON"


class _MappingError(ValueError):
    pass


def _text(value: object, name: str) -> str:
    if type(value) is not str or not value.strip():
        raise _MappingError(f"invalid {name}")
    return value


def _nonnegative_int(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise _MappingError(f"invalid {name}")
    return value


def _request_call_id(
    request: _contracts.ModelCallRequest,
) -> _contracts.ModelCallId:
    if type(request.identity) is not _contracts.ModelCallIdentity:
        raise TypeError("request identity must be exact")
    call_id = request.identity.model_call_id
    if type(call_id) is not _contracts.ModelCallId:
        raise TypeError("request call identity must be exact")
    return call_id


def _error(
    request: _contracts.ModelCallRequest,
    category: _contracts.ModelRuntimeErrorCategory,
    retryability: bool,
    message: str,
    metadata: _contracts.ProviderCallMetadata | None = None,
) -> _contracts.ModelRuntimeError:
    return _contracts.ModelRuntimeError(
        category=category,
        message=message,
        retryability=retryability,
        model_call_id=_request_call_id(request),
        provider_metadata=metadata,
    )


def _raise_transient(
    request: _contracts.ModelCallRequest,
    metadata: _contracts.ProviderCallMetadata | None = None,
) -> NoReturn:
    raise _error(
        request,
        _contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
        True,
        _TRANSIENT_MESSAGE,
        metadata,
    )


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> NoReturn:
    raise ValueError(value)


def _validate_json_object(payload: str) -> None:
    try:
        decoded = _json.loads(
            payload,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite,
        )
    except Exception as error:
        del error
        raise _MappingError("invalid JSON") from None
    if type(decoded) is not dict:
        raise _MappingError("JSON payload must be an object")


def _metadata(
    *,
    request: _contracts.ModelCallRequest,
    response: _ChatCompletion,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    latency_ms: int,
) -> _contracts.ProviderCallMetadata:
    response_id = _text(response.id, "response id")
    response_model = _text(response.model, "model")
    sdk_version = _text(getattr(_openai, "__version__", None), "SDK version")
    usage = response.usage
    if type(usage) is not _CompletionUsage:
        raise _MappingError("invalid usage")
    token_usage = _contracts.ModelTokenUsage(
        _nonnegative_int(usage.prompt_tokens, "prompt tokens"),
        _nonnegative_int(usage.completion_tokens, "completion tokens"),
        _nonnegative_int(usage.total_tokens, "total tokens"),
    )
    versions = _contracts.ModelRuntimeVersionTuple(
        provider_id="qwen_token_plan",
        api_family="chat_completions",
        sdk_version=sdk_version,
        configured_model_id="qwen3.8-max",
        resolved_model_id=response_model,
        prompt_template_id=request.contract_versions.prompt_template_id,
        prompt_template_version=request.contract_versions.prompt_template_version,
        output_schema_id=request.structured_output.output_schema_id,
        output_schema_version=request.structured_output.output_schema_version,
        skill_contract_version=request.contract_versions.skill_contract_version,
        domain_validator_version=request.contract_versions.domain_validator_version,
        execution_profile_id=request.execution_profile.execution_profile_id,
        execution_profile_version=request.execution_profile.execution_profile_version,
        context_assembly_version=request.contract_versions.context_assembly_version,
    )
    request_id = getattr(response, "_request_id", None)
    if request_id is not None and (
        type(request_id) is not str or not request_id.strip()
    ):
        raise _MappingError("invalid request id")
    return _contracts.ProviderCallMetadata(
        model_call_id=_request_call_id(request),
        provider_attempt_ids=provider_attempt_ids,
        version_tuple=versions,
        provider_response_id=response_id,
        provider_request_id=request_id,
        usage=token_usage,
        latency_ms=latency_ms,
    )


def _try_metadata(
    *,
    request: _contracts.ModelCallRequest,
    response: _ChatCompletion,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    latency_ms: int,
) -> _contracts.ProviderCallMetadata | None:
    try:
        return _metadata(
            request=request,
            response=response,
            provider_attempt_ids=provider_attempt_ids,
            latency_ms=latency_ms,
        )
    except (AttributeError, TypeError, ValueError):
        return None


def map_qwen_token_plan_response(
    *,
    request: _contracts.ModelCallRequest,
    response: _ChatCompletion,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    latency_ms: int,
) -> _contracts.ModelCallResult:
    """Map one untrusted Chat Completion without retaining provider objects."""

    choices: list[_Choice] = []
    choice: _Choice = _cast(_Choice, None)
    message: _ChatCompletionMessage = _cast(_ChatCompletionMessage, None)
    content: str = _cast(str, None)
    try:
        if type(request) is not _contracts.ModelCallRequest:
            raise TypeError("request must be an exact ModelCallRequest")
        if type(response) is not _ChatCompletion:
            raise TypeError("response must be an exact ChatCompletion")
        if type(provider_attempt_ids) is not tuple or not provider_attempt_ids:
            raise TypeError("provider_attempt_ids must be a non-empty tuple")
        if any(
            type(attempt) is not _contracts.ProviderAttemptId
            for attempt in provider_attempt_ids
        ):
            raise TypeError("provider_attempt_ids members must be exact")
        if type(latency_ms) is not int:
            raise TypeError("latency_ms must be an int")
        if latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        _request_call_id(request)
        metadata = _try_metadata(
            request=request,
            response=response,
            provider_attempt_ids=provider_attempt_ids,
            latency_ms=latency_ms,
        )
        if metadata is None:
            _raise_transient(request)
        if response.object != "chat.completion":
            _raise_transient(request, metadata)
        choices = response.choices
        if type(choices) is not list or len(choices) != 1:
            _raise_transient(request, metadata)
        choice = choices[0]
        if (
            type(choice) is not _Choice
            or type(choice.message) is not _ChatCompletionMessage
        ):
            _raise_transient(request, metadata)
        message = choice.message
        if message.role != "assistant":
            _raise_transient(request, metadata)
        if message.refusal is not None:
            raise _error(
                request,
                _contracts.ModelRuntimeErrorCategory.REFUSAL,
                False,
                _REFUSAL_MESSAGE,
                metadata,
            )
        if message.tool_calls is not None or message.function_call is not None:
            _raise_transient(request, metadata)
        finish_reason = choice.finish_reason
        if finish_reason == "length":
            raise _error(
                request,
                _contracts.ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT,
                False,
                _INCOMPLETE_MESSAGE,
                metadata,
            )
        if finish_reason != "stop":
            _raise_transient(request, metadata)
        content = _cast(str, message.content)
        if type(content) is not str or not content.strip():
            raise _error(
                request,
                _contracts.ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT,
                False,
                _INCOMPLETE_MESSAGE,
                metadata,
            )
        try:
            _validate_json_object(content)
        except _MappingError:
            raise _error(
                request,
                _contracts.ModelRuntimeErrorCategory.INVALID_CANDIDATE,
                False,
                _INVALID_CANDIDATE_MESSAGE,
                metadata,
            ) from None
        return _contracts.ModelCallResult(
            _contracts.ModelOutputEnvelope(content),
            metadata,
        )
    finally:
        del response, choices, choice, message, content


__all__ = ["map_qwen_token_plan_response"]
