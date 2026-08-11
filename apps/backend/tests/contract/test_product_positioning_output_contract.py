"""Contract checks for the private Product Positioning output seam."""

from __future__ import annotations

from inspect import Parameter, iscoroutinefunction, signature
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.application import model_runtime
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.modules.product_positioning.application.skills import (
    product_positioning as _positioning,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _schema_compatibility,
)

ProductPositioningStageDecision = _positioning.ProductPositioningStageDecision
product_positioning_candidate_output_spec = (
    _positioning.product_positioning_candidate_output_spec
)

pytestmark = pytest.mark.contract


def test_private_facade_and_enum_catalog_are_exact() -> None:
    assert _positioning.__all__ == [
        "ProductPositioningStageDecision",
        "product_positioning_candidate_output_spec",
    ]
    assert [getattr(_positioning, name) for name in _positioning.__all__] == [
        ProductPositioningStageDecision,
        product_positioning_candidate_output_spec,
    ]
    assert [item.value for item in ProductPositioningStageDecision] == [
        "ready_for_review",
        "ready_for_review_with_limitations",
        "waiting_input",
        "paused",
        "failed",
    ]
    assert not hasattr(model_runtime, "ProductPositioningStageDecision")


def test_spec_facade_is_exact_synchronous_and_typed() -> None:
    function = product_positioning_candidate_output_spec
    assert list(signature(function).parameters) == []
    assert all(
        parameter.kind is Parameter.POSITIONAL_OR_KEYWORD
        for parameter in signature(function).parameters.values()
    )
    assert get_type_hints(function) == {"return": StructuredOutputSpec}
    assert not iscoroutinefunction(function)
    first = function()
    second = function()
    assert type(first) is StructuredOutputSpec
    assert first == second
    assert first is not second
    assert first.output_schema_id == "product_positioning_candidate"
    assert first.output_schema_version == "v1"
    _schema_compatibility.ensure_openai_responses_schema_compatible(
        structured_output=first,
        model_call_id=ModelCallId("positioning-schema-test"),
    )
    first_mapping = cast(dict[str, object], first.schema.to_mapping())
    second_mapping = cast(dict[str, object], second.schema.to_mapping())
    assert first_mapping == second_mapping
    cast(dict[str, object], first_mapping["properties"])["mutated"] = {}
    assert "mutated" not in cast(dict[str, object], second_mapping["properties"])


