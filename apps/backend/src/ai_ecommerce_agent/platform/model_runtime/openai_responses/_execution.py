"""Private execution of one injected OpenAI Responses transport attempt."""

from __future__ import annotations

from email.utils import parsedate_to_datetime
from math import isfinite
from random import random
from time import monotonic, sleep, time
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
_CONFIGURATION_CATEGORY = _contracts.ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS
_INVALID_REQUEST_CATEGORY = _contracts.ModelRuntimeErrorCategory.INVALID_REQUEST
_TRANSIENT_CATEGORY = _contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE


def _failure_classification(
    error: _openai.OpenAIError,
) -> tuple[_contracts.ModelRuntimeErrorCategory, bool, str]:
    if isinstance(error, (_openai.APITimeoutError, _openai.APIConnectionError)):
        return _TRANSIENT_CATEGORY, True, _TRANSIENT_MESSAGE
    status_code = getattr(error, "status_code", None)
    if type(status_code) is int:
        if status_code in {401, 403, 404}:
            return _CONFIGURATION_CATEGORY, False, _CONFIGURATION_MESSAGE
        if status_code == 408 or status_code in {409, 429} or status_code >= 500:
            return _TRANSIENT_CATEGORY, True, _TRANSIENT_MESSAGE
        if 400 <= status_code < 500:
            return _INVALID_REQUEST_CATEGORY, False, _INVALID_REQUEST_MESSAGE
    return _TRANSIENT_CATEGORY, True, _TRANSIENT_MESSAGE


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
    request_body = cast(
        _response_params.ResponseCreateParamsNonStreaming,
        prepared.request_body.to_mapping(),
    )
    response, error, latency_ms = _transport_attempt(
        client=client,
        request_body=request_body,
        timeout_seconds=prepared.timeout_seconds,
    )
    if error is not None:
        raise _mapped_error(
            request=request,
            error=error,
            provider_attempt_ids=provider_attempt_ids,
            latency_ms=latency_ms,
        )
    return map_openai_responses_response(
        request=request,
        response=cast(_responses.Response, response),
        provider_attempt_ids=provider_attempt_ids,
        latency_ms=latency_ms,
    )


def _retry_delay(error: _openai.OpenAIError, fallback: float) -> float:
    def positive(value: str | None, scale: float = 1.0) -> float | None:
        value = value or ""
        try:
            result = float(value) * scale
        except (TypeError, ValueError, OverflowError):
            return None
        return result if isfinite(result) and result > 0 else None

    try:
        headers = cast(dict[str, str], error.response.headers)  # type: ignore[attr-defined]
        delay = positive(headers.get("retry-after-ms"), 0.001)
        if delay is not None:
            return delay
        value = headers.get("Retry-After")
        delay = positive(value)
        if delay is not None:
            return delay
        if type(value) is str:
            date = parsedate_to_datetime(value)
            if date.tzinfo is not None:
                delay = date.timestamp() - time()
                if isfinite(delay) and delay > 0:
                    return delay
    except (AttributeError, TypeError, ValueError, OverflowError, IndexError, OSError):
        pass
    return fallback * random()


def _transport_attempt(
    *,
    client: _openai.OpenAI,
    request_body: _response_params.ResponseCreateParamsNonStreaming,
    timeout_seconds: float,
) -> tuple[object | None, _openai.OpenAIError | None, int]:
    start = monotonic()
    try:
        response = client.responses.create(**request_body, timeout=timeout_seconds)
    except _openai.OpenAIError as error:
        return None, error, _latency_ms(start, monotonic())
    return response, None, _latency_ms(start, monotonic())


def _mapped_error(
    *,
    request: _contracts.ModelCallRequest,
    error: _openai.OpenAIError,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    latency_ms: int,
) -> _contracts.ModelRuntimeError:
    category, retryability, message = _failure_classification(error)
    return _contracts.ModelRuntimeError(
        category=category,
        message=message,
        retryability=retryability,
        model_call_id=request.identity.model_call_id,
        provider_metadata=_failure_metadata(
            request=request,
            provider_attempt_ids=provider_attempt_ids,
            provider_request_id=_request_id(error),
            latency_ms=latency_ms,
        ),
    )


