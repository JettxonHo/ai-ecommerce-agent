"""Contract tests for the public OpenAI Responses request projection."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import StrEnum
from inspect import Parameter, signature
from typing import get_type_hints

import pytest

import ai_ecommerce_agent.platform.model_runtime as _runtime_package
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelExecutionProfile,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    OpenAIReasoningEffort,
    OpenAIResponsesCallParameters,
    PreparedOpenAIResponsesCall,
    prepare_openai_responses_call,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

_runtime_package.__dict__.pop("openai_responses", None)

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = [
    "OpenAIReasoningEffort",
    "OpenAIResponsesCallParameters",
    "PreparedOpenAIResponsesCall",
    "prepare_openai_responses_call",
]


def test_public_facade_has_exact_order_and_identity() -> None:
    from ai_ecommerce_agent.platform.model_runtime import openai_responses

    assert openai_responses.__all__ == _EXPECTED_PUBLIC
    assert [getattr(openai_responses, name) for name in _EXPECTED_PUBLIC] == [
        OpenAIReasoningEffort,
        OpenAIResponsesCallParameters,
        PreparedOpenAIResponsesCall,
        prepare_openai_responses_call,
    ]
    public_names = {
        name
        for name in openai_responses.__dict__
        if not name.startswith("_") and name != "annotations"
    }
    assert public_names == {*_EXPECTED_PUBLIC, "request_preparation"}


def test_enum_and_dataclass_contracts_are_exact() -> None:
    assert issubclass(OpenAIReasoningEffort, StrEnum)
    assert [(member.name, member.value) for member in OpenAIReasoningEffort] == [
        ("LOW", "low"),
        ("MEDIUM", "medium"),
        ("HIGH", "high"),
    ]
    assert [field.name for field in fields(OpenAIResponsesCallParameters)] == [
        "execution_profile",
        "reasoning_effort",
        "max_output_tokens",
        "timeout_seconds",
    ]
    assert [field.name for field in fields(PreparedOpenAIResponsesCall)] == [
        "request_body",
        "timeout_seconds",
    ]
    for cls in (OpenAIResponsesCallParameters, PreparedOpenAIResponsesCall):
        assert is_dataclass(cls)
        assert cls.__dataclass_params__.frozen is True  # type: ignore[attr-defined]
        assert "__dict__" not in cls.__slots__  # type: ignore[attr-defined]

    assert get_type_hints(OpenAIResponsesCallParameters) == {
        "execution_profile": ModelExecutionProfile,
        "reasoning_effort": OpenAIReasoningEffort,
        "max_output_tokens": int,
        "timeout_seconds": int,
    }
    assert get_type_hints(PreparedOpenAIResponsesCall) == {
        "request_body": StructuredContent,
        "timeout_seconds": int,
    }


def test_prepare_signature_and_hints_are_exact() -> None:
    parameters = signature(prepare_openai_responses_call).parameters
    assert list(parameters) == ["request", "parameters"]
    assert all(item.kind is Parameter.KEYWORD_ONLY for item in parameters.values())
    assert get_type_hints(prepare_openai_responses_call) == {
        "request": ModelCallRequest,
        "parameters": OpenAIResponsesCallParameters,
        "return": PreparedOpenAIResponsesCall,
    }
