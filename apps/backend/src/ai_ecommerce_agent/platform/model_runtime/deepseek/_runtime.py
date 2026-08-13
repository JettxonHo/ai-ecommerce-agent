"""Private, opt-in DeepSeek Chat Completions Model Runtime adapter."""

from __future__ import annotations

import os as _os
from time import monotonic as _monotonic
from typing import Any as _Any
from typing import cast as _cast

import openai as _openai
from openai.types.chat.chat_completion import ChatCompletion as _ChatCompletion

import ai_ecommerce_agent.application.model_runtime as _contracts

from ._request_preparation import (
    DeepSeekCallParameters,
    DeepSeekReasoningEffort,
    PreparedDeepSeekCall,
    prepare_deepseek_call,
)
from ._response_mapping import map_deepseek_response

DEEPSEEK_CREDENTIAL_REF = "deepseek_primary"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"
_DEEPSEEK_API_KEY_ENVIRONMENT_NAME = "DEEPSEEK_API_KEY"
_CONFIGURATION_MESSAGE = "DeepSeek configuration/access failure"
_TRANSIENT_MESSAGE = "DeepSeek provider transport failed"


DEEPSEEK_PROFILE_CATALOG: tuple[DeepSeekCallParameters, ...] = (
    DeepSeekCallParameters(
        _contracts.ModelExecutionProfile("product_intake_v1", "v1"),
        DeepSeekReasoningEffort.HIGH,
        8192,
        120,
    ),
    DeepSeekCallParameters(
        _contracts.ModelExecutionProfile("customer_insight_v1", "v1"),
        DeepSeekReasoningEffort.HIGH,
        12288,
        180,
    ),
    DeepSeekCallParameters(
        _contracts.ModelExecutionProfile("product_positioning_v1", "v1"),
        DeepSeekReasoningEffort.HIGH,
        16384,
        240,
    ),
    DeepSeekCallParameters(
        _contracts.ModelExecutionProfile("marketing_brief_v1", "v1"),
        DeepSeekReasoningEffort.HIGH,
        16384,
        180,
    ),
    DeepSeekCallParameters(
        _contracts.ModelExecutionProfile("xiaohongshu_mapping_v1", "v1"),
        DeepSeekReasoningEffort.HIGH,
        12288,
        120,
    ),
)


class DeepSeekConfigurationError(ValueError):
    """Safe fixed error raised when the private adapter is unavailable."""


def _parameters_for(
    execution_profile: _contracts.ModelExecutionProfile,
    model_call_id: _contracts.ModelCallId,
) -> DeepSeekCallParameters:
    for parameters in DEEPSEEK_PROFILE_CATALOG:
        if parameters.execution_profile == execution_profile:
            return parameters
    raise _contracts.ModelRuntimeError(
        category=_contracts.ModelRuntimeErrorCategory.INVALID_REQUEST,
        message="execution profile is not an accepted DeepSeek profile",
        retryability=False,
        model_call_id=model_call_id,
        provider_metadata=None,
    )


def _provider_request_id(error: BaseException) -> str | None:
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
            provider_id="deepseek",
            api_family="chat_completions",
            sdk_version=_openai.__version__,
            configured_model_id=DEEPSEEK_MODEL,
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


def _map_provider_error(
    *,
    request: _contracts.ModelCallRequest,
    error: BaseException,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    latency_ms: int,
) -> _contracts.ModelRuntimeError:
    status_code = getattr(error, "status_code", None)
    if type(status_code) is int and status_code in {401, 402, 403, 404}:
        category = _contracts.ModelRuntimeErrorCategory.CONFIGURATION_OR_ACCESS
        retryability = False
        message = _CONFIGURATION_MESSAGE
    elif type(status_code) is int and status_code in {400, 422}:
        category = _contracts.ModelRuntimeErrorCategory.INVALID_REQUEST
        retryability = False
        message = "DeepSeek request was invalid"
    else:
        category = _contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
        retryability = True
        message = _TRANSIENT_MESSAGE
    return _contracts.ModelRuntimeError(
        category=category,
        message=message,
        retryability=retryability,
        model_call_id=request.identity.model_call_id,
        provider_metadata=_failure_metadata(
            request=request,
            provider_attempt_ids=provider_attempt_ids,
            provider_request_id=_provider_request_id(error),
            latency_ms=latency_ms,
        ),
    )


