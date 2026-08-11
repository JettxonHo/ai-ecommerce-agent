"""Provider-neutral Product Positioning candidate output contract."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum

from ai_ecommerce_agent.application.model_runtime import StructuredOutputSpec
from ai_ecommerce_agent.shared_kernel.structured_content import StructuredContent

_NON_EMPTY = r".*\S.*"


class ProductPositioningStageDecision(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    READY_FOR_REVIEW_WITH_LIMITATIONS = "ready_for_review_with_limitations"
    WAITING_INPUT = "waiting_input"
    PAUSED = "paused"
    FAILED = "failed"


def _string(*, nullable: bool = False) -> dict[str, object]:
    return {
        "type": ["string", "null"] if nullable else "string",
        "pattern": _NON_EMPTY,
    }


def _string_array(*, min_items: int | None = None) -> dict[str, object]:
    schema: dict[str, object] = {"type": "array", "items": _string()}
    if min_items is not None:
        schema["minItems"] = min_items
    return schema


def _object(
    properties: Mapping[str, object], required: tuple[str, ...]
) -> dict[str, object]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


def _reasons_to_believe() -> dict[str, object]:
    properties = {
        "statement": _string(),
        "based_on_fact_ids": _string_array(),
        "based_on_insight_ids": _string_array(),
    }
    return _object(properties, tuple(properties))


def _proof_points() -> dict[str, object]:
    properties = {
        "statement": _string(),
        "based_on_fact_ids": _string_array(min_items=1),
    }
    return _object(properties, tuple(properties))


def _positioning_context() -> dict[str, object]:
    properties = {
        "facts_version_id": _string(),
        "insights_version_id": _string(),
        "competitor_source_set_version_id": _string(nullable=True),
        "business_constraints": _string_array(),
        "input_limitations": _string_array(),
    }
    return _object(properties, tuple(properties))


def _positioning_candidate() -> dict[str, object]:
    properties = {
        "candidate_id": _string(),
        "candidate_title": _string(),
        "strategy_type": _string(),
        "target_segment": _string(),
        "target_segment_is_hypothesis": {"type": "boolean"},
        "usage_context": _string(),
        "job_or_core_need": _string(),
        "job_or_core_need_is_hypothesis": {"type": "boolean"},
        "category_frame": _string(),
        "value_proposition": _string(),
        "key_benefits": _string_array(),
        "differentiation": _string(),
        "differentiation_is_opportunity_hypothesis": {"type": "boolean"},
        "reasons_to_believe": {
            "type": "array",
            "items": _reasons_to_believe(),
        },
        "proof_points": {"type": "array", "items": _proof_points()},
        "based_on_fact_ids": _string_array(min_items=1),
        "based_on_insight_ids": _string_array(),
        "competitor_evidence_ids": _string_array(),
        "assumptions": _string_array(),
        "evidence_limitations": _string_array(),
        "strategic_risks": _string_array(),
        "evidence_profile": _string(),
        "ranking_rationale": _string(),
    }
    return _object(properties, tuple(properties))


def _comparison_matrix_item() -> dict[str, object]:
    properties = {
        "candidate_id": _string(),
        "target_segment": _string(),
        "core_need": _string(),
        "primary_value": _string(),
        "key_differentiation": _string(),
        "evidence_profile": _string(),
        "main_risk": _string(nullable=True),
    }
    return _object(properties, tuple(properties))


def _recommendation() -> dict[str, object]:
    properties = {
        "recommended_candidate_id": _string(nullable=True),
        "recommendation_rationale": _string(nullable=True),
        "conditions_for_success": _string_array(),
        "validation_needed": _string_array(),
    }
    return _object(properties, tuple(properties))


def _schema() -> dict[str, object]:
    properties = {
        "positioning_context": _positioning_context(),
        "positioning_candidates": {
            "type": "array",
            "items": _positioning_candidate(),
        },
        "comparison_matrix": {
            "type": "array",
            "items": _comparison_matrix_item(),
        },
        "recommendation": _recommendation(),
        "workflow_stage_decision": {
            "type": "string",
            "enum": [item.value for item in ProductPositioningStageDecision],
        },
    }
    return _object(
        properties,
        (
            "positioning_context",
            "positioning_candidates",
            "comparison_matrix",
            "recommendation",
            "workflow_stage_decision",
        ),
    )


def product_positioning_candidate_output_spec() -> StructuredOutputSpec:
    """Build a fresh Product Positioning candidate schema."""

    return StructuredOutputSpec(
        "product_positioning_candidate",
        "v1",
        StructuredContent.from_mapping(_schema()),
    )
