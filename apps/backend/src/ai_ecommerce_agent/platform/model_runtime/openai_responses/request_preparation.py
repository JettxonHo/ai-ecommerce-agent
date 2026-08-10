"""Pure preparation of an OpenAI Responses request projection."""

from __future__ import annotations

import json as _json
from dataclasses import dataclass as _dataclass
from enum import StrEnum as _StrEnum

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId as _ModelCallId,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest as _ModelCallRequest,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelExecutionProfile as _ModelExecutionProfile,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelRuntimeError as _ModelRuntimeError,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelRuntimeErrorCategory as _ErrorCategory,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent as _StructuredContent

from ._schema_compatibility import (
    ensure_openai_responses_schema_compatible as _ensure_schema_compatible,
)


class OpenAIReasoningEffort(_StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@_dataclass(frozen=True, slots=True)
class OpenAIResponsesCallParameters:
    execution_profile: _ModelExecutionProfile
    reasoning_effort: OpenAIReasoningEffort
    max_output_tokens: int
    timeout_seconds: int


@_dataclass(frozen=True, slots=True)
class PreparedOpenAIResponsesCall:
    request_body: _StructuredContent
    timeout_seconds: int


def _profile_mismatch(call_id: _ModelCallId) -> _ModelRuntimeError:
    return _ModelRuntimeError(
        _ErrorCategory.INVALID_REQUEST,
        "execution profile does not match request",
        False,
        call_id,
        None,
    )


def _validate(
    request: _ModelCallRequest, parameters: OpenAIResponsesCallParameters
) -> None:
    if type(request) is not _ModelCallRequest:
        raise TypeError("request must be a ModelCallRequest")
    if type(parameters) is not OpenAIResponsesCallParameters:
        raise TypeError("parameters must be OpenAIResponsesCallParameters")
    if type(parameters.execution_profile) is not _ModelExecutionProfile:
        raise TypeError("execution_profile must be a ModelExecutionProfile")
    if type(parameters.reasoning_effort) is not OpenAIReasoningEffort:
        raise TypeError("reasoning_effort must be an OpenAIReasoningEffort")
    for name, value in (
        ("max_output_tokens", parameters.max_output_tokens),
        ("timeout_seconds", parameters.timeout_seconds),
    ):
        if type(value) is not int:
            raise TypeError(f"{name} must be an int")
        if value <= 0:
            raise ValueError(f"{name} must be positive")
    if parameters.execution_profile != request.execution_profile:
        raise _profile_mismatch(request.identity.model_call_id)


def prepare_openai_responses_call(
    *,
    request: _ModelCallRequest,
    parameters: OpenAIResponsesCallParameters,
) -> PreparedOpenAIResponsesCall:
    """Prepare a deterministic, detached Responses request projection."""

    _validate(request, parameters)
    _ensure_schema_compatible(
        structured_output=request.structured_output,
        model_call_id=request.identity.model_call_id,
    )
    context_json = _json.dumps(
        request.context.to_mapping(),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    body = _StructuredContent.from_mapping(
        {
            "model": "gpt-5.6-terra",
            "store": False,
            "instructions": request.instructions,
            "input": context_json,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": request.structured_output.output_schema_id,
                    "schema": request.structured_output.schema.to_mapping(),
                    "strict": True,
                }
            },
            "reasoning": {"effort": parameters.reasoning_effort.value},
            "max_output_tokens": parameters.max_output_tokens,
        }
    )
    return PreparedOpenAIResponsesCall(body, parameters.timeout_seconds)
