"""Pure preparation of a Qwen Token Plan Chat Completions request."""

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


class QwenReasoningEffort(_StrEnum):
    """The provider-neutral profile reasoning labels retained by the adapter."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@_dataclass(frozen=True, slots=True)
class QwenTokenPlanCallParameters:
    execution_profile: _ModelExecutionProfile
    reasoning_effort: QwenReasoningEffort
    max_output_tokens: int
    timeout_seconds: int


@_dataclass(frozen=True, slots=True)
class PreparedQwenTokenPlanCall:
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
    request: _ModelCallRequest,
    parameters: QwenTokenPlanCallParameters,
) -> None:
    if type(request) is not _ModelCallRequest:
        raise TypeError("request must be a ModelCallRequest")
    if type(parameters) is not QwenTokenPlanCallParameters:
        raise TypeError("parameters must be QwenTokenPlanCallParameters")
    if type(parameters.execution_profile) is not _ModelExecutionProfile:
        raise TypeError("execution_profile must be a ModelExecutionProfile")
    if type(parameters.reasoning_effort) is not QwenReasoningEffort:
        raise TypeError("reasoning_effort must be a QwenReasoningEffort")
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


def prepare_qwen_token_plan_call(
    *,
    request: _ModelCallRequest,
    parameters: QwenTokenPlanCallParameters,
) -> PreparedQwenTokenPlanCall:
    """Prepare a detached, deterministic Chat Completions projection.

    Qwen's Chat Completions surface does not accept the Responses ``text``
    wrapper.  The project-owned schema is therefore placed in the provider's
    ``json_schema`` response format while all context remains deterministic
    JSON.  Profile reasoning labels stay provider-neutral; no unsupported
    OpenAI reasoning parameter is sent to Qwen.
    """

    _validate(request, parameters)
    context_json = _json.dumps(
        request.context.to_mapping(),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    body = _StructuredContent.from_mapping(
        {
            "model": "qwen3.8-max",
            "messages": [
                {"role": "system", "content": request.instructions},
                {"role": "user", "content": context_json},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": request.structured_output.output_schema_id,
                    "schema": request.structured_output.schema.to_mapping(),
                    "strict": True,
                },
            },
            "stream": False,
            "max_completion_tokens": parameters.max_output_tokens,
        }
    )
    return PreparedQwenTokenPlanCall(body, parameters.timeout_seconds)


__all__ = [
    "PreparedQwenTokenPlanCall",
    "QwenReasoningEffort",
    "QwenTokenPlanCallParameters",
    "prepare_qwen_token_plan_call",
]