def test_schema_has_exact_root_and_nested_ordered_fields() -> None:
    schema = cast(
        dict[str, object],
        product_positioning_candidate_output_spec().schema.to_mapping(),
    )
    properties = cast(dict[str, object], schema["properties"])
    assert list(properties) == [
        "comparison_matrix",
        "positioning_candidates",
        "positioning_context",
        "recommendation",
        "workflow_stage_decision",
    ]
    assert schema["required"] == [
        "positioning_context",
        "positioning_candidates",
        "comparison_matrix",
        "recommendation",
        "workflow_stage_decision",
    ]
    assert schema["additionalProperties"] is False

    context = cast(dict[str, object], properties["positioning_context"])
    assert list(cast(dict[str, object], context["properties"])) == [
        "business_constraints",
        "competitor_source_set_version_id",
        "facts_version_id",
        "input_limitations",
        "insights_version_id",
    ]
    assert context["required"] == [
        "facts_version_id",
        "insights_version_id",
        "competitor_source_set_version_id",
        "business_constraints",
        "input_limitations",
    ]

    candidate = cast(
        dict[str, object],
        cast(dict[str, object], properties["positioning_candidates"])["items"],
    )
    assert list(cast(dict[str, object], candidate["properties"])) == [
        "assumptions",
        "based_on_fact_ids",
        "based_on_insight_ids",
        "candidate_id",
        "candidate_title",
        "category_frame",
        "competitor_evidence_ids",
        "differentiation",
        "differentiation_is_opportunity_hypothesis",
        "evidence_limitations",
        "evidence_profile",
        "job_or_core_need",
        "job_or_core_need_is_hypothesis",
        "key_benefits",
        "proof_points",
        "ranking_rationale",
        "reasons_to_believe",
        "strategic_risks",
        "strategy_type",
        "target_segment",
        "target_segment_is_hypothesis",
        "usage_context",
        "value_proposition",
    ]
    assert candidate["required"] == [
        "candidate_id",
        "candidate_title",
        "strategy_type",
        "target_segment",
        "target_segment_is_hypothesis",
        "usage_context",
        "job_or_core_need",
        "job_or_core_need_is_hypothesis",
        "category_frame",
        "value_proposition",
        "key_benefits",
        "differentiation",
        "differentiation_is_opportunity_hypothesis",
        "reasons_to_believe",
        "proof_points",
        "based_on_fact_ids",
        "based_on_insight_ids",
        "competitor_evidence_ids",
        "assumptions",
        "evidence_limitations",
        "strategic_risks",
        "evidence_profile",
        "ranking_rationale",
    ]

    reason = cast(
        dict[str, object],
        cast(dict[str, object], candidate["properties"])["reasons_to_believe"],
    )["items"]
    reason_schema = cast(dict[str, object], reason)
    assert list(cast(dict[str, object], reason_schema["properties"])) == [
        "based_on_fact_ids",
        "based_on_insight_ids",
        "statement",
    ]
    assert reason_schema["required"] == [
        "statement",
        "based_on_fact_ids",
        "based_on_insight_ids",
    ]
    proof = cast(
        dict[str, object],
        cast(dict[str, object], candidate["properties"])["proof_points"],
    )["items"]
    proof_schema = cast(dict[str, object], proof)
    assert list(cast(dict[str, object], proof_schema["properties"])) == [
        "based_on_fact_ids",
        "statement",
    ]
    assert proof_schema["required"] == [
        "statement",
        "based_on_fact_ids",
    ]
    proof_properties = cast(dict[str, object], proof_schema["properties"])
    assert cast(dict[str, object], proof_properties["based_on_fact_ids"]) == {
        "type": "array",
        "items": {"type": "string", "pattern": r".*\S.*"},
        "minItems": 1,
    }

    matrix = cast(
        dict[str, object],
        cast(dict[str, object], properties["comparison_matrix"])["items"],
    )
    assert list(cast(dict[str, object], matrix["properties"])) == [
        "candidate_id",
        "core_need",
        "evidence_profile",
        "key_differentiation",
        "main_risk",
        "primary_value",
        "target_segment",
    ]
    assert matrix["required"] == [
        "candidate_id",
        "target_segment",
        "core_need",
        "primary_value",
        "key_differentiation",
        "evidence_profile",
        "main_risk",
    ]
    recommendation = cast(dict[str, object], properties["recommendation"])
    assert list(cast(dict[str, object], recommendation["properties"])) == [
        "conditions_for_success",
        "recommendation_rationale",
        "recommended_candidate_id",
        "validation_needed",
    ]
    assert recommendation["required"] == [
        "recommended_candidate_id",
        "recommendation_rationale",
        "conditions_for_success",
        "validation_needed",
    ]
    recommendation_properties = cast(dict[str, object], recommendation["properties"])
    assert cast(
        dict[str, object], recommendation_properties["recommended_candidate_id"]
    )["type"] == ["string", "null"]
    assert cast(
        dict[str, object], recommendation_properties["recommendation_rationale"]
    )["type"] == ["string", "null"]

    for item in (context, candidate, reason, proof, matrix, recommendation):
        assert cast(dict[str, object], item)["additionalProperties"] is False


def test_schema_has_no_final_strategy_or_numeric_scoring_fields() -> None:
    serialized = repr(product_positioning_candidate_output_spec().schema.to_mapping())
    for forbidden in (
        "StrategyType",
        "EvidenceProfile",
        "review_status",
        "score",
        "weight",
        "similarity",
        "confidence",
        "formula",
    ):
        assert forbidden not in serialized
