"""Pure preparation of a DeepSeek Chat Completions request."""

from __future__ import annotations

import json as _json
from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass
from enum import StrEnum as _StrEnum
from typing import cast as _cast

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

_MODEL_ID = "deepseek-v4-pro"


class DeepSeekReasoningEffort(_StrEnum):
    """The fixed reasoning label sent to the DeepSeek API."""

    HIGH = "high"


@_dataclass(frozen=True, slots=True)
class DeepSeekCallParameters:
    execution_profile: _ModelExecutionProfile
    reasoning_effort: DeepSeekReasoningEffort
    max_output_tokens: int
    timeout_seconds: int


@_dataclass(frozen=True, slots=True)
class PreparedDeepSeekCall:
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
    parameters: DeepSeekCallParameters,
) -> None:
    if type(request) is not _ModelCallRequest:
        raise TypeError("request must be a ModelCallRequest")
    if type(parameters) is not DeepSeekCallParameters:
        raise TypeError("parameters must be DeepSeekCallParameters")
    if type(parameters.execution_profile) is not _ModelExecutionProfile:
        raise TypeError("execution_profile must be a ModelExecutionProfile")
    if type(parameters.reasoning_effort) is not DeepSeekReasoningEffort:
        raise TypeError("reasoning_effort must be a DeepSeekReasoningEffort")
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


def _schema_type(value: object) -> str:
    if isinstance(value, _Mapping):
        mapping = _cast(_Mapping[str, object], value)
        schema_type: object = mapping.get("type")
        if type(schema_type) is str and schema_type.strip():
            return schema_type
        if type(schema_type) is list and schema_type:
            items = _cast(list[object], schema_type)
            values: list[str] = [item for item in items if type(item) is str]
            if len(values) == len(items):
                return "|".join(values)
    return "unknown"


def _field_shape(spec: object) -> str:
    if type(spec) is not _StructuredContent:
        raise TypeError("structured output schema must be StructuredContent")
    schema = spec.to_mapping()
    properties_value = schema.get("properties")
    properties = (
        _cast(_Mapping[str, object], properties_value)
        if isinstance(properties_value, _Mapping)
        else None
    )
    if not isinstance(properties, _Mapping):
        return "{}"
    required_value = schema.get("required")
    required_names = (
        frozenset(
            item for item in _cast(list[object], required_value) if type(item) is str
        )
        if type(required_value) is list
        else frozenset[str]()
    )
    shape = {
        str(name): {
            "required": name in required_names,
            "type": _schema_type(value),
        }
        for name, value in properties.items()
        if type(name) is str
    }
    return _json.dumps(
        shape,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def prepare_deepseek_call(
    *,
    request: _ModelCallRequest,
    parameters: DeepSeekCallParameters,
) -> PreparedDeepSeekCall:
    """Prepare a detached, deterministic DeepSeek JSON-mode call."""

    _validate(request, parameters)
    context_json = _json.dumps(
        request.context.to_mapping(),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    instruction = (
        f"{request.instructions}\nField shape (JSON): "
        f"{_field_shape(request.structured_output.schema)}"
    )
    body = _StructuredContent.from_mapping(
        {
            "model": _MODEL_ID,
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": context_json},
            ],
            "response_format": {"type": "json_object"},
            "extra_body": {"thinking": {"type": "enabled"}},
            "reasoning_effort": parameters.reasoning_effort.value,
            "stream": False,
            "max_tokens": parameters.max_output_tokens,
        }
    )
    return PreparedDeepSeekCall(body, parameters.timeout_seconds)


__all__ = [
    "DeepSeekCallParameters",
    "DeepSeekReasoningEffort",
    "PreparedDeepSeekCall",
    "prepare_deepseek_call",
]
