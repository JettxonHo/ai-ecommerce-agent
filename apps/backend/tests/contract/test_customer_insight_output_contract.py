"""Contract checks for the private Customer Insight candidate-output seam."""

from __future__ import annotations

from inspect import Parameter, iscoroutinefunction, signature
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.application import model_runtime
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.modules.customer_insight.application.skills import (
    customer_insight_analysis as _customer_insight,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _schema_compatibility,
)

CustomerInsightMode = _customer_insight.CustomerInsightMode
CustomerInsightEvidenceCoverage = _customer_insight.CustomerInsightEvidenceCoverage
CustomerInsightStageDecision = _customer_insight.CustomerInsightStageDecision
customer_insight_candidate_output_spec = (
    _customer_insight.customer_insight_candidate_output_spec
)

pytestmark = pytest.mark.contract


def test_private_facade_and_enum_catalog_are_exact() -> None:
    assert _customer_insight.__all__ == [
        "CustomerInsightMode",
        "CustomerInsightEvidenceCoverage",
        "CustomerInsightStageDecision",
        "customer_insight_candidate_output_spec",
    ]
    assert [getattr(_customer_insight, name) for name in _customer_insight.__all__] == [
        CustomerInsightMode,
        CustomerInsightEvidenceCoverage,
        CustomerInsightStageDecision,
        customer_insight_candidate_output_spec,
    ]
    assert list(CustomerInsightMode) == [
        CustomerInsightMode.EVIDENCE_BACKED,
        CustomerInsightMode.DEGRADED_HYPOTHESIS,
    ]
    assert [item.value for item in CustomerInsightMode] == [
        "evidence_backed",
        "degraded_hypothesis",
    ]
    assert [item.value for item in CustomerInsightEvidenceCoverage] == [
        "none",
        "anecdotal",
        "repeated_signal",
        "dataset_supported",
        "multi_source_corroborated",
    ]
    assert [item.value for item in CustomerInsightStageDecision] == [
        "valid",
        "valid_with_limitations",
        "waiting_input",
        "paused",
        "failed",
    ]
    assert not hasattr(model_runtime, "CustomerInsightMode")
    assert not hasattr(model_runtime, "CustomerInsightEvidenceCoverage")
    assert not hasattr(model_runtime, "CustomerInsightStageDecision")


def test_spec_facade_is_exact_synchronous_and_typed() -> None:
    function = customer_insight_candidate_output_spec
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
    assert first.output_schema_id == "customer_insight_candidate"
    assert first.output_schema_version == "v1"
    _schema_compatibility.ensure_openai_responses_schema_compatible(
        structured_output=first,
        model_call_id=ModelCallId("customer-insight-schema-test"),
    )
    first_mapping = cast(dict[str, object], first.schema.to_mapping())
    second_mapping = cast(dict[str, object], second.schema.to_mapping())
    assert first_mapping == second_mapping
    cast(dict[str, object], first_mapping["properties"])["mutated"] = {}
    assert "mutated" not in cast(dict[str, object], second_mapping["properties"])


def test_schema_has_exact_ordered_fields_and_closed_objects() -> None:
    schema = cast(
        dict[str, object], customer_insight_candidate_output_spec().schema.to_mapping()
    )
    properties = cast(dict[str, object], schema["properties"])
    assert list(properties) == [
        "customer_insights",
        "evidence_assessment",
        "hypotheses_to_validate",
        "themes",
        "workflow_stage_decision",
    ]
    assert schema["required"] == [
        "evidence_assessment",
        "themes",
        "customer_insights",
        "hypotheses_to_validate",
        "workflow_stage_decision",
    ]
    assert schema["additionalProperties"] is False

    evidence = cast(dict[str, object], properties["evidence_assessment"])
    assert list(cast(dict[str, object], evidence["properties"])) == [
        "evidence_coverage",
        "limitations",
        "mode",
        "sample_summary",
        "source_set_version_id",
        "source_types",
    ]
    assert evidence["required"] == [
        "mode",
        "evidence_coverage",
        "source_types",
        "source_set_version_id",
        "sample_summary",
        "limitations",
    ]
    themes = cast(
        dict[str, object], cast(dict[str, object], properties["themes"])["items"]
    )
    assert list(cast(dict[str, object], themes["properties"])) == [
        "contradicting_fragment_ids",
        "evidence_coverage",
        "label",
        "limitations",
        "source_scopes",
        "supporting_fragment_ids",
    ]
    assert themes["required"] == [
        "label",
        "evidence_coverage",
        "source_scopes",
        "supporting_fragment_ids",
        "contradicting_fragment_ids",
        "limitations",
    ]
    insights = cast(
        dict[str, object],
        cast(dict[str, object], properties["customer_insights"])["items"],
    )
    assert list(cast(dict[str, object], insights["properties"])) == [
        "audience_segment",
        "based_on_fact_ids",
        "behavioral_or_purchase_impact",
        "contradicting_fragment_ids",
        "customer_language_fragment_ids",
        "dataset_statistic_ids",
        "evidence_coverage",
        "insight_type",
        "limitations",
        "notes",
        "source_scopes",
        "statement",
        "supporting_fragment_ids",
        "underlying_reason",
        "usage_context",
        "user_problem_or_need",
    ]
    assert insights["required"] == [
        "insight_type",
        "statement",
        "audience_segment",
        "usage_context",
        "user_problem_or_need",
        "underlying_reason",
        "behavioral_or_purchase_impact",
        "evidence_coverage",
        "source_scopes",
        "supporting_fragment_ids",
        "contradicting_fragment_ids",
        "dataset_statistic_ids",
        "customer_language_fragment_ids",
        "based_on_fact_ids",
        "limitations",
        "notes",
    ]
    hypotheses = cast(
        dict[str, object],
        cast(dict[str, object], properties["hypotheses_to_validate"])["items"],
    )
    assert list(cast(dict[str, object], hypotheses["properties"])) == [
        "audience_segment",
        "based_on_fact_ids",
        "behavioral_or_purchase_impact",
        "contradicting_fragment_ids",
        "limitations",
        "notes",
        "source_scopes",
        "statement",
        "supporting_fragment_ids",
        "underlying_reason",
        "usage_context",
        "user_problem_or_need",
        "validation_needed",
    ]
    assert hypotheses["required"] == [
        "statement",
        "audience_segment",
        "usage_context",
        "user_problem_or_need",
        "underlying_reason",
        "behavioral_or_purchase_impact",
        "source_scopes",
        "supporting_fragment_ids",
        "contradicting_fragment_ids",
        "based_on_fact_ids",
        "validation_needed",
        "limitations",
        "notes",
    ]
    for item in (evidence, themes, insights, hypotheses):
        assert item["additionalProperties"] is False


def test_schema_does_not_freeze_quote_or_calculation_fields() -> None:
    schema = cast(
        dict[str, object], customer_insight_candidate_output_spec().schema.to_mapping()
    )
    serialized = repr(schema)
    assert "quote_text" not in serialized
    assert "customer_language_fragment_ids" in serialized
    assert "percentage" not in serialized
    assert "frequency" not in serialized
    assert "sample_size" not in serialized
