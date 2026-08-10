"""Private mapping from a typed OpenAI Responses response to model contracts."""

from __future__ import annotations

from typing import NoReturn

import openai as _openai
import openai.types.responses as _responses

import ai_ecommerce_agent.application.model_runtime as _contracts

_INCOMPLETE_MESSAGE = "OpenAI Responses output is incomplete"
_CANCELLED_MESSAGE = "OpenAI Responses call was cancelled or superseded"
_TRANSIENT_MESSAGE = "OpenAI Responses provider response was transient"
_REFUSAL_MESSAGE = "OpenAI Responses provider refused the request"


class _MappingError(ValueError):
    pass


def _text(value: object) -> str:
    if type(value) is not str or not value.strip():
        raise _MappingError("invalid text")
    return value


def _nonnegative_int(value: object) -> int:
    if type(value) is not int or value < 0:
        raise _MappingError("invalid integer")
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


def _metadata(
    *,
    request: _contracts.ModelCallRequest,
    response: _responses.Response,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    latency_ms: int,
) -> _contracts.ProviderCallMetadata:
    if type(request.contract_versions) is not _contracts.ModelCallContractVersions:
        raise _MappingError("invalid contract versions")
    if type(request.execution_profile) is not _contracts.ModelExecutionProfile:
        raise _MappingError("invalid execution profile")
    if type(request.structured_output) is not _contracts.StructuredOutputSpec:
        raise _MappingError("invalid structured output")
    response_id = _text(response.id)
    response_model = _text(response.model)
    request_id = _text(getattr(response, "_request_id", None))
    sdk_version = _text(getattr(_openai, "__version__", None))
    usage = response.usage
    if type(usage) is not _responses.ResponseUsage:
        raise _MappingError("invalid usage")
    token_usage = _contracts.ModelTokenUsage(
        _nonnegative_int(usage.input_tokens),
        _nonnegative_int(usage.output_tokens),
        _nonnegative_int(usage.total_tokens),
    )
    versions = _contracts.ModelRuntimeVersionTuple(
        provider_id="openai",
        api_family="responses",
        sdk_version=sdk_version,
        configured_model_id="gpt-5.6-terra",
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
    response: _responses.Response,
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


def _output_text(response: _responses.Response) -> tuple[bool, bool, str]:
    output = response.output
    if type(output) is not list:
        raise _MappingError("invalid output")
    refusal = False
    unsupported = False
    text_parts: list[str] = []
    for item in output:
        if type(item) is _responses.ResponseReasoningItem:
            continue
        if type(item) is not _responses.ResponseOutputMessage:
            unsupported = True
            continue
        if (
            type(item.id) is not str
            or not item.id.strip()
            or type(item.role) is not str
            or item.role != "assistant"
            or type(item.type) is not str
            or item.type != "message"
            or type(item.status) is not str
            or item.status != "completed"
            or type(item.content) is not list
        ):
            raise _MappingError("invalid response message")
        for block in item.content:
            if type(block) is _responses.ResponseOutputText:
                if type(block.text) is not str:
                    raise _MappingError("invalid output text")
                text_parts.append(block.text)
            elif type(block) is _responses.ResponseOutputRefusal:
                if type(block.refusal) is not str:
                    raise _MappingError("invalid refusal")
                refusal = True
            else:
                unsupported = True
    return refusal, unsupported, "".join(text_parts)


def map_openai_responses_response(
    *,
    request: _contracts.ModelCallRequest,
    response: _responses.Response,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    latency_ms: int,
) -> _contracts.ModelCallResult:
    """Map one SDK response without executing or parsing provider content."""
    if type(request) is not _contracts.ModelCallRequest:
        raise TypeError("request must be an exact ModelCallRequest")
    if type(response) is not _responses.Response:
        raise TypeError("response must be an exact OpenAI Response")
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
    status = response.status
    if type(status) is not str:
        _raise_transient(request, metadata)
    if status == "incomplete":
        raise _error(
            request,
            _contracts.ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT,
            False,
            _INCOMPLETE_MESSAGE,
            metadata,
        )
    if status == "cancelled":
        raise _error(
            request,
            _contracts.ModelRuntimeErrorCategory.CANCELLED_OR_SUPERSEDED,
            False,
            _CANCELLED_MESSAGE,
            metadata,
        )
    if status != "completed":
        _raise_transient(request, metadata)
    if response.error is not None or response.incomplete_details is not None:
        _raise_transient(request, metadata)
    if metadata is None:
        _raise_transient(request)
    try:
        refusal, unsupported, payload_text = _output_text(response)
    except _MappingError:
        _raise_transient(request, metadata)
    if refusal:
        raise _error(
            request,
            _contracts.ModelRuntimeErrorCategory.REFUSAL,
            False,
            _REFUSAL_MESSAGE,
            metadata,
        )
    if unsupported:
        _raise_transient(request, metadata)
    if not payload_text.strip():
        raise _error(
            request,
            _contracts.ModelRuntimeErrorCategory.INCOMPLETE_OUTPUT,
            False,
            _INCOMPLETE_MESSAGE,
            metadata,
        )
    return _contracts.ModelCallResult(
        _contracts.ModelOutputEnvelope(payload_text), metadata
    )
