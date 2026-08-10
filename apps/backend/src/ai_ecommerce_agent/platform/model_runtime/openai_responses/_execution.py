"""Private execution of one injected OpenAI Responses transport attempt."""

from __future__ import annotations

from time import monotonic
from typing import cast

import openai as _openai
import openai.types.responses as _responses
import openai.types.responses.response_create_params as _response_params

import ai_ecommerce_agent.application.model_runtime as _contracts

from ._response_mapping import map_openai_responses_response
from .request_preparation import (
    OpenAIResponsesCallParameters,
    prepare_openai_responses_call,
)

_CONFIGURATION_MESSAGE = "OpenAI Responses configuration/access failure"
_INVALID_REQUEST_MESSAGE = "OpenAI Responses request was invalid"
_TRANSIENT_MESSAGE = "OpenAI Responses provider transport failed"


def _failure_classification(
    error: _openai.OpenAIError,
) -> tuple[_contracts.ModelRuntimeErrorCategory, bool, str]:
    if isinstance(error, (_openai.APITimeoutError, _openai.APIConnectionError)):
        return (
            _contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            True,
            _TRANSIENT_MESSAGE,
        )
    status_code = getattr(error, "status_code", None)
    if type(status_code) is int:
        if status_code in {401, 403, 404}:
            return (
                _contracts.ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS,
                False,
                _CONFIGURATION_MESSAGE,
            )
        if status_code == 408 or status_code in {409, 429} or status_code >= 500:
            return (
                _contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
                True,
                _TRANSIENT_MESSAGE,
            )
        if 400 <= status_code < 500:
            return (
                _contracts.ModelRuntimeErrorCategory.INVALID_REQUEST,
                False,
                _INVALID_REQUEST_MESSAGE,
            )
    return (
        _contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
        True,
        _TRANSIENT_MESSAGE,
    )


def _request_id(error: _openai.OpenAIError) -> str | None:
    value = getattr(error, "request_id", None)
    if type(value) is str and value.strip():
        return value
    return None


def _failure_metadata(
    *,
    request: _contracts.ModelCallRequest,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    provider_request_id: str | None,
    latency_ms: int,
) -> _contracts.ProviderCallMetadata | None:
    try:
        versions = _contracts.ModelRuntimeVersionTuple(
            provider_id="openai",
            api_family="responses",
            sdk_version=_openai.__version__,
            configured_model_id="gpt-5.6-terra",
            resolved_model_id=None,
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
            model_call_id=request.identity.model_call_id,
            provider_attempt_ids=provider_attempt_ids,
            version_tuple=versions,
            provider_response_id=None,
            provider_request_id=provider_request_id,
            usage=None,
            latency_ms=latency_ms,
        )
    except (AttributeError, TypeError, ValueError):
        return None


def _validate(
    *,
    client: _openai.OpenAI,
    request: _contracts.ModelCallRequest,
    parameters: OpenAIResponsesCallParameters,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
) -> None:
    if type(client) is not _openai.OpenAI:
        raise TypeError("client must be an exact synchronous OpenAI")
    if type(request) is not _contracts.ModelCallRequest:
        raise TypeError("request must be an exact ModelCallRequest")
    if type(parameters) is not OpenAIResponsesCallParameters:
        raise TypeError("parameters must be exact OpenAIResponsesCallParameters")
    if type(provider_attempt_ids) is not tuple or not provider_attempt_ids:
        raise TypeError("provider_attempt_ids must be a non-empty tuple")
    if any(
        type(attempt_id) is not _contracts.ProviderAttemptId
        for attempt_id in provider_attempt_ids
    ):
        raise TypeError("provider_attempt_ids members must be exact")
    if type(client.max_retries) is not int or client.max_retries != 0:
        raise _contracts.ModelRuntimeError(
            category=_contracts.ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS,
            message=_CONFIGURATION_MESSAGE,
            retryability=False,
            model_call_id=request.identity.model_call_id,
            provider_metadata=None,
        )


def _latency_ms(start: float, finish: float) -> int:
    return max(0, int((finish - start) * 1000))


def execute_openai_responses_attempt(
    *,
    client: _openai.OpenAI,
    request: _contracts.ModelCallRequest,
    parameters: OpenAIResponsesCallParameters,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
) -> _contracts.ModelCallResult:
    """Execute exactly one prepared Responses request through an injected client."""
    _validate(
        client=client,
        request=request,
        parameters=parameters,
        provider_attempt_ids=provider_attempt_ids,
    )
    prepared = prepare_openai_responses_call(request=request, parameters=parameters)
    start = monotonic()
    classification: tuple[_contracts.ModelRuntimeErrorCategory, bool, str] | None = None
    provider_request_id: str | None = None
    response: object | None = None
    try:
        request_body = cast(
            _response_params.ResponseCreateParamsNonStreaming,
            prepared.request_body.to_mapping(),
        )
        response = client.responses.create(
            **request_body,
            timeout=prepared.timeout_seconds,
        )
    except _openai.OpenAIError as error:
        finish = monotonic()
        classification = _failure_classification(error)
        provider_request_id = _request_id(error)
    else:
        finish = monotonic()
    latency_ms = _latency_ms(start, finish)
    if classification is not None:
        category, retryability, message = classification
        metadata = _failure_metadata(
            request=request,
            provider_attempt_ids=provider_attempt_ids,
            provider_request_id=provider_request_id,
            latency_ms=latency_ms,
        )
        raise _contracts.ModelRuntimeError(
            category=category,
            message=message,
            retryability=retryability,
            model_call_id=request.identity.model_call_id,
            provider_metadata=metadata,
        )
    return map_openai_responses_response(
        request=request,
        response=cast(_responses.Response, response),
        provider_attempt_ids=provider_attempt_ids,
        latency_ms=latency_ms,
    )
