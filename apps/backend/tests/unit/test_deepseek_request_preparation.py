"""Tests-first contract for the private DeepSeek request projection."""

from __future__ import annotations

import json
from typing import cast

import pytest

import ai_ecommerce_agent.platform.model_runtime as _runtime_package
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelExecutionProfile,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._request_preparation import (
    DeepSeekCallParameters,
    DeepSeekReasoningEffort,
    prepare_deepseek_call,
)
from ai_ecommerce_agent.platform.model_runtime.deepseek._runtime import (
    DEEPSEEK_PROFILE_CATALOG,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

_runtime_package.__dict__.pop("deepseek", None)

pytestmark = pytest.mark.unit

_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "string"},
        "nested": {
            "type": "object",
            "properties": {
                "flag": {"type": "boolean"},
                "kind": {"type": "string", "enum": ["alpha", "beta"]},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["flag", "kind", "tags"],
            "additionalProperties": False,
        },
    },
    "required": ["value", "nested"],
    "additionalProperties": False,
}


def _request(profile_id: str = "product_intake_v1") -> ModelCallRequest:
    return ModelCallRequest(
        identity=ModelCallIdentity(ModelCallId("deepseek-call-1")),
        instructions="Return JSON matching the project schema.",
        context=StructuredContent.from_mapping(
            {"z": "中文", "primary_input": "fixture", "upstream": None}
        ),
        structured_output=StructuredOutputSpec(
            output_schema_id="fixture_schema",
            output_schema_version="v1",
            schema=StructuredContent.from_mapping(_SCHEMA),
        ),
        execution_profile=ModelExecutionProfile(profile_id, "v1"),
        contract_versions=ModelCallContractVersions(
            "prompt-1", "v1", "skill-1", "domain-1", "context-1"
        ),
    )


def _parameters(
    profile_id: str = "product_intake_v1",
) -> DeepSeekCallParameters:
    return DeepSeekCallParameters(
        execution_profile=ModelExecutionProfile(profile_id, "v1"),
        reasoning_effort=DeepSeekReasoningEffort.HIGH,
        max_output_tokens=8192,
        timeout_seconds=120,
    )


def test_request_projection_is_exact_deepseek_chat_json_mode() -> None:
    request = _request()
    prepared = prepare_deepseek_call(request=request, parameters=_parameters())
    context_json = json.dumps(
        request.context.to_mapping(),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    body = prepared.request_body.to_mapping()
    schema_json = json.dumps(
        _SCHEMA,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    assert body == {
        "model": "deepseek-v4-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return JSON matching the project schema.\n"
                    f"Required output JSON Schema: {schema_json}"
                ),
            },
            {"role": "user", "content": context_json},
        ],
        "response_format": {"type": "json_object"},
        "extra_body": {"thinking": {"type": "enabled"}},
        "reasoning_effort": "high",
        "stream": False,
        "max_tokens": 8192,
    }
    assert prepared.timeout_seconds == 120
    messages = cast(list[dict[str, object]], body["messages"])
    system_instruction = cast(str, messages[0]["content"])
    assert '"enum":["alpha","beta"]' in system_instruction
    assert '"items":{"type":"string"}' in system_instruction
    assert '"required":["flag","kind","tags"]' in system_instruction
    assert '"additionalProperties":false' in system_instruction
    assert "json_schema" not in json.dumps(body, ensure_ascii=False)
    assert "strict" not in json.dumps(body, ensure_ascii=False)


def test_projection_has_no_tools_files_urls_history_temperature_or_sampling() -> None:
    body = prepare_deepseek_call(
        request=_request(), parameters=_parameters()
    ).request_body.to_mapping()
    assert set(body) == {
        "model",
        "messages",
        "response_format",
        "extra_body",
        "reasoning_effort",
        "stream",
        "max_tokens",
    }
    assert all(
        key not in body
        for key in (
            "tools",
            "functions",
            "files",
            "previous_response_id",
            "store",
            "temperature",
            "top_p",
        )
    )


def test_profile_catalog_preserves_deepseek_order_and_exact_bounds() -> None:
    assert [
        item.execution_profile.execution_profile_id for item in DEEPSEEK_PROFILE_CATALOG
    ] == [
        "product_intake_v1",
        "customer_insight_v1",
        "product_positioning_v1",
        "marketing_brief_v1",
        "xiaohongshu_mapping_v1",
    ]
    assert [
        item.execution_profile.execution_profile_version
        for item in DEEPSEEK_PROFILE_CATALOG
    ] == ["v1", "v1", "v1", "v1", "v2"]
    assert [item.reasoning_effort.value for item in DEEPSEEK_PROFILE_CATALOG] == [
        "high",
        "high",
        "high",
        "high",
        "high",
    ]
    assert [item.max_output_tokens for item in DEEPSEEK_PROFILE_CATALOG] == [
        8192,
        12288,
        16384,
        16384,
        16384,
    ]
    assert [item.timeout_seconds for item in DEEPSEEK_PROFILE_CATALOG] == [
        120,
        180,
        240,
        180,
        240,
    ]
