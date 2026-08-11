"""Behavior tests for the Customer Insight candidate output schema."""

from __future__ import annotations

import json
from typing import Any, cast

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId,
    ModelCallResult,
    ModelOutputEnvelope,
    ModelRuntimeError,
    ModelRuntimeVersionTuple,
    ModelTokenUsage,
    ProviderAttemptId,
    ProviderCallMetadata,
)
from ai_ecommerce_agent.application.structured_output import (
    parse_and_validate_structured_output,
)
from ai_ecommerce_agent.modules.customer_insight.application.skills import (
    customer_insight_analysis as _customer_insight,
)

customer_insight_candidate_output_spec = (
    _customer_insight.customer_insight_candidate_output_spec
)

pytestmark = pytest.mark.unit


def _result(payload: dict[str, object]) -> ModelCallResult:
    versions = ModelRuntimeVersionTuple(
        "provider",
        "responses",
        "sdk",
        "configured",
        None,
        "prompt",
        "v1",
        "customer_insight_candidate",
        "v1",
        "skill",
        "domain",
        "profile",
        "v1",
        "context",
    )
    metadata = ProviderCallMetadata(
        ModelCallId("call-customer-insight"),
        (ProviderAttemptId("attempt-customer-insight"),),
        versions,
        "response-customer-insight",
        None,
        ModelTokenUsage(1, 2, 3),
        1,
    )
    return ModelCallResult(
        ModelOutputEnvelope(json.dumps(payload, separators=(",", ":"))), metadata
    )


def _candidate_payload(kind: str) -> dict[str, object]:
    evidence = {
        "mode": "evidence_backed",
        "evidence_coverage": "repeated_signal",
        "source_types": ["current_product_reviews", "customer_service"],
        "source_set_version_id": "source-set-v1",
        "sample_summary": "Repeated reports across independent records",
        "limitations": [],
    }
    theme = {
        "label": "leak resistance",
        "evidence_coverage": "repeated_signal",
        "source_scopes": ["current_product"],
        "supporting_fragment_ids": ["fragment-1"],
        "contradicting_fragment_ids": ["fragment-2"],
        "limitations": [],
    }
    insight = {
        "insight_type": "pain_point",
        "statement": "Commuters worry that a leaking bottle can damage work items",
        "audience_segment": "daily commuters",
        "usage_context": "carrying the bottle in a work bag",
        "user_problem_or_need": "keep documents and electronics dry",
        "underlying_reason": "small leaks have disproportionate consequences",
        "behavioral_or_purchase_impact": "leak resistance affects purchase confidence",
        "evidence_coverage": "repeated_signal",
        "source_scopes": ["current_product"],
        "supporting_fragment_ids": ["fragment-1"],
        "contradicting_fragment_ids": ["fragment-2"],
        "dataset_statistic_ids": [],
        "customer_language_fragment_ids": ["fragment-1"],
        "based_on_fact_ids": [],
        "limitations": [],
        "notes": [],
    }
    hypothesis = {
        "statement": "Leak resistance may be important for office commuters",
        "audience_segment": "office commuters",
        "usage_context": "carrying a bottle beside a laptop",
        "user_problem_or_need": "avoid accidental bag damage",
        "underlying_reason": "the cost of a spill may exceed the product price",
        "behavioral_or_purchase_impact": "this may influence comparison shopping",
        "source_scopes": [],
        "supporting_fragment_ids": [],
        "contradicting_fragment_ids": [],
        "based_on_fact_ids": [],
        "validation_needed": ["validate with current-customer interviews"],
        "limitations": ["no direct customer evidence is available"],
        "notes": [],
    }
    base: dict[str, object] = {
        "evidence_assessment": evidence,
        "themes": [theme],
        "customer_insights": [insight],
        "hypotheses_to_validate": [],
        "workflow_stage_decision": "valid",
    }
    if kind == "degraded":
        base.update(
            {
                "evidence_assessment": {
                    "mode": "degraded_hypothesis",
                    "evidence_coverage": "none",
                    "source_types": [],
                    "source_set_version_id": "source-set-absent",
                    "sample_summary": "No direct customer evidence was provided",
                    "limitations": ["hypotheses require validation"],
                },
                "themes": [],
                "customer_insights": [],
                "hypotheses_to_validate": [hypothesis],
                "workflow_stage_decision": "valid_with_limitations",
            }
        )
    elif kind == "competitor":
        competitor_scope = "competitor:anchor-sku"
        cast(dict[str, object], base["evidence_assessment"]).update(
            {
                "evidence_coverage": "anecdotal",
                "source_types": ["competitor_reviews"],
                "source_set_version_id": "source-set-competitor-v1",
                "sample_summary": "Competitor-only customer records",
            }
        )
        cast(dict[str, object], cast(list[object], base["themes"])[0]).update(
            {
                "evidence_coverage": "anecdotal",
                "source_scopes": [competitor_scope],
                "supporting_fragment_ids": ["competitor-fragment-1"],
                "contradicting_fragment_ids": [],
            }
        )
        competitor_insight = cast(
            dict[str, object], cast(list[object], base["customer_insights"])[0]
        )
        competitor_insight.update(
            {
                "statement": (
                    "Competitor customers mention leak resistance as a "
                    "comparison concern"
                ),
                "evidence_coverage": "anecdotal",
                "source_scopes": [competitor_scope],
                "supporting_fragment_ids": ["competitor-fragment-1"],
                "contradicting_fragment_ids": [],
                "customer_language_fragment_ids": [],
            }
        )
        base["workflow_stage_decision"] = "valid_with_limitations"
    return base


