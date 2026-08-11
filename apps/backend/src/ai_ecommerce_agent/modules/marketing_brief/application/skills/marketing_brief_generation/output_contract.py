"""Provider-neutral Marketing Brief candidate output contract."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import cast

from ai_ecommerce_agent.application.model_runtime import StructuredOutputSpec
from ai_ecommerce_agent.shared_kernel.structured_content import StructuredContent

_NON_EMPTY = r".*\S.*"


class MarketingBriefStageDecision(StrEnum):
    VALID = "valid"
    VALID_WITH_LIMITATIONS = "valid_with_limitations"
    STRATEGY_CHANGE_REQUIRED = "strategy_change_required"
    WAITING_INPUT = "waiting_input"
    PAUSED = "paused"
    FAILED = "failed"


def _string() -> dict[str, object]:
    return {"type": "string", "pattern": _NON_EMPTY}


def _strings(*, min_items: int | None = None) -> dict[str, object]:
    schema: dict[str, object] = {"type": "array", "items": _string()}
    if min_items is not None:
        schema["minItems"] = min_items
    return schema


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


def _communication_objective() -> dict[str, object]:
    properties = {
        "primary_objective": _string(),
        "secondary_objectives": _strings(),
        "business_assumption": {"type": "boolean"},
    }
    return _object(properties, tuple(properties))


def _message_hierarchy() -> dict[str, object]:
    properties = {
        "primary_message": _string(),
        "secondary_benefits": _strings(),
        "supporting_proof_points": _strings(),
    }
    return _object(properties, tuple(properties))


def _benefit_hierarchy() -> dict[str, object]:
    properties = {
        "primary_benefit": _string(),
        "secondary_benefits": _strings(),
        "supporting_features": _strings(),
    }
    return _object(properties, tuple(properties))


def _reasons_to_believe() -> dict[str, object]:
    properties = {
        "statement": _string(),
        "based_on_fact_ids": _strings(),
        "based_on_insight_ids": _strings(),
    }
    return _object(properties, tuple(properties))


def _proof_point() -> dict[str, object]:
    properties = {
        "proof_point": _string(),
        "fact_id": _string(),
        "supporting_fragment_ids": _strings(min_items=1),
        "source_version_id": _string(),
        "approved_wording": _string(),
    }
    return _object(properties, tuple(properties))


def _objection_response() -> dict[str, object]:
    properties = {
        "objection": _string(),
        "response": _string(),
        "based_on_fact_ids": _strings(),
        "based_on_insight_ids": _strings(),
        "insufficient_evidence": {"type": "boolean"},
    }
    return _object(properties, tuple(properties))


def _content_angle() -> dict[str, object]:
    properties = {
        "angle_title": _string(),
        "angle_type": _string(),
        "user_tension": _string(),
        "message_focus": _string(),
        "supporting_benefits": _strings(),
        "proof_points": _strings(),
        "hypothesis_status": _string(),
        "requires_validation": {"type": "boolean"},
        "risk_notes": _strings(),
    }
    return _object(properties, tuple(properties))


def _tone_and_voice() -> dict[str, object]:
    properties = {
        "tone": _string(),
        "voice": _string(),
        "suggested_tone": {"type": "boolean"},
    }
    return _object(properties, tuple(properties))


def _candidate() -> dict[str, object]:
    objective = {
        "communication_objective": _communication_objective(),
        "audience": _string(),
        "audience_context": _strings(),
        "audience_is_hypothesis": {"type": "boolean"},
    }
    message = {
        "core_message": _string(),
        "message_hierarchy": _message_hierarchy(),
        "benefit_hierarchy": _benefit_hierarchy(),
    }
    evidence = {
        "reasons_to_believe": _objects(_reasons_to_believe()),
        "proof_points": _objects(_proof_point()),
    }
    execution = {
        "objections": _strings(),
        "objection_responses": _objects(_objection_response()),
        "content_angles": _objects(_content_angle()),
        "tone_and_voice": _tone_and_voice(),
        "call_to_action_objective": _string(),
    }
    honesty = {
        "mandatory_messages": _strings(),
        "prohibited_claims": _strings(),
        "accepted_hypotheses": _strings(),
        "hypotheses_to_test": _strings(),
        "evidence_limitations": _strings(),
        "risk_notes": _strings(),
        "platform_adaptation_rules": _strings(),
    }
    groups = {
        "objective_and_audience": _object(objective, tuple(objective)),
        "message_architecture": _object(message, tuple(message)),
        "reasons_to_believe_and_evidence": _object(evidence, tuple(evidence)),
        "execution_direction": _object(execution, tuple(execution)),
        "constraints_and_honesty": _object(honesty, tuple(honesty)),
    }
    return _object(groups, tuple(groups))


def _workflow_context() -> dict[str, object]:
    properties = {
        "approved_strategy_version_id": _string(),
        "facts_version_id": _string(),
        "insights_version_id": _string(),
        "input_limitations": _strings(),
        "stage_decision": _enum(
            tuple(item.value for item in MarketingBriefStageDecision)
        ),
    }
    return _object(properties, tuple(properties))


def _schema() -> dict[str, object]:
    candidate = _candidate()
    properties = {
        "brief_candidate": _object(
            cast(Mapping[str, object], candidate["properties"]),
            tuple(cast(list[str], candidate["required"])),
            nullable=True,
        ),
        "version_and_workflow_context": _workflow_context(),
    }
    return _object(properties, tuple(properties))


def marketing_brief_candidate_output_spec() -> StructuredOutputSpec:
    """Build a fresh Marketing Brief candidate schema."""

    return StructuredOutputSpec(
        "marketing_brief_candidate",
        "v1",
        StructuredContent.from_mapping(_schema()),
    )
