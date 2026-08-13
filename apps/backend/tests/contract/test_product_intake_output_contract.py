"""Contract checks for the private Product Intake candidate-output seam."""

from __future__ import annotations

from inspect import Parameter, iscoroutinefunction, signature
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.application import model_runtime
from ai_ecommerce_agent.application.model_runtime import (
    StructuredOutputSpec,
)
from ai_ecommerce_agent.modules.product_intake.application.skills import (
    product_intake_fact_extraction as _fact_extraction,
)

ProductIntakeAssertionType = _fact_extraction.ProductIntakeAssertionType
ProductIntakeCompletenessLevel = _fact_extraction.ProductIntakeCompletenessLevel
ProductIntakeStageDecision = _fact_extraction.ProductIntakeStageDecision
product_intake_candidate_output_spec = (
    _fact_extraction.product_intake_candidate_output_spec
)

pytestmark = pytest.mark.contract


def test_private_facade_and_enum_catalog_are_exact() -> None:
    from ai_ecommerce_agent.modules.product_intake.application.skills import (
        product_intake_fact_extraction,
    )

    assert product_intake_fact_extraction.__all__ == [
        "ProductIntakeCompletenessLevel",
        "ProductIntakeAssertionType",
        "ProductIntakeStageDecision",
        "product_intake_candidate_output_spec",
    ]
    assert [
        getattr(product_intake_fact_extraction, name)
        for name in product_intake_fact_extraction.__all__
    ] == [
        ProductIntakeCompletenessLevel,
        ProductIntakeAssertionType,
        ProductIntakeStageDecision,
        product_intake_candidate_output_spec,
    ]
    assert list(ProductIntakeCompletenessLevel) == [
        ProductIntakeCompletenessLevel.INSUFFICIENT,
        ProductIntakeCompletenessLevel.MINIMAL,
        ProductIntakeCompletenessLevel.STANDARD,
        ProductIntakeCompletenessLevel.EVIDENCE_RICH,
    ]
    assert [item.value for item in ProductIntakeCompletenessLevel] == [
        "insufficient",
        "minimal",
        "standard",
        "evidence_rich",
    ]
    assert [item.value for item in ProductIntakeAssertionType] == [
        "direct_fact",
        "documented_claim",
        "certified_or_tested_fact",
        "marketing_expression",
        "unknown_or_ambiguous",
    ]
    assert [item.value for item in ProductIntakeStageDecision] == [
        "valid",
        "waiting_input",
        "paused",
        "failed",
    ]
    assert not hasattr(model_runtime, "ProductIntakeCompletenessLevel")


def test_spec_facade_is_exact_synchronous_and_typed() -> None:
    function = product_intake_candidate_output_spec
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
    assert first.output_schema_id == "product_intake_fact_candidate"
    assert first.output_schema_version == "v1"
    first_mapping = cast(dict[str, object], first.schema.to_mapping())
    second_mapping = cast(dict[str, object], second.schema.to_mapping())
    assert first_mapping == second_mapping
    cast(dict[str, object], first_mapping["properties"])["mutated"] = {}
    assert "mutated" not in cast(dict[str, object], second_mapping["properties"])


def test_schema_has_exact_top_level_and_nested_ordered_fields() -> None:
    schema = cast(
        dict[str, object], product_intake_candidate_output_spec().schema.to_mapping()
    )
    assert schema["required"] == [
        "intake_assessment",
        "fact_candidates",
        "claims_requiring_verification",
        "conflicts_and_limitations",
        "workflow_stage_decision",
    ]
    assert schema["additionalProperties"] is False
    assert list(cast(dict[str, object], schema["properties"])) == [
        "claims_requiring_verification",
        "conflicts_and_limitations",
        "fact_candidates",
        "intake_assessment",
        "workflow_stage_decision",
    ]
    intake = cast(
        dict[str, object],
        cast(dict[str, object], schema["properties"])["intake_assessment"],
    )
    assert list(cast(dict[str, object], intake["properties"])) == [
        "available_source_types",
        "completeness_level",
        "excluded_sources",
        "missing_information",
        "runnable",
        "warnings",
    ]
    assert intake["required"] == [
        "completeness_level",
        "runnable",
        "available_source_types",
        "excluded_sources",
        "missing_information",
        "warnings",
    ]
    fact_schema = cast(
        dict[str, object],
        cast(dict[str, object], schema["properties"])["fact_candidates"],
    )
    fact = cast(dict[str, object], fact_schema["items"])
    assert list(cast(dict[str, object], fact["properties"])) == [
        "assertion_type",
        "attribute_key",
        "category",
        "contradicting_fragment_ids",
        "normalized_value",
        "notes",
        "raw_value",
        "supporting_fragment_ids",
        "unit",
    ]
    assert fact["required"] == [
        "category",
        "attribute_key",
        "raw_value",
        "normalized_value",
        "unit",
        "assertion_type",
        "supporting_fragment_ids",
        "contradicting_fragment_ids",
        "notes",
    ]
    claim_schema = cast(
        dict[str, object],
        cast(dict[str, object], schema["properties"])["claims_requiring_verification"],
    )
    claim = cast(dict[str, object], claim_schema["items"])
    assert list(cast(dict[str, object], claim["properties"])) == [
        "claim_text",
        "notes",
        "supporting_fragment_ids",
        "verification_need",
    ]
    assert claim["required"] == [
        "claim_text",
        "supporting_fragment_ids",
        "verification_need",
        "notes",
    ]
    conflicts = cast(
        dict[str, object],
        cast(dict[str, object], schema["properties"])["conflicts_and_limitations"],
    )
    assert list(cast(dict[str, object], conflicts["properties"])) == [
        "evidence_limitations",
        "hypotheses_to_validate",
        "insufficient_information",
        "source_conflicts",
    ]
    assert conflicts["required"] == [
        "source_conflicts",
        "evidence_limitations",
        "insufficient_information",
        "hypotheses_to_validate",
    ]
    source_conflict_schema = cast(
        dict[str, object],
        cast(dict[str, object], conflicts["properties"])["source_conflicts"],
    )
    source_conflict = cast(dict[str, object], source_conflict_schema["items"])
    assert list(cast(dict[str, object], source_conflict["properties"])) == [
        "attribute_key",
        "blocking",
        "conflict_kind",
        "impact",
        "observed_values",
    ]
    assert source_conflict["required"] == [
        "conflict_kind",
        "attribute_key",
        "observed_values",
        "blocking",
        "impact",
    ]
    observed_value = cast(
        dict[str, object],
        source_conflict["properties"],
    )["observed_values"]
    assert cast(dict[str, object], observed_value)["minItems"] == 2
    observed_item = cast(
        dict[str, object], cast(dict[str, object], observed_value)["items"]
    )
    assert list(cast(dict[str, object], observed_item["properties"])) == [
        "fragment_ids",
        "raw_value",
    ]
    assert observed_item["required"] == [
        "raw_value",
        "fragment_ids",
    ]
