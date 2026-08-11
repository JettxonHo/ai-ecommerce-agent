"""Provider-neutral Xiaohongshu Brief mapping candidate contract."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import cast

from ai_ecommerce_agent.application.model_runtime import StructuredOutputSpec
from ai_ecommerce_agent.shared_kernel.structured_content import StructuredContent

_NON_EMPTY = r".*\S.*"


class XiaohongshuNoteFormat(StrEnum):
    IMAGE_TEXT_NOTE_BRIEF = "image_text_note_brief"
    VIDEO_NOTE_BRIEF = "video_note_brief"


class XiaohongshuBriefStageDecision(StrEnum):
    VALID = "valid"
    VALID_WITH_LIMITATIONS = "valid_with_limitations"
    BRIEF_CHANGE_REQUIRED = "brief_change_required"
    PLATFORM_POLICY_UPDATE_REQUIRED = "platform_policy_update_required"
    WAITING_INPUT = "waiting_input"
    PAUSED = "paused"
    FAILED = "failed"


def _string(*, nullable: bool = False) -> dict[str, object]:
    return {
        "type": ["string", "null"] if nullable else "string",
        "pattern": _NON_EMPTY,
    }


def _strings() -> dict[str, object]:
    return {"type": "array", "items": _string()}


def _enum(values: tuple[str, ...]) -> dict[str, object]:
    return {"type": "string", "enum": list(values)}


def _object(
    properties: Mapping[str, object],
    required: tuple[str, ...],
    *,
    nullable: bool = False,
) -> dict[str, object]:
    return {
        "type": ["object", "null"] if nullable else "object",
        "properties": dict(properties),
        "required": list(required),
        "additionalProperties": False,
    }


def _objects(item: Mapping[str, object]) -> dict[str, object]:
    return {"type": "array", "items": dict(item)}


def _title_direction() -> dict[str, object]:
    properties = {
        "title_direction": _string(),
        "user_question_or_tension": _string(),
        "primary_keyword": _string(),
        "message_focus": _string(),
        "proof_required": {"type": "boolean"},
        "risk_notes": _strings(),
    }
    return _object(properties, tuple(properties))


def _cover_direction() -> dict[str, object]:
    properties = {
        "cover_message_direction": _string(),
        "cover_visual_focus": _string(),
        "cover_information_priority": _string(),
        "cover_risk_notes": _strings(),
    }
    return _object(properties, tuple(properties))


def _narrative_module() -> dict[str, object]:
    properties = {
        "module_name": _string(),
        "content_direction": _string(),
        "proof_points": _strings(),
        "limitations": _strings(),
        "risk_notes": _strings(),
    }
    return _object(properties, tuple(properties))


def _content_angle_mapping() -> dict[str, object]:
    properties = {
        "source_content_angle_id": _string(),
        "xiaohongshu_angle": _string(),
        "note_format": _enum(tuple(item.value for item in XiaohongshuNoteFormat)),
        "content_mode": _string(),
        "narrative_structure": _strings(),
        "proof_points": _strings(),
        "customer_language": _strings(),
        "hypotheses": _strings(),
        "limitations": _strings(),
        "risk_notes": _strings(),
    }
    return _object(properties, tuple(properties))


def _proof_placement() -> dict[str, object]:
    properties = {
        "proof_point": _string(),
        "narrative_module": _string(),
        "placement_direction": _string(),
    }
    return _object(properties, tuple(properties))


def _customer_language() -> dict[str, object]:
    properties = {
        "fragment_id": _string(),
        "source_scope": _string(),
        "quote_type": _string(),
        "locator": _string(),
        "usage_direction": _string(),
    }
    return _object(properties, tuple(properties))


def _cta_mapping() -> dict[str, object]:
    properties = {
        "source_cta_objective": _string(),
        "cta_direction": _string(),
        "risk_notes": _strings(),
    }
    return _object(properties, tuple(properties))


def _platform_and_campaign_context() -> dict[str, object]:
    properties = {
        "platform": _string(),
        "account_type": _string(nullable=True),
        "content_relationship": _string(nullable=True),
        "commercial_context": _string(nullable=True),
        "campaign_objective": _string(nullable=True),
        "available_asset_types": _strings(),
    }
    return _object(properties, tuple(properties))


def _note_format_and_content_mode() -> dict[str, object]:
    properties = {
        "recommended_note_format": _enum(
            tuple(item.value for item in XiaohongshuNoteFormat)
        ),
        "primary_content_mode": _string(),
        "secondary_content_mode": _string(nullable=True),
        "platform_objective": _string(),
        "source_content_angle_ids": _strings(),
    }
    return _object(properties, tuple(properties))


def _creative_structure_directions() -> dict[str, object]:
    properties = {
        "title_directions": _objects(_title_direction()),
        "cover_direction": _cover_direction(),
        "narrative_structure": _objects(_narrative_module()),
        "content_angle_mappings": _objects(_content_angle_mapping()),
        "message_priority": _strings(),
        "proof_placement": _objects(_proof_placement()),
        "fit_boundary": _string(),
    }
    return _object(properties, tuple(properties))


def _discovery_and_action_directions() -> dict[str, object]:
    properties = {
        "search_intent": _string(),
        "keyword_directions": _strings(),
        "topic_directions": _strings(),
        "hashtag_directions": _strings(),
        "cta_mapping": _cta_mapping(),
        "interaction_prompt_direction": _string(),
    }
    return _object(properties, tuple(properties))


def _evidence_and_platform_constraints() -> dict[str, object]:
    properties = {
        "proof_points": _strings(),
        "customer_language": _objects(_customer_language()),
        "mandatory_messages": _strings(),
        "prohibited_claims": _strings(),
        "hypotheses": _strings(),
        "evidence_limitations": _strings(),
        "platform_risk_notes": _strings(),
        "review_route_notes": _strings(),
        "required_qualification_notes": _strings(),
        "commercial_disclosure_notes": _strings(),
    }
    return _object(properties, tuple(properties))


def _candidate() -> dict[str, object]:
    properties = {
        "platform_and_campaign_context": _platform_and_campaign_context(),
        "note_format_and_content_mode": _note_format_and_content_mode(),
        "creative_structure_directions": _creative_structure_directions(),
        "discovery_and_action_directions": _discovery_and_action_directions(),
        "evidence_and_platform_constraints": _evidence_and_platform_constraints(),
    }
    return _object(properties, tuple(properties))


def _workflow_and_version_context() -> dict[str, object]:
    properties = {
        "marketing_brief_version_id": _string(),
        "approved_strategy_version_id": _string(),
        "facts_version_id": _string(),
        "platform_policy_snapshot_id": _string(nullable=True),
        "platform_policy_version": _string(nullable=True),
        "input_limitations": _strings(),
        "stage_decision": _enum(
            tuple(item.value for item in XiaohongshuBriefStageDecision)
        ),
    }
    return _object(properties, tuple(properties))


def _schema() -> dict[str, object]:
    candidate = _candidate()
    properties = {
        "xiaohongshu_brief_candidate": _object(
            cast(Mapping[str, object], candidate["properties"]),
            tuple(cast(list[str], candidate["required"])),
            nullable=True,
        ),
        "workflow_and_version_context": _workflow_and_version_context(),
    }
    return _object(properties, tuple(properties))


def xiaohongshu_brief_candidate_output_spec() -> StructuredOutputSpec:
    """Build a fresh Xiaohongshu Brief mapping candidate schema."""

    return StructuredOutputSpec(
        "xiaohongshu_brief_candidate",
        "v1",
        StructuredContent.from_mapping(_schema()),
    )