def execute_openai_responses_with_transport_retry(
    *,
    client: _openai.OpenAI,
    request: _contracts.ModelCallRequest,
    parameters: OpenAIResponsesCallParameters,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    overall_deadline_monotonic: float,
    fallback_retry_delay_seconds: float,
) -> _contracts.ModelCallResult:
    """Execute at most two injected transport attempts inside one deadline."""
    _validate(
        client=client,
        request=request,
        parameters=parameters,
        provider_attempt_ids=provider_attempt_ids,
    )
    if len(provider_attempt_ids) not in (1, 2):
        raise ValueError("provider_attempt_ids must contain one or two IDs")
    if len(provider_attempt_ids) == 2 and (
        provider_attempt_ids[0].value == provider_attempt_ids[1].value
    ):
        raise ValueError("provider_attempt_ids must be distinct")
    if type(overall_deadline_monotonic) is not float:
        raise TypeError("overall_deadline_monotonic must be a float")
    if not isfinite(overall_deadline_monotonic):
        raise ValueError("overall_deadline_monotonic must be finite")
    if type(fallback_retry_delay_seconds) is not float:
        raise TypeError("fallback_retry_delay_seconds must be a float")
    if not isfinite(fallback_retry_delay_seconds) or fallback_retry_delay_seconds <= 0:
        raise ValueError("fallback_retry_delay_seconds must be positive and finite")

    prepared = prepare_openai_responses_call(request=request, parameters=parameters)
    request_body = cast(
        _response_params.ResponseCreateParamsNonStreaming,
        prepared.request_body.to_mapping(),
    )
    first_attempt_ids = provider_attempt_ids[:1]
    remaining = overall_deadline_monotonic - monotonic()
    if remaining <= 0:
        raise _contracts.ModelRuntimeError(
            category=_contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            message=_TRANSIENT_MESSAGE,
            retryability=True,
            model_call_id=request.identity.model_call_id,
            provider_metadata=None,
        )
    response, error, latency_ms = _transport_attempt(
        client=client,
        request_body=request_body,
        timeout_seconds=min(parameters.timeout_seconds, remaining),
    )
    if error is None:
        return map_openai_responses_response(
            request=request,
            response=cast(_responses.Response, response),
            provider_attempt_ids=first_attempt_ids,
            latency_ms=latency_ms,
        )
    status_code = getattr(error, "status_code", None)
    retryable = isinstance(
        error, (_openai.APITimeoutError, _openai.APIConnectionError)
    ) or (
        type(status_code) is int
        and (status_code in {408, 409, 429} or status_code >= 500)
    )
    first_error = _mapped_error(
        request=request,
        error=error,
        provider_attempt_ids=first_attempt_ids,
        latency_ms=latency_ms,
    )
    if len(provider_attempt_ids) == 1 or not retryable:
        raise first_error
    delay = _retry_delay(error, fallback_retry_delay_seconds)
    if overall_deadline_monotonic - monotonic() <= delay:
        raise first_error
    sleep(delay)
    remaining = overall_deadline_monotonic - monotonic()
    if remaining <= 0:
        raise first_error
    response, error, latency_ms = _transport_attempt(
        client=client,
        request_body=request_body,
        timeout_seconds=min(parameters.timeout_seconds, remaining),
    )
    if error is None:
        return map_openai_responses_response(
            request=request,
            response=cast(_responses.Response, response),
            provider_attempt_ids=provider_attempt_ids,
            latency_ms=latency_ms,
        )
    raise _mapped_error(
        request=request,
        error=error,
        provider_attempt_ids=provider_attempt_ids,
        latency_ms=latency_ms,
    )
