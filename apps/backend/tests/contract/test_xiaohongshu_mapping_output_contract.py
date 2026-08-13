"""Contract tests for the private Xiaohongshu mapping output seam."""

from __future__ import annotations

import inspect
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    StructuredOutputSpec,
)
from ai_ecommerce_agent.modules.xiaohongshu_adapter.application.skills import (
    xiaohongshu_brief_mapping as _mapping,
)

pytestmark = pytest.mark.contract


def test_private_facade_and_catalogs_are_exact() -> None:
    assert _mapping.__all__ == [
        "XiaohongshuNoteFormat",
        "XiaohongshuBriefStageDecision",
        "xiaohongshu_brief_candidate_output_spec",
    ]
    assert [getattr(_mapping, name) for name in _mapping.__all__] == [
        _mapping.XiaohongshuNoteFormat,
        _mapping.XiaohongshuBriefStageDecision,
        _mapping.xiaohongshu_brief_candidate_output_spec,
    ]
    assert [member.value for member in _mapping.XiaohongshuNoteFormat] == [
        "image_text_note_brief",
        "video_note_brief",
    ]
    assert [member.value for member in _mapping.XiaohongshuBriefStageDecision] == [
        "valid",
        "valid_with_limitations",
        "brief_change_required",
        "platform_policy_update_required",
        "waiting_input",
        "paused",
        "failed",
    ]


def test_spec_facade_is_exact_synchronous_and_typed() -> None:
    function = _mapping.xiaohongshu_brief_candidate_output_spec
    assert list(inspect.signature(function).parameters) == []
    assert not inspect.iscoroutinefunction(function)
    assert get_type_hints(function) == {"return": StructuredOutputSpec}
    first = function()
    second = function()
    assert type(first) is StructuredOutputSpec
    assert first == second
    assert first is not second
    assert first.output_schema_id == "xiaohongshu_brief_candidate"
    assert first.output_schema_version == "v1"
    first_mapping = cast(dict[str, object], first.schema.to_mapping())
    second_mapping = cast(dict[str, object], second.schema.to_mapping())
    cast(dict[str, object], first_mapping["properties"])["extra"] = {}
    assert "extra" not in cast(dict[str, object], second_mapping["properties"])


def test_schema_has_exact_root_groups_and_context_order() -> None:
    schema = cast(
        dict[str, object],
        _mapping.xiaohongshu_brief_candidate_output_spec().schema.to_mapping(),
    )
    properties = cast(dict[str, object], schema["properties"])
    assert list(properties) == [
        "workflow_and_version_context",
        "xiaohongshu_brief_candidate",
    ]
    assert schema["required"] == [
        "xiaohongshu_brief_candidate",
        "workflow_and_version_context",
    ]
    candidate = cast(dict[str, object], properties["xiaohongshu_brief_candidate"])
    assert list(cast(dict[str, object], candidate["properties"])) == [
        "creative_structure_directions",
        "discovery_and_action_directions",
        "evidence_and_platform_constraints",
        "note_format_and_content_mode",
        "platform_and_campaign_context",
    ]
    assert candidate["required"] == [
        "platform_and_campaign_context",
        "note_format_and_content_mode",
        "creative_structure_directions",
        "discovery_and_action_directions",
        "evidence_and_platform_constraints",
    ]
    context = cast(dict[str, object], properties["workflow_and_version_context"])
    assert list(cast(dict[str, object], context["properties"])) == [
        "approved_strategy_version_id",
        "facts_version_id",
        "input_limitations",
        "marketing_brief_version_id",
        "platform_policy_snapshot_id",
        "platform_policy_version",
        "stage_decision",
    ]
    assert context["required"] == [
        "marketing_brief_version_id",
        "approved_strategy_version_id",
        "facts_version_id",
        "platform_policy_snapshot_id",
        "platform_policy_version",
        "input_limitations",
        "stage_decision",
    ]
    for mapping in (schema, candidate, context):
        assert mapping["additionalProperties"] is False


def test_schema_is_structural_only() -> None:
    serialized = repr(
        _mapping.xiaohongshu_brief_candidate_output_spec().schema.to_mapping()
    )
    for forbidden in (
        "final_title",
        "final_body",
        "hashtags",
        "cover_copy",
        "Storyboard",
        "oneOf",
        "minItems",
        "maxItems",
        "ResourceReference",
    ):
        assert forbidden not in serialized
    assert "'if'" not in serialized
    assert "'then'" not in serialized
