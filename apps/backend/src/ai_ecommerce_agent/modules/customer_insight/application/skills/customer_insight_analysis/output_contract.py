"""Provider-neutral Customer Insight candidate output contract."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum

from ai_ecommerce_agent.application.model_runtime import StructuredOutputSpec
from ai_ecommerce_agent.shared_kernel.structured_content import StructuredContent

_NON_EMPTY = r".*\S.*"


class CustomerInsightMode(StrEnum):
    EVIDENCE_BACKED = "evidence_backed"
    DEGRADED_HYPOTHESIS = "degraded_hypothesis"


class CustomerInsightEvidenceCoverage(StrEnum):
    NONE = "none"
    ANECDOTAL = "anecdotal"
    REPEATED_SIGNAL = "repeated_signal"
    DATASET_SUPPORTED = "dataset_supported"
    MULTI_SOURCE_CORROBORATED = "multi_source_corroborated"


class CustomerInsightStageDecision(StrEnum):
    VALID = "valid"
    VALID_WITH_LIMITATIONS = "valid_with_limitations"
    WAITING_INPUT = "waiting_input"
    PAUSED = "paused"
    FAILED = "failed"


def _string() -> dict[str, object]:
    return {"type": "string", "pattern": _NON_EMPTY}


def _string_array(*, min_items: int | None = None) -> dict[str, object]:
    schema: dict[str, object] = {"type": "array", "items": _string()}
    if min_items is not None:
        schema["minItems"] = min_items
    return schema


def _enum(values: tuple[str, ...]) -> dict[str, object]:
    return {"type": "string", "enum": list(values)}


def _object(
    properties: Mapping[str, object], required: tuple[str, ...]
) -> dict[str, object]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


def _evidence_assessment() -> dict[str, object]:
    properties = {
        "mode": _enum(tuple(item.value for item in CustomerInsightMode)),
        "evidence_coverage": _enum(
            tuple(item.value for item in CustomerInsightEvidenceCoverage)
        ),
        "source_types": _string_array(),
        "source_set_version_id": _string(),
        "sample_summary": _string(),
        "limitations": _string_array(),
    }
    return _object(
        properties,
        (
            "mode",
            "evidence_coverage",
            "source_types",
            "source_set_version_id",
            "sample_summary",
            "limitations",
        ),
    )


def _theme() -> dict[str, object]:
    properties = {
        "label": _string(),
        "evidence_coverage": _enum(
            tuple(item.value for item in CustomerInsightEvidenceCoverage)
        ),
        "source_scopes": _string_array(min_items=1),
        "supporting_fragment_ids": _string_array(min_items=1),
        "contradicting_fragment_ids": _string_array(),
        "limitations": _string_array(),
    }
    return _object(
        properties,
        (
            "label",
            "evidence_coverage",
            "source_scopes",
            "supporting_fragment_ids",
            "contradicting_fragment_ids",
            "limitations",
        ),
    )


def _customer_insight() -> dict[str, object]:
    properties = {
        "insight_type": _string(),
        "statement": _string(),
        "audience_segment": _string(),
        "usage_context": _string(),
        "user_problem_or_need": _string(),
        "underlying_reason": _string(),
        "behavioral_or_purchase_impact": _string(),
        "evidence_coverage": _enum(
            tuple(item.value for item in CustomerInsightEvidenceCoverage)
        ),
        "source_scopes": _string_array(min_items=1),
        "supporting_fragment_ids": _string_array(min_items=1),
        "contradicting_fragment_ids": _string_array(),
        "dataset_statistic_ids": _string_array(),
        "customer_language_fragment_ids": _string_array(),
        "based_on_fact_ids": _string_array(),
        "limitations": _string_array(),
        "notes": _string_array(),
    }
    return _object(
        properties,
        tuple(properties),
    )


def _hypothesis() -> dict[str, object]:
    properties = {
        "statement": _string(),
        "audience_segment": _string(),
        "usage_context": _string(),
        "user_problem_or_need": _string(),
        "underlying_reason": _string(),
        "behavioral_or_purchase_impact": _string(),
        "source_scopes": _string_array(),
        "supporting_fragment_ids": _string_array(),
        "contradicting_fragment_ids": _string_array(),
        "based_on_fact_ids": _string_array(),
        "validation_needed": _string_array(min_items=1),
        "limitations": _string_array(min_items=1),
        "notes": _string_array(),
    }
    return _object(properties, tuple(properties))


def _schema() -> dict[str, object]:
    properties = {
        "evidence_assessment": _evidence_assessment(),
        "themes": {"type": "array", "items": _theme()},
        "customer_insights": {"type": "array", "items": _customer_insight()},
        "hypotheses_to_validate": {"type": "array", "items": _hypothesis()},
        "workflow_stage_decision": _enum(
            tuple(item.value for item in CustomerInsightStageDecision)
        ),
    }
    return _object(properties, tuple(properties))


def customer_insight_candidate_output_spec() -> StructuredOutputSpec:
    """Build a fresh Customer Insight candidate schema."""

    return StructuredOutputSpec(
        "customer_insight_candidate",
        "v1",
        StructuredContent.from_mapping(_schema()),
    )
