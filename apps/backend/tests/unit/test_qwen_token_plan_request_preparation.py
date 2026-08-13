"""Behavioral tests for deterministic Qwen Token Plan request preparation."""

from __future__ import annotations

import json

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelExecutionProfile,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.qwen_token_plan._request_preparation import (  # noqa: E501
    QwenReasoningEffort,
    QwenTokenPlanCallParameters,
    prepare_qwen_token_plan_call,
)
from ai_ecommerce_agent.platform.model_runtime.qwen_token_plan._runtime import (
    QWEN_TOKEN_PLAN_PROFILE_CATALOG,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit


def _request(profile_id: str = "product_intake_v1") -> ModelCallRequest:
    return ModelCallRequest(
        identity=ModelCallIdentity(ModelCallId("qwen-call-1")),
        instructions="Return JSON matching the project schema.",
        context=StructuredContent.from_mapping(
            {"z": "中文", "primary_input": "fixture", "upstream": None}
        ),
        structured_output=StructuredOutputSpec(
            output_schema_id="fixture_schema",
            output_schema_version="v1",
            schema=StructuredContent.from_mapping(
                {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                }
            ),
        ),
        execution_profile=ModelExecutionProfile(profile_id, "v1"),
        contract_versions=ModelCallContractVersions(
            "prompt-1", "v1", "skill-1", "domain-1", "context-1"
        ),
    )


def _parameters(
    profile_id: str = "product_intake_v1",
) -> QwenTokenPlanCallParameters:
    return QwenTokenPlanCallParameters(
        execution_profile=ModelExecutionProfile(profile_id, "v1"),
        reasoning_effort=QwenReasoningEffort.LOW,
        max_output_tokens=8192,
        timeout_seconds=120,
    )


def test_request_projection_is_exact_and_canonical() -> None:
    request = _request()
    prepared = prepare_qwen_token_plan_call(
        request=request,
        parameters=_parameters(),
    )
    context_json = json.dumps(
        request.context.to_mapping(),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert prepared.request_body.to_mapping() == {
        "model": "qwen3.8-max",
        "messages": [
            {"role": "system", "content": request.instructions},
            {"role": "user", "content": context_json},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "fixture_schema",
                "schema": request.structured_output.schema.to_mapping(),
                "strict": True,
            },
        },
        "stream": False,
        "max_completion_tokens": 8192,
    }
    assert prepared.timeout_seconds == 120


def test_profile_catalog_preserves_the_five_stage_order_and_bounds() -> None:
    assert [
        item.execution_profile.execution_profile_id
        for item in QWEN_TOKEN_PLAN_PROFILE_CATALOG
    ] == [
        "product_intake_v1",
        "customer_insight_v1",
        "product_positioning_v1",
        "marketing_brief_v1",
        "xiaohongshu_mapping_v1",
    ]
    assert [
        item.reasoning_effort.value for item in QWEN_TOKEN_PLAN_PROFILE_CATALOG
    ] == [
        "low",
        "medium",
        "high",
        "medium",
        "low",
    ]
    assert [item.max_output_tokens for item in QWEN_TOKEN_PLAN_PROFILE_CATALOG] == [
        8192,
        12288,
        16384,
        16384,
        12288,
    ]
    assert [item.timeout_seconds for item in QWEN_TOKEN_PLAN_PROFILE_CATALOG] == [
        120,
        180,
        240,
        180,
        120,
    ]


def test_projection_contains_no_tools_files_urls_or_history() -> None:
    body = prepare_qwen_token_plan_call(
        request=_request(),
        parameters=_parameters(),
    ).request_body.to_mapping()
    assert set(body) == {
        "model",
        "messages",
        "response_format",
        "stream",
        "max_completion_tokens",
    }
    assert all(
        key not in body
        for key in ("tools", "functions", "files", "previous_response_id", "store")
    )
