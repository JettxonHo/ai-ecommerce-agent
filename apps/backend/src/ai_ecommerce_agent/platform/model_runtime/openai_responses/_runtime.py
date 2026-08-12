"""The narrow production OpenAI Responses Model Runtime adapter.

The adapter is intentionally the only place that owns an SDK client.  It
accepts the provider-neutral application port, selects one of the five fixed
Fast Lane profiles, and delegates one bounded operation to the existing
transport executor.  No SDK response, request body or provider payload is
retained outside this module.
"""

from __future__ import annotations

import os as _os
from time import monotonic as _monotonic

import openai as _openai

import ai_ecommerce_agent.application.model_runtime as _contracts

from ._execution import execute_openai_responses_with_transport_retry
from .request_preparation import (
    OpenAIReasoningEffort,
    OpenAIResponsesCallParameters,
)

OPENAI_PRIMARY_CREDENTIAL_REF = "openai_primary"
_OPENAI_API_KEY_ENVIRONMENT_NAME = "OPENAI_API_KEY"
_CONFIGURATION_MESSAGE = "OpenAI Responses configuration/access failure"
_FALLBACK_RETRY_DELAY_SECONDS = 0.25


OPENAI_RESPONSES_PROFILE_CATALOG: tuple[OpenAIResponsesCallParameters, ...] = (
    OpenAIResponsesCallParameters(
        _contracts.ModelExecutionProfile("product_intake_v1", "v1"),
        OpenAIReasoningEffort.LOW,
        8192,
        120,
    ),
    OpenAIResponsesCallParameters(
        _contracts.ModelExecutionProfile("customer_insight_v1", "v1"),
        OpenAIReasoningEffort.MEDIUM,
        12288,
        180,
    ),
    OpenAIResponsesCallParameters(
        _contracts.ModelExecutionProfile("product_positioning_v1", "v1"),
        OpenAIReasoningEffort.HIGH,
        16384,
        240,
    ),
    OpenAIResponsesCallParameters(
        _contracts.ModelExecutionProfile("marketing_brief_v1", "v1"),
        OpenAIReasoningEffort.MEDIUM,
        16384,
        180,
    ),
    OpenAIResponsesCallParameters(
        _contracts.ModelExecutionProfile("xiaohongshu_mapping_v1", "v1"),
        OpenAIReasoningEffort.LOW,
        12288,
        120,
    ),
)


def _parameters_for(
    execution_profile: _contracts.ModelExecutionProfile,
    model_call_id: _contracts.ModelCallId,
) -> OpenAIResponsesCallParameters:
    for parameters in OPENAI_RESPONSES_PROFILE_CATALOG:
        if parameters.execution_profile == execution_profile:
            return parameters
    raise _contracts.ModelRuntimeError(
        category=_contracts.ModelRuntimeErrorCategory.INVALID_REQUEST,
        message="execution profile is not an accepted OpenAI Responses profile",
        retryability=False,
        model_call_id=model_call_id,
        provider_metadata=None,
    )


class OpenAIResponsesConfigurationError(ValueError):
    """Safe fixed error raised when the live adapter cannot be configured."""


class OpenAIResponsesModelRuntime:
    """Provider adapter implementing the synchronous Model Runtime port."""

    def __init__(self, *, client: _openai.OpenAI) -> None:
        if type(client) is not _openai.OpenAI:
            raise TypeError("client must be an exact synchronous OpenAI")
        if type(client.max_retries) is not int or client.max_retries != 0:
            raise OpenAIResponsesConfigurationError(_CONFIGURATION_MESSAGE)
        self._client = client
        self._metadata: list[_contracts.ProviderCallMetadata] = []

    @property
    def metadata_records(self) -> tuple[_contracts.ProviderCallMetadata, ...]:
        """Return provider-neutral metadata captured for this runtime."""

        return tuple(self._metadata)

    @property
    def sdk_max_retries(self) -> int:
        """Expose only the configured retry count, never the SDK client."""

        return self._client.max_retries

    @property
    def retry_count(self) -> int:
        """Return transport retries observed without exposing SDK state."""

        return sum(
            max(0, len(item.provider_attempt_ids) - 1) for item in self._metadata
        )

    def execute(
        self, request: _contracts.ModelCallRequest
    ) -> _contracts.ModelCallResult:
        if type(request) is not _contracts.ModelCallRequest:
            raise TypeError("request must be an exact ModelCallRequest")
        parameters = _parameters_for(
            request.execution_profile, request.identity.model_call_id
        )
        call_id = request.identity.model_call_id.value
        attempts = (
            _contracts.ProviderAttemptId(f"{call_id}-attempt-1"),
            _contracts.ProviderAttemptId(f"{call_id}-attempt-2"),
        )
        try:
            result = execute_openai_responses_with_transport_retry(
                client=self._client,
                request=request,
                parameters=parameters,
                provider_attempt_ids=attempts,
                overall_deadline_monotonic=_monotonic() + parameters.timeout_seconds,
                fallback_retry_delay_seconds=_FALLBACK_RETRY_DELAY_SECONDS,
            )
        except _contracts.ModelRuntimeError as error:
            if error.provider_metadata is not None:
                self._metadata.append(error.provider_metadata)
            raise
        self._metadata.append(result.provider_metadata)
        return result

    def close(self) -> None:
        """Close the SDK client owned by this adapter."""

        self._client.close()


def create_openai_responses_runtime(
    *, credential_ref: str = OPENAI_PRIMARY_CREDENTIAL_REF
) -> OpenAIResponsesModelRuntime:
    """Resolve ``openai_primary`` and build one exact sync OpenAI client.

    Secret resolution deliberately stays inside this infrastructure factory.
    The value is never returned, logged or included in the provider-neutral
    runtime object graph.
    """

    if credential_ref != OPENAI_PRIMARY_CREDENTIAL_REF:
        raise ValueError("unsupported credential reference; expected openai_primary")
    secret = _os.environ.get(_OPENAI_API_KEY_ENVIRONMENT_NAME, "")
    if type(secret) is not str or not secret.strip():
        raise OpenAIResponsesConfigurationError(_CONFIGURATION_MESSAGE)
    try:
        client = _openai.OpenAI(api_key=secret, max_retries=0)
    except Exception as error:
        del error
        raise OpenAIResponsesConfigurationError(_CONFIGURATION_MESSAGE) from None
    if type(client) is not _openai.OpenAI or client.max_retries != 0:
        if type(client) is _openai.OpenAI:
            client.close()
        raise OpenAIResponsesConfigurationError(_CONFIGURATION_MESSAGE)
    return OpenAIResponsesModelRuntime(client=client)


__all__ = [
    "OPENAI_PRIMARY_CREDENTIAL_REF",
    "OPENAI_RESPONSES_PROFILE_CATALOG",
    "OpenAIResponsesConfigurationError",
    "OpenAIResponsesModelRuntime",
    "create_openai_responses_runtime",
]