def _set_path(
    payload: dict[str, object], path: tuple[object, ...], value: object
) -> None:
    current: Any = payload
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


def _delete_path(payload: dict[str, object], path: tuple[object, ...]) -> None:
    current: Any = payload
    for key in path[:-1]:
        current = current[key]
    del current[path[-1]]


def _payload_for_path(path: tuple[object, ...]) -> dict[str, object]:
    if path and path[0] == "hypotheses_to_validate":
        return _candidate_payload("degraded")
    if path and path[0] in {"themes", "customer_insights"}:
        return _candidate_payload("sufficient")
    return _candidate_payload("sufficient")


@pytest.mark.parametrize("kind", ["sufficient", "degraded", "competitor"])
def test_three_production_shaped_candidates_pass_existing_validator(kind: str) -> None:
    payload = _candidate_payload(kind)
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=customer_insight_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


def test_competitor_only_candidate_is_explicitly_scoped_and_limited() -> None:
    payload = _candidate_payload("competitor")
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=customer_insight_candidate_output_spec()
    )
    assert payload["workflow_stage_decision"] == "valid_with_limitations"
    assert parsed.to_mapping() == payload
    serialized = json.dumps(payload, separators=(",", ":"))
    assert "current_product" not in serialized
    for group in ("themes", "customer_insights"):
        for item in cast(list[object], payload[group]):
            scopes = cast(list[object], cast(dict[str, object], item)["source_scopes"])
            assert all(str(scope).startswith("competitor:") for scope in scopes)


