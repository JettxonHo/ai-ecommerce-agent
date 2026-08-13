"""Contract tests for the private Qwen Token Plan adapter seam."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from inspect import Parameter, signature
from typing import get_type_hints

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelCallResult,
    ProviderAttemptId,
)
from ai_ecommerce_agent.platform.model_runtime.qwen_token_plan import (
    _request_preparation,
    _response_mapping,
)

pytestmark = pytest.mark.contract


def test_request_contracts_are_frozen_and_private() -> None:
    assert [
        field.name for field in fields(_request_preparation.QwenTokenPlanCallParameters)
    ] == [
        "execution_profile",
        "reasoning_effort",
        "max_output_tokens",
        "timeout_seconds",
    ]
    assert [
        field.name for field in fields(_request_preparation.PreparedQwenTokenPlanCall)
    ] == [
        "request_body",
        "timeout_seconds",
    ]
    for cls in (
        _request_preparation.QwenTokenPlanCallParameters,
        _request_preparation.PreparedQwenTokenPlanCall,
    ):
        assert is_dataclass(cls)
        assert cls.__dataclass_params__.frozen is True  # type: ignore[attr-defined]
        assert "__dict__" not in cls.__slots__  # type: ignore[attr-defined]


def test_request_preparation_signature_is_keyword_only() -> None:
    function = _request_preparation.prepare_qwen_token_plan_call
    parameters = signature(function).parameters
    assert list(parameters) == ["request", "parameters"]
    assert all(item.kind is Parameter.KEYWORD_ONLY for item in parameters.values())
    assert get_type_hints(function) == {
        "request": ModelCallRequest,
        "parameters": _request_preparation.QwenTokenPlanCallParameters,
        "return": _request_preparation.PreparedQwenTokenPlanCall,
    }


def test_response_mapping_signature_keeps_provider_types_private() -> None:
    function = _response_mapping.map_qwen_token_plan_response
    parameters = signature(function).parameters
    assert list(parameters) == [
        "request",
        "response",
        "provider_attempt_ids",
        "latency_ms",
    ]
    assert all(item.kind is Parameter.KEYWORD_ONLY for item in parameters.values())
    hints = get_type_hints(function)
    assert hints["request"] is ModelCallRequest
    assert hints["provider_attempt_ids"] == tuple[ProviderAttemptId, ...]
    assert hints["latency_ms"] is int
    assert hints["return"] is ModelCallResult
