"""Contract tests for the private OpenAI Responses transport attempt."""

from __future__ import annotations

from dataclasses import fields
from inspect import Parameter, signature
from typing import get_type_hints

import openai
import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelCallResult,
    ProviderAttemptId,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _execution,
    request_preparation,
)

pytestmark = pytest.mark.contract


def test_private_executor_signature_and_hints_are_exact() -> None:
    function = _execution.execute_openai_responses_attempt
    assert list(signature(function).parameters) == [
        "client",
        "request",
        "parameters",
        "provider_attempt_ids",
    ]
    assert all(
        item.kind is Parameter.KEYWORD_ONLY
        for item in signature(function).parameters.values()
    )
    assert get_type_hints(function) == {
        "client": openai.OpenAI,
        "request": ModelCallRequest,
        "parameters": request_preparation.OpenAIResponsesCallParameters,
        "provider_attempt_ids": tuple[ProviderAttemptId, ...],
        "return": ModelCallResult,
    }


def test_executor_module_has_no_public_facade_or_new_contract_types() -> None:
    from ai_ecommerce_agent.platform.model_runtime import openai_responses

    assert openai_responses.__all__ == [
        "OpenAIReasoningEffort",
        "OpenAIResponsesCallParameters",
        "PreparedOpenAIResponsesCall",
        "prepare_openai_responses_call",
    ]
    assert "execute_openai_responses_attempt" not in openai_responses.__all__
    assert not hasattr(openai_responses, "execute_openai_responses_attempt")
    assert [
        field.name
        for field in fields(request_preparation.OpenAIResponsesCallParameters)
    ] == [
        "execution_profile",
        "reasoning_effort",
        "max_output_tokens",
        "timeout_seconds",
    ]