def test_none_coverage_does_not_semantically_forbid_a_structural_theme() -> None:
    payload = _candidate_payload("degraded")
    payload["themes"] = [
        {
            "label": "possible leak concern",
            "evidence_coverage": "none",
            "source_scopes": ["context"],
            "supporting_fragment_ids": ["context-fragment"],
            "contradicting_fragment_ids": [],
            "limitations": ["requires direct customer validation"],
        }
    ]
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=customer_insight_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    "path",
    [
        ("evidence_assessment", "mode"),
        ("evidence_assessment", "evidence_coverage"),
        ("evidence_assessment", "source_types"),
        ("evidence_assessment", "source_set_version_id"),
        ("evidence_assessment", "sample_summary"),
        ("evidence_assessment", "limitations"),
        ("themes", 0, "label"),
        ("themes", 0, "evidence_coverage"),
        ("themes", 0, "source_scopes"),
        ("themes", 0, "supporting_fragment_ids"),
        ("themes", 0, "contradicting_fragment_ids"),
        ("themes", 0, "limitations"),
        ("customer_insights", 0, "insight_type"),
        ("customer_insights", 0, "statement"),
        ("customer_insights", 0, "audience_segment"),
        ("customer_insights", 0, "usage_context"),
        ("customer_insights", 0, "user_problem_or_need"),
        ("customer_insights", 0, "underlying_reason"),
        ("customer_insights", 0, "behavioral_or_purchase_impact"),
        ("customer_insights", 0, "evidence_coverage"),
        ("customer_insights", 0, "source_scopes"),
        ("customer_insights", 0, "supporting_fragment_ids"),
        ("customer_insights", 0, "contradicting_fragment_ids"),
        ("customer_insights", 0, "dataset_statistic_ids"),
        ("customer_insights", 0, "customer_language_fragment_ids"),
        ("customer_insights", 0, "based_on_fact_ids"),
        ("customer_insights", 0, "limitations"),
        ("customer_insights", 0, "notes"),
        ("hypotheses_to_validate", 0, "statement"),
        ("hypotheses_to_validate", 0, "audience_segment"),
        ("hypotheses_to_validate", 0, "usage_context"),
        ("hypotheses_to_validate", 0, "user_problem_or_need"),
        ("hypotheses_to_validate", 0, "underlying_reason"),
        ("hypotheses_to_validate", 0, "behavioral_or_purchase_impact"),
        ("hypotheses_to_validate", 0, "source_scopes"),
        ("hypotheses_to_validate", 0, "supporting_fragment_ids"),
        ("hypotheses_to_validate", 0, "contradicting_fragment_ids"),
        ("hypotheses_to_validate", 0, "based_on_fact_ids"),
        ("hypotheses_to_validate", 0, "validation_needed"),
        ("hypotheses_to_validate", 0, "limitations"),
        ("hypotheses_to_validate", 0, "notes"),
        ("workflow_stage_decision",),
    ],
)
def test_every_frozen_required_field_is_required(path: tuple[object, ...]) -> None:
    payload = _payload_for_path(path)
    _delete_path(payload, path)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=customer_insight_candidate_output_spec()
        )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("evidence_assessment", "mode"), "unsupported"),
        (("evidence_assessment", "evidence_coverage"), "unsupported"),
        (("evidence_assessment", "source_types"), [1]),
        (("evidence_assessment", "source_set_version_id"), "   "),
        (("themes", 0, "evidence_coverage"), "unsupported"),
        (("themes", 0, "source_scopes"), []),
        (("themes", 0, "supporting_fragment_ids"), []),
        (("themes", 0, "supporting_fragment_ids", 0), 1),
        (("customer_insights", 0, "evidence_coverage"), "unsupported"),
        (("customer_insights", 0, "source_scopes"), []),
        (("customer_insights", 0, "supporting_fragment_ids"), []),
        (("customer_insights", 0, "supporting_fragment_ids", 0), None),
        (("hypotheses_to_validate", 0, "validation_needed"), []),
        (("hypotheses_to_validate", 0, "limitations"), []),
        (("hypotheses_to_validate", 0, "validation_needed", 0), 1),
        (("workflow_stage_decision",), "unsupported"),
    ],
)
def test_minimums_and_item_types_are_strict(
    path: tuple[object, ...], value: object
) -> None:
    payload = _payload_for_path(path)
    _set_path(payload, path, value)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=customer_insight_candidate_output_spec()
        )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("evidence_assessment", "mode"), 1),
        (("evidence_assessment", "evidence_coverage"), 1),
        (("evidence_assessment", "source_types"), [1]),
        (("evidence_assessment", "source_set_version_id"), 1),
        (("evidence_assessment", "sample_summary"), 1),
        (("evidence_assessment", "limitations"), [1]),
        (("themes",), [1]),
        (("themes", 0, "label"), 1),
        (("themes", 0, "evidence_coverage"), 1),
        (("themes", 0, "source_scopes"), [1]),
        (("themes", 0, "supporting_fragment_ids"), [1]),
        (("themes", 0, "contradicting_fragment_ids"), [1]),
        (("themes", 0, "limitations"), [1]),
        (("customer_insights",), [1]),
        (("customer_insights", 0, "insight_type"), 1),
        (("customer_insights", 0, "statement"), 1),
        (("customer_insights", 0, "audience_segment"), 1),
        (("customer_insights", 0, "usage_context"), 1),
        (("customer_insights", 0, "user_problem_or_need"), 1),
        (("customer_insights", 0, "underlying_reason"), 1),
        (("customer_insights", 0, "behavioral_or_purchase_impact"), 1),
        (("customer_insights", 0, "evidence_coverage"), 1),
        (("customer_insights", 0, "source_scopes"), [1]),
        (("customer_insights", 0, "supporting_fragment_ids"), [1]),
        (("customer_insights", 0, "contradicting_fragment_ids"), [1]),
        (("customer_insights", 0, "dataset_statistic_ids"), [1]),
        (("customer_insights", 0, "customer_language_fragment_ids"), [1]),
        (("customer_insights", 0, "based_on_fact_ids"), [1]),
        (("customer_insights", 0, "limitations"), [1]),
        (("customer_insights", 0, "notes"), [1]),
        (("hypotheses_to_validate",), [1]),
        (("hypotheses_to_validate", 0, "statement"), 1),
        (("hypotheses_to_validate", 0, "audience_segment"), 1),
        (("hypotheses_to_validate", 0, "usage_context"), 1),
        (("hypotheses_to_validate", 0, "user_problem_or_need"), 1),
        (("hypotheses_to_validate", 0, "underlying_reason"), 1),
        (("hypotheses_to_validate", 0, "behavioral_or_purchase_impact"), 1),
        (("hypotheses_to_validate", 0, "source_scopes"), [1]),
        (("hypotheses_to_validate", 0, "supporting_fragment_ids"), [1]),
        (("hypotheses_to_validate", 0, "contradicting_fragment_ids"), [1]),
        (("hypotheses_to_validate", 0, "based_on_fact_ids"), [1]),
        (("hypotheses_to_validate", 0, "validation_needed"), [1]),
        (("hypotheses_to_validate", 0, "limitations"), [1]),
        (("hypotheses_to_validate", 0, "notes"), [1]),
        (("workflow_stage_decision",), 1),
    ],
)
def test_each_frozen_type_and_item_boundary_rejects_wrong_values(
    path: tuple[object, ...], value: object
) -> None:
    payload = _payload_for_path(path)
    _set_path(payload, path, value)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=customer_insight_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("evidence_assessment",),
        ("themes",),
        ("customer_insights",),
        ("hypotheses_to_validate",),
        ("workflow_stage_decision",),
        ("evidence_assessment", "mode"),
        ("evidence_assessment", "evidence_coverage"),
        ("evidence_assessment", "source_types"),
        ("evidence_assessment", "source_set_version_id"),
        ("evidence_assessment", "sample_summary"),
        ("evidence_assessment", "limitations"),
        ("themes", 0, "label"),
        ("themes", 0, "evidence_coverage"),
        ("themes", 0, "source_scopes"),
        ("themes", 0, "supporting_fragment_ids"),
        ("themes", 0, "contradicting_fragment_ids"),
        ("themes", 0, "limitations"),
        ("customer_insights", 0, "insight_type"),
        ("customer_insights", 0, "statement"),
        ("customer_insights", 0, "audience_segment"),
        ("customer_insights", 0, "usage_context"),
        ("customer_insights", 0, "user_problem_or_need"),
        ("customer_insights", 0, "underlying_reason"),
        ("customer_insights", 0, "behavioral_or_purchase_impact"),
        ("customer_insights", 0, "evidence_coverage"),
        ("customer_insights", 0, "source_scopes"),
        ("customer_insights", 0, "supporting_fragment_ids"),
        ("customer_insights", 0, "contradicting_fragment_ids"),
        ("customer_insights", 0, "dataset_statistic_ids"),
        ("customer_insights", 0, "customer_language_fragment_ids"),
        ("customer_insights", 0, "based_on_fact_ids"),
        ("customer_insights", 0, "limitations"),
        ("customer_insights", 0, "notes"),
        ("hypotheses_to_validate", 0, "statement"),
        ("hypotheses_to_validate", 0, "audience_segment"),
        ("hypotheses_to_validate", 0, "usage_context"),
        ("hypotheses_to_validate", 0, "user_problem_or_need"),
        ("hypotheses_to_validate", 0, "underlying_reason"),
        ("hypotheses_to_validate", 0, "behavioral_or_purchase_impact"),
        ("hypotheses_to_validate", 0, "source_scopes"),
        ("hypotheses_to_validate", 0, "supporting_fragment_ids"),
        ("hypotheses_to_validate", 0, "contradicting_fragment_ids"),
        ("hypotheses_to_validate", 0, "based_on_fact_ids"),
        ("hypotheses_to_validate", 0, "validation_needed"),
        ("hypotheses_to_validate", 0, "limitations"),
        ("hypotheses_to_validate", 0, "notes"),
    ],
)
def test_every_non_nullable_field_rejects_null(path: tuple[object, ...]) -> None:
    payload = _payload_for_path(path)
    _set_path(payload, path, None)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=customer_insight_candidate_output_spec()
        )