def _execute_one_attempt(
    *,
    client: _openai.OpenAI,
    request: _contracts.ModelCallRequest,
    prepared: PreparedDeepSeekCall,
    provider_attempt_ids: tuple[_contracts.ProviderAttemptId, ...],
    overall_deadline_monotonic: float,
) -> _contracts.ModelCallResult:
    remaining = overall_deadline_monotonic - _monotonic()
    if remaining <= 0:
        raise _contracts.ModelRuntimeError(
            category=_contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            message=_TRANSIENT_MESSAGE,
            retryability=True,
            model_call_id=request.identity.model_call_id,
            provider_metadata=None,
        )
    start = _monotonic()
    try:
        create = _cast(_Any, client.chat.completions.create)
        response = _cast(
            _ChatCompletion,
            create(
                **prepared.request_body.to_mapping(),
                timeout=min(prepared.timeout_seconds, remaining),
            ),
        )
    except Exception as error:
        latency_ms = max(0, int((_monotonic() - start) * 1000))
        mapped = _map_provider_error(
            request=request,
            error=_cast(BaseException, error),
            provider_attempt_ids=provider_attempt_ids,
            latency_ms=latency_ms,
        )
        del error
        raise mapped from None
    latency_ms = max(0, int((_monotonic() - start) * 1000))
    if type(response) is not _ChatCompletion:
        del response
        raise _contracts.ModelRuntimeError(
            category=_contracts.ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE,
            message=_TRANSIENT_MESSAGE,
            retryability=True,
            model_call_id=request.identity.model_call_id,
            provider_metadata=None,
        )
    try:
        return map_deepseek_response(
            request=request,
            response=response,
            provider_attempt_ids=provider_attempt_ids,
            latency_ms=latency_ms,
        )
    finally:
        del response


class DeepSeekModelRuntime:
    """The private adapter implementing the provider-neutral runtime port."""

    def __init__(self, *, client: _openai.OpenAI) -> None:
        if type(client) is not _openai.OpenAI:
            raise TypeError("client must be an exact synchronous OpenAI")
        if type(client.max_retries) is not int or client.max_retries != 0:
            raise DeepSeekConfigurationError(_CONFIGURATION_MESSAGE)
        self._client = client
        self._metadata: list[_contracts.ProviderCallMetadata] = []

    @property
    def metadata_records(self) -> tuple[_contracts.ProviderCallMetadata, ...]:
        return tuple(self._metadata)

    @property
    def sdk_max_retries(self) -> int:
        return self._client.max_retries

    @property
    def retry_count(self) -> int:
        return 0

    def execute(
        self, request: _contracts.ModelCallRequest
    ) -> _contracts.ModelCallResult:
        if type(request) is not _contracts.ModelCallRequest:
            raise TypeError("request must be an exact ModelCallRequest")
        parameters = _parameters_for(
            request.execution_profile,
            request.identity.model_call_id,
        )
        attempt_id = _contracts.ProviderAttemptId(
            f"{request.identity.model_call_id.value}-attempt-1"
        )
        prepared = prepare_deepseek_call(request=request, parameters=parameters)
        try:
            result = _execute_one_attempt(
                client=self._client,
                request=request,
                prepared=prepared,
                provider_attempt_ids=(attempt_id,),
                overall_deadline_monotonic=_monotonic() + parameters.timeout_seconds,
            )
        except _contracts.ModelRuntimeError as error:
            if error.provider_metadata is not None:
                self._metadata.append(error.provider_metadata)
            raise
        self._metadata.append(result.provider_metadata)
        return result

    def close(self) -> None:
        self._client.close()


def create_deepseek_runtime(
    *, credential_ref: str = DEEPSEEK_CREDENTIAL_REF
) -> DeepSeekModelRuntime:
    """Resolve ``deepseek_primary`` and build one exact sync OpenAI client."""

    if credential_ref != DEEPSEEK_CREDENTIAL_REF:
        raise ValueError("unsupported credential reference; expected deepseek_primary")
    secret = _os.environ.get(_DEEPSEEK_API_KEY_ENVIRONMENT_NAME, "")
    if type(secret) is not str or not secret.strip():
        del secret
        raise DeepSeekConfigurationError(_CONFIGURATION_MESSAGE)
    client: _openai.OpenAI | None = None
    try:
        client = _openai.OpenAI(
            api_key=secret,
            base_url=DEEPSEEK_BASE_URL,
            max_retries=0,
        )
    except Exception as error:
        del error
        del secret
        raise DeepSeekConfigurationError(_CONFIGURATION_MESSAGE) from None
    del secret
    if type(client) is not _openai.OpenAI or client.max_retries != 0:
        if type(client) is _openai.OpenAI:
            client.close()
        raise DeepSeekConfigurationError(_CONFIGURATION_MESSAGE)
    return DeepSeekModelRuntime(client=client)


__all__ = [
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_CREDENTIAL_REF",
    "DEEPSEEK_MODEL",
    "DEEPSEEK_PROFILE_CATALOG",
    "DeepSeekConfigurationError",
    "DeepSeekModelRuntime",
    "create_deepseek_runtime",
]
