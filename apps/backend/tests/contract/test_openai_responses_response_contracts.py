"""Contract tests for the private typed OpenAI Responses outcome mapper."""

from __future__ import annotations

from inspect import Parameter, signature
from typing import get_type_hints

import pytest
from openai.types.responses import Response

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallRequest,
    ModelCallResult,
    ProviderAttemptId,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _response_mapping,
)

pytestmark = pytest.mark.contract


def test_private_mapper_signature_and_public_facade_are_exact() -> None:
    mapper = _response_mapping.map_openai_responses_response
    assert list(signature(mapper).parameters) == [
        "request",
        "response",
        "provider_attempt_ids",
        "latency_ms",
    ]
    assert all(
        parameter.kind is Parameter.KEYWORD_ONLY
        for parameter in signature(mapper).parameters.values()
    )
    assert get_type_hints(mapper) == {
        "request": ModelCallRequest,
        "response": Response,
        "provider_attempt_ids": tuple[ProviderAttemptId, ...],
        "latency_ms": int,
        "return": ModelCallResult,
    }

    import ai_ecommerce_agent.platform.model_runtime.openai_responses as facade

    assert facade.__all__ == [
        "OpenAIReasoningEffort",
        "OpenAIResponsesCallParameters",
        "PreparedOpenAIResponsesCall",
        "prepare_openai_responses_call",
    ]
    assert not hasattr(facade, "map_openai_responses_response")