@pytest.mark.parametrize(
    ("path", "values"),
    [
        (("evidence_assessment", "mode"), ["evidence_backed", "degraded_hypothesis"]),
        (
            ("evidence_assessment", "evidence_coverage"),
            [
                "none",
                "anecdotal",
                "repeated_signal",
                "dataset_supported",
                "multi_source_corroborated",
            ],
        ),
        (
            ("workflow_stage_decision",),
            ["valid", "valid_with_limitations", "waiting_input", "paused", "failed"],
        ),
    ],
)
def test_all_frozen_enum_values_are_accepted(
    path: tuple[object, ...], values: list[str]
) -> None:
    for value in values:
        payload = _candidate_payload("sufficient")
        _set_path(payload, path, value)
        parse_and_validate_structured_output(
            result=_result(payload), spec=customer_insight_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("unexpected",),
        ("evidence_assessment", "unexpected"),
        ("themes", 0, "unexpected"),
        ("customer_insights", 0, "unexpected"),
        ("hypotheses_to_validate", 0, "unexpected"),
    ],
)
def test_every_object_is_closed_against_extra_keys(path: tuple[object, ...]) -> None:
    payload = _payload_for_path(path)
    _set_path(payload, path, True)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=customer_insight_candidate_output_spec()
        )


def test_deep_mappings_are_detached_and_no_cross_field_rule_is_encoded() -> None:
    first = customer_insight_candidate_output_spec()
    second = customer_insight_candidate_output_spec()
    first_mapping = cast(dict[str, object], first.schema.to_mapping())
    second_mapping = cast(dict[str, object], second.schema.to_mapping())
    assert first_mapping == second_mapping
    cast(dict[str, object], first_mapping["properties"])["mutated"] = {}
    assert "mutated" not in cast(dict[str, object], second_mapping["properties"])
    degraded = _candidate_payload("degraded")
    cast(list[object], degraded["themes"]).append({"invalid": "business rule only"})
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(degraded), spec=customer_insight_candidate_output_spec()
        )
