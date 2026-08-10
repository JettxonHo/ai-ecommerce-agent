"""Behavioral tests for deterministic OpenAI Responses request preparation."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from typing import Any, cast

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelExecutionProfile,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    OpenAIReasoningEffort,
    OpenAIResponsesCallParameters,
    PreparedOpenAIResponsesCall,
    prepare_openai_responses_call,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit


_PROFILE = ModelExecutionProfile("profile-1", "v1")
_CALL_ID = ModelCallId("call-1")


class _RequestSubclass(ModelCallRequest):
    pass


class _ParametersSubclass(OpenAIResponsesCallParameters):
    pass


class _IntSubclass(int):
    pass


class _TextSubclass(str):
    pass


def _context() -> StructuredContent:
    return StructuredContent.from_mapping(
        {
            "z": "中文",
            "a": ["first", {"z": 2, "a": 1}],
            "nested": {"b": True, "a": None},
        }
    )


def _schema() -> StructuredContent:
    return StructuredContent.from_mapping(
        {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
            "additionalProperties": False,
        }
    )


def _request(
    *,
    profile: ModelExecutionProfile = _PROFILE,
    context: StructuredContent | None = None,
    schema: StructuredContent | None = None,
) -> ModelCallRequest:
    return ModelCallRequest(
        ModelCallIdentity(_CALL_ID),
        "instruction-marker",
        context or _context(),
        StructuredOutputSpec("schema-1", "v1", schema or _schema()),
        profile,
        ModelCallContractVersions("prompt-1", "v1", "skill-1", "domain-1", "context-1"),
    )


def _parameters(
    *,
    profile: ModelExecutionProfile = _PROFILE,
    reasoning_effort: OpenAIReasoningEffort = OpenAIReasoningEffort.MEDIUM,
    max_output_tokens: int = 128,
    timeout_seconds: int = 30,
) -> OpenAIResponsesCallParameters:
    return OpenAIResponsesCallParameters(
        profile, reasoning_effort, max_output_tokens, timeout_seconds
    )


def _prepare(
    request: ModelCallRequest | object = None,
    parameters: OpenAIResponsesCallParameters | object = None,
) -> PreparedOpenAIResponsesCall:
    return prepare_openai_responses_call(
        request=cast(ModelCallRequest, request if request is not None else _request()),
        parameters=cast(
            OpenAIResponsesCallParameters,
            parameters if parameters is not None else _parameters(),
        ),
    )


def test_request_body_is_exact_and_context_json_is_canonical() -> None:
    request = _request()
    result = _prepare(request)
    expected_context = json.dumps(
        request.context.to_mapping(),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert result.request_body.to_mapping() == {
        "model": "gpt-5.6-terra",
        "store": False,
        "instructions": "instruction-marker",
        "input": expected_context,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "schema-1",
                "schema": request.structured_output.schema.to_mapping(),
                "strict": True,
            }
        },
        "reasoning": {"effort": "medium"},
        "max_output_tokens": 128,
    }
    assert result.timeout_seconds == 30
    assert set(result.request_body.to_mapping()) == {
        "model",
        "store",
        "instructions",
        "input",
        "text",
        "reasoning",
        "max_output_tokens",
    }


def test_projection_is_deeply_immutable_detached_and_deterministic() -> None:
    request = _request()
    before_context = request.context.to_mapping()
    before_schema = request.structured_output.schema.to_mapping()
    first = _prepare(request)
    second = _prepare(request)
    assert first == second
    assert first is not second
    assert first.request_body is not second.request_body
    assert request.context.to_mapping() == before_context
    assert request.structured_output.schema.to_mapping() == before_schema

    detached = cast(dict[str, object], first.request_body.to_mapping())
    text = cast(dict[str, object], detached["text"])
    fmt = cast(dict[str, object], text["format"])
    detached_schema = cast(dict[str, object], fmt["schema"])
    detached_schema["properties"] = {}
    detached["instructions"] = "mutated"
    assert first.request_body.to_mapping()["instructions"] == "instruction-marker"
    assert request.structured_output.schema.to_mapping() == before_schema

    with pytest.raises(FrozenInstanceError):
        first.timeout_seconds = 0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del first.request_body  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("reasoning_effort", "medium"),
        ("reasoning_effort", _TextSubclass("medium")),
        ("max_output_tokens", True),
        ("max_output_tokens", 0),
        ("max_output_tokens", -1),
        ("max_output_tokens", 1.0),
        ("max_output_tokens", _IntSubclass(1)),
        ("timeout_seconds", True),
        ("timeout_seconds", 0),
        ("timeout_seconds", -1),
        ("timeout_seconds", 1.0),
        ("timeout_seconds", _IntSubclass(1)),
    ],
)
def test_parameter_fields_have_strict_types_and_positive_bounds(
    field: str, value: object
) -> None:
    parameters = _parameters()
    object.__setattr__(parameters, field, value)
    with pytest.raises((TypeError, ValueError)):
        _prepare(parameters=parameters)


def test_request_and_parameter_dto_types_are_exact() -> None:
    request = _request()
    parameters = _parameters()
    subclass_request = _RequestSubclass(
        request.identity,
        request.instructions,
        request.context,
        request.structured_output,
        request.execution_profile,
        request.contract_versions,
    )
    subclass_parameters = _ParametersSubclass(
        parameters.execution_profile,
        parameters.reasoning_effort,
        parameters.max_output_tokens,
        parameters.timeout_seconds,
    )
    with pytest.raises(TypeError):
        _prepare(request=subclass_request)
    with pytest.raises(TypeError):
        _prepare(parameters=subclass_parameters)


def test_profile_mismatch_is_a_safe_error_with_original_call_identity() -> None:
    request = _request()
    parameters = _parameters(profile=ModelExecutionProfile("other", "v1"))
    with pytest.raises(ModelRuntimeError) as caught:
        _prepare(request, parameters)
    error = caught.value
    assert error.category is ModelRuntimeErrorCategory.INVALID_REQUEST
    assert error.retryability is False
    assert error.model_call_id is _CALL_ID
    assert error.provider_metadata is None
    assert "profile" in error.message


def test_helper_is_called_before_projection_and_errors_keep_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
        request_preparation,
    )

    module = cast(Any, request_preparation)
    events: list[str] = []
    original = module._ensure_schema_compatible

    def helper(**kwargs: object) -> None:
        events.append("helper")
        original(**kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(module, "_ensure_schema_compatible", helper)
    _prepare()
    assert events == ["helper"]

    expected = ModelRuntimeError(
        ModelRuntimeErrorCategory.INVALID_REQUEST,
        "sentinel",
        False,
        _CALL_ID,
        None,
    )

    def raise_expected(**kwargs: object) -> None:
        raise expected

    monkeypatch.setattr(module, "_ensure_schema_compatible", raise_expected)
    with pytest.raises(ModelRuntimeError) as caught:
        _prepare()
    assert caught.value is expected

    unexpected = RuntimeError("unexpected")

    def raise_unexpected(**kwargs: object) -> None:
        raise unexpected

    monkeypatch.setattr(module, "_ensure_schema_compatible", raise_unexpected)
    with pytest.raises(RuntimeError) as caught:
        _prepare()
    assert caught.value is unexpected
