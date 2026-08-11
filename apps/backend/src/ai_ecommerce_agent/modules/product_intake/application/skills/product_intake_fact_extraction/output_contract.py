"""Provider-neutral Product Intake candidate output contract."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum

from ai_ecommerce_agent.application.model_runtime import (
    StructuredOutputSpec,
)
from ai_ecommerce_agent.shared_kernel.structured_content import StructuredContent

_NON_EMPTY = r".*\S.*"


class ProductIntakeCompletenessLevel(StrEnum):
    INSUFFICIENT = "insufficient"
    MINIMAL = "minimal"
    STANDARD = "standard"
    EVIDENCE_RICH = "evidence_rich"


class ProductIntakeAssertionType(StrEnum):
    DIRECT_FACT = "direct_fact"
    DOCUMENTED_CLAIM = "documented_claim"
    CERTIFIED_OR_TESTED_FACT = "certified_or_tested_fact"
    MARKETING_EXPRESSION = "marketing_expression"
    UNKNOWN_OR_AMBIGUOUS = "unknown_or_ambiguous"


class ProductIntakeStageDecision(StrEnum):
    VALID = "valid"
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


def _enum(values: tuple[str, ...]) -> dict[str, object]:
    return {"type": "string", "enum": list(values)}


def _object(
    properties: Mapping[str, object],
    required: tuple[str, ...],
) -> dict[str, object]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


def _intake_assessment() -> dict[str, object]:
    properties = {
        "completeness_level": _enum(
            tuple(level.value for level in ProductIntakeCompletenessLevel)
        ),
        "runnable": {"type": "boolean"},
        "available_source_types": _string_array(),
        "excluded_sources": _string_array(),
        "missing_information": _string_array(),
        "warnings": _string_array(),
    }
    return _object(
        properties,
        (
            "completeness_level",
            "runnable",
            "available_source_types",
            "excluded_sources",
            "missing_information",
            "warnings",
        ),
    )


def _fact_candidate() -> dict[str, object]:
    properties = {
        "category": _string(),
        "attribute_key": _string(),
        "raw_value": _string(),
        "normalized_value": _string(nullable=True),
        "unit": _string(nullable=True),
        "assertion_type": _enum(
            tuple(assertion.value for assertion in ProductIntakeAssertionType)
        ),
        "supporting_fragment_ids": _string_array(min_items=1),
        "contradicting_fragment_ids": _string_array(),
        "notes": _string_array(),
    }
    return _object(
        properties,
        (
            "category",
            "attribute_key",
            "raw_value",
            "normalized_value",
            "unit",
            "assertion_type",
            "supporting_fragment_ids",
            "contradicting_fragment_ids",
            "notes",
        ),
    )


def _claim() -> dict[str, object]:
    properties = {
        "claim_text": _string(),
        "supporting_fragment_ids": _string_array(min_items=1),
        "verification_need": _string(),
        "notes": _string_array(),
    }
    return _object(
        properties,
        ("claim_text", "supporting_fragment_ids", "verification_need", "notes"),
    )


def _observed_value() -> dict[str, object]:
    return _object(
        {"raw_value": _string(), "fragment_ids": _string_array(min_items=1)},
        ("raw_value", "fragment_ids"),
    )


def _source_conflict() -> dict[str, object]:
    return _object(
        {
            "conflict_kind": _string(),
            "attribute_key": _string(),
            "observed_values": {
                "type": "array",
                "items": _observed_value(),
                "minItems": 2,
            },
            "blocking": {"type": "boolean"},
            "impact": _string(),
        },
        ("conflict_kind", "attribute_key", "observed_values", "blocking", "impact"),
    )


def _conflicts_and_limitations() -> dict[str, object]:
    return _object(
        {
            "source_conflicts": {"type": "array", "items": _source_conflict()},
            "evidence_limitations": _string_array(),
            "insufficient_information": _string_array(),
            "hypotheses_to_validate": _string_array(),
        },
        (
            "source_conflicts",
            "evidence_limitations",
            "insufficient_information",
            "hypotheses_to_validate",
        ),
    )


def _schema() -> dict[str, object]:
    properties = {
        "intake_assessment": _intake_assessment(),
        "fact_candidates": {"type": "array", "items": _fact_candidate()},
        "claims_requiring_verification": {"type": "array", "items": _claim()},
        "conflicts_and_limitations": _conflicts_and_limitations(),
        "workflow_stage_decision": _enum(
            tuple(decision.value for decision in ProductIntakeStageDecision)
        ),
    }
    return _object(
        properties,
        (
            "intake_assessment",
            "fact_candidates",
            "claims_requiring_verification",
            "conflicts_and_limitations",
            "workflow_stage_decision",
        ),
    )


def product_intake_candidate_output_spec() -> StructuredOutputSpec:
    """Build a fresh Product Intake candidate schema."""

    schema = StructuredContent.from_mapping(_schema())
    spec = StructuredOutputSpec(
        "product_intake_fact_candidate",
        "v1",
        schema,
    )
    return spec
