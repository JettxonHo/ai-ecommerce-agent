"""Behavior tests for the Product Positioning candidate-output schema."""

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
from ai_ecommerce_agent.modules.product_positioning.application.skills import (
    product_positioning as _positioning,
)

product_positioning_candidate_output_spec = (
    _positioning.product_positioning_candidate_output_spec
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
        "product_positioning_candidate",
        "v1",
        "skill",
        "domain",
        "profile",
        "v1",
        "context",
    )
    metadata = ProviderCallMetadata(
        ModelCallId("call-product-positioning"),
        (ProviderAttemptId("attempt-product-positioning"),),
        versions,
        "response-product-positioning",
        None,
        ModelTokenUsage(1, 2, 3),
        1,
    )
    return ModelCallResult(
        ModelOutputEnvelope(json.dumps(payload, separators=(",", ":"))), metadata
    )


def _reason(index: int = 1) -> dict[str, object]:
    return {
        "statement": f"fact {index} supports the positioning direction",
        "based_on_fact_ids": [f"fact-{index}"],
        "based_on_insight_ids": [f"insight-{index}"],
    }


def _proof(index: int = 1) -> dict[str, object]:
    return {
        "statement": f"fact {index} documents the relevant product capability",
        "based_on_fact_ids": [f"fact-{index}"],
    }


def _candidate(
    index: int,
    *,
    competitor_only: bool = False,
    hypothesis: bool = False,
) -> dict[str, object]:
    scope = "competitor:anchor" if competitor_only else "current_product"
    return {
        "candidate_id": f"candidate-{index}",
        "candidate_title": f"candidate {index} positioning",
        "strategy_type": "commute-lightweight",
        "target_segment": "daily commuters",
        "target_segment_is_hypothesis": hypothesis,
        "usage_context": "carrying a bottle in a work bag",
        "job_or_core_need": "keep work items dry while commuting",
        "job_or_core_need_is_hypothesis": hypothesis,
        "category_frame": "commuter hydration companion",
        "value_proposition": "a practical way to carry water with less worry",
        "key_benefits": ["easy daily carrying", "reduced spill concern"],
        "differentiation": "focuses on the commute carrying moment",
        "differentiation_is_opportunity_hypothesis": hypothesis,
        "reasons_to_believe": [_reason(index)],
        "proof_points": [_proof(index)],
        "based_on_fact_ids": [f"fact-{index}"],
        "based_on_insight_ids": [f"insight-{index}"],
        "competitor_evidence_ids": [f"{scope}-fragment"] if competitor_only else [],
        "assumptions": ["the carrying moment matters to this audience"],
        "evidence_limitations": ["candidate requires human review"],
        "strategic_risks": ["the audience may value other benefits more"],
        "evidence_profile": "mixed_reference_snapshot",
        "ranking_rationale": "clear fit with the stated commute context",
    }


def _matrix(index: int = 1) -> dict[str, object]:
    return {
        "candidate_id": f"candidate-{index}",
        "target_segment": "daily commuters",
        "core_need": "keep work items dry",
        "primary_value": "less worry during carrying",
        "key_differentiation": "commute-specific positioning",
        "evidence_profile": "mixed_reference_snapshot",
        "main_risk": "the need may not be primary",
    }


def _payload(kind: str = "sufficient") -> dict[str, object]:
    candidates = [_candidate(index) for index in (1, 2, 3)]
    matrix = [_matrix(index) for index in (1, 2, 3)]
    distinct_segments = ["daily commuters", "campus travelers", "weekend cyclists"]
    distinct_needs = [
        "keep work items dry",
        "carry hydration between classes",
        "pack water for outdoor rides",
    ]
    distinct_categories = [
        "commuter hydration companion",
        "campus hydration companion",
        "outdoor hydration companion",
    ]
    distinct_values = [
        "a practical way to carry water with less worry",
        "a simple way to keep hydration close between classes",
        "a dependable way to carry water on short rides",
    ]
    distinct_differentiation = [
        "focuses on the commute carrying moment",
        "focuses on the between-class carrying moment",
        "focuses on the short-ride carrying moment",
    ]
    for index, candidate in enumerate(candidates):
        candidate["target_segment"] = distinct_segments[index]
        candidate["job_or_core_need"] = distinct_needs[index]
        candidate["category_frame"] = distinct_categories[index]
        candidate["value_proposition"] = distinct_values[index]
        candidate["differentiation"] = distinct_differentiation[index]
    context: dict[str, object] = {
        "facts_version_id": "facts-v1",
        "insights_version_id": "insights-v1",
        "competitor_source_set_version_id": "competitor-set-v1",
        "business_constraints": ["do not overclaim superiority"],
        "input_limitations": ["final strategy still requires review"],
    }
    recommendation: dict[str, object] = {
        "recommended_candidate_id": "candidate-1",
        "recommendation_rationale": "candidate one has the clearest evidence path",
        "conditions_for_success": ["validate the audience need"],
        "validation_needed": ["confirm with customer evidence"],
    }
    decision = "ready_for_review"
    if kind == "limited":
        candidates = [_candidate(1, hypothesis=True)]
        matrix = [_matrix(1)]
        context["competitor_source_set_version_id"] = None
        context["input_limitations"] = ["no direct customer evidence"]
        recommendation["recommended_candidate_id"] = None
        recommendation["recommendation_rationale"] = None
        decision = "ready_for_review_with_limitations"
    elif kind == "no_competitor":
        candidates = [_candidate(1)]
        matrix = [_matrix(1)]
        context["competitor_source_set_version_id"] = None
        context["input_limitations"] = ["no competitor evidence was provided"]
        for candidate in candidates:
            candidate["competitor_evidence_ids"] = []
        decision = "ready_for_review_with_limitations"
    elif kind == "competitor_only":
        candidates = [_candidate(1, competitor_only=True, hypothesis=True)]
        matrix = [_matrix(1)]
        context["competitor_source_set_version_id"] = "competitor-set-v1"
        context["input_limitations"] = [
            "competitor signal does not prove product ability"
        ]
        decision = "ready_for_review_with_limitations"
    return {
        "positioning_context": context,
        "positioning_candidates": candidates,
        "comparison_matrix": matrix,
        "recommendation": recommendation,
        "workflow_stage_decision": decision,
    }


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


@pytest.mark.parametrize(
    "kind",
    ["sufficient", "limited", "no_competitor", "competitor_only"],
)
def test_representative_production_shaped_candidates_pass(kind: str) -> None:
    payload = _payload(kind)
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=product_positioning_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


def test_sufficient_candidates_are_materially_distinct() -> None:
    candidates = cast(list[object], _payload()["positioning_candidates"])
    material_fields = (
        "target_segment",
        "job_or_core_need",
        "category_frame",
        "value_proposition",
        "differentiation",
    )
    signatures = {
        tuple(cast(dict[str, object], candidate)[field] for field in material_fields)
        for candidate in candidates
    }
    assert len(signatures) == 3


def test_candidate_and_competitor_boundaries_remain_structural() -> None:
    competitor = _payload("competitor_only")
    candidate = cast(list[object], competitor["positioning_candidates"])[0]
    candidate_mapping = cast(dict[str, object], candidate)
    assert candidate_mapping["target_segment_is_hypothesis"] is True
    assert candidate_mapping["differentiation_is_opportunity_hypothesis"] is True
    assert candidate_mapping["competitor_evidence_ids"] == [
        "competitor:anchor-fragment"
    ]
    assert candidate_mapping["based_on_fact_ids"] == ["fact-1"]
    assert "competitor" not in str(candidate_mapping["differentiation"]).lower()
    assert (
        cast(dict[str, object], competitor["positioning_context"])[
            "competitor_source_set_version_id"
        ]
        == "competitor-set-v1"
    )
    assert all(
        str(token).startswith("competitor:")
        for token in cast(list[object], candidate_mapping["competitor_evidence_ids"])
    )
    assert all(
        str(token).startswith("fact-")
        for token in cast(list[object], candidate_mapping["based_on_fact_ids"])
    )
    parsed = parse_and_validate_structured_output(
        result=_result(competitor), spec=product_positioning_candidate_output_spec()
    )
    assert parsed.to_mapping() == competitor


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_context",),
        ("positioning_candidates",),
        ("comparison_matrix",),
        ("recommendation",),
        ("workflow_stage_decision",),
        ("positioning_context", "facts_version_id"),
        ("positioning_context", "insights_version_id"),
        ("positioning_context", "competitor_source_set_version_id"),
        ("positioning_context", "business_constraints"),
        ("positioning_context", "input_limitations"),
        ("positioning_candidates", 0, "candidate_id"),
        ("positioning_candidates", 0, "candidate_title"),
        ("positioning_candidates", 0, "strategy_type"),
        ("positioning_candidates", 0, "target_segment"),
        ("positioning_candidates", 0, "target_segment_is_hypothesis"),
        ("positioning_candidates", 0, "usage_context"),
        ("positioning_candidates", 0, "job_or_core_need"),
        ("positioning_candidates", 0, "job_or_core_need_is_hypothesis"),
        ("positioning_candidates", 0, "category_frame"),
        ("positioning_candidates", 0, "value_proposition"),
        ("positioning_candidates", 0, "differentiation"),
        (
            "positioning_candidates",
            0,
            "differentiation_is_opportunity_hypothesis",
        ),
        ("positioning_candidates", 0, "key_benefits"),
        ("positioning_candidates", 0, "reasons_to_believe"),
        ("positioning_candidates", 0, "proof_points"),
        ("positioning_candidates", 0, "based_on_fact_ids"),
        ("positioning_candidates", 0, "based_on_insight_ids"),
        ("positioning_candidates", 0, "competitor_evidence_ids"),
        ("positioning_candidates", 0, "assumptions"),
        ("positioning_candidates", 0, "evidence_limitations"),
        ("positioning_candidates", 0, "strategic_risks"),
        ("positioning_candidates", 0, "evidence_profile"),
        ("positioning_candidates", 0, "ranking_rationale"),
        ("positioning_candidates", 0, "reasons_to_believe", 0, "statement"),
        (
            "positioning_candidates",
            0,
            "reasons_to_believe",
            0,
            "based_on_fact_ids",
        ),
        (
            "positioning_candidates",
            0,
            "reasons_to_believe",
            0,
            "based_on_insight_ids",
        ),
        ("positioning_candidates", 0, "proof_points", 0, "statement"),
        (
            "positioning_candidates",
            0,
            "proof_points",
            0,
            "based_on_fact_ids",
        ),
        ("comparison_matrix", 0, "candidate_id"),
        ("comparison_matrix", 0, "target_segment"),
        ("comparison_matrix", 0, "core_need"),
        ("comparison_matrix", 0, "primary_value"),
        ("comparison_matrix", 0, "key_differentiation"),
        ("comparison_matrix", 0, "evidence_profile"),
        ("comparison_matrix", 0, "main_risk"),
        ("recommendation", "recommended_candidate_id"),
        ("recommendation", "recommendation_rationale"),
        ("recommendation", "conditions_for_success"),
        ("recommendation", "validation_needed"),
    ],
)
def test_required_and_array_fields_reject_missing(path: tuple[object, ...]) -> None:
    payload = _payload()
    _delete_path(payload, path)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_context",),
        ("positioning_candidates",),
        ("comparison_matrix",),
        ("recommendation",),
        ("workflow_stage_decision",),
        ("positioning_context", "facts_version_id"),
        ("positioning_context", "insights_version_id"),
        ("positioning_context", "business_constraints"),
        ("positioning_context", "input_limitations"),
        ("positioning_candidates", 0, "candidate_id"),
        ("positioning_candidates", 0, "candidate_title"),
        ("positioning_candidates", 0, "strategy_type"),
        ("positioning_candidates", 0, "target_segment"),
        ("positioning_candidates", 0, "target_segment_is_hypothesis"),
        ("positioning_candidates", 0, "usage_context"),
        ("positioning_candidates", 0, "job_or_core_need"),
        ("positioning_candidates", 0, "job_or_core_need_is_hypothesis"),
        ("positioning_candidates", 0, "category_frame"),
        ("positioning_candidates", 0, "value_proposition"),
        ("positioning_candidates", 0, "key_benefits"),
        ("positioning_candidates", 0, "differentiation"),
        (
            "positioning_candidates",
            0,
            "differentiation_is_opportunity_hypothesis",
        ),
        ("positioning_candidates", 0, "reasons_to_believe"),
        ("positioning_candidates", 0, "proof_points"),
        ("positioning_candidates", 0, "based_on_fact_ids"),
        ("positioning_candidates", 0, "based_on_insight_ids"),
        ("positioning_candidates", 0, "competitor_evidence_ids"),
        ("positioning_candidates", 0, "assumptions"),
        ("positioning_candidates", 0, "evidence_limitations"),
        ("positioning_candidates", 0, "strategic_risks"),
        ("positioning_candidates", 0, "evidence_profile"),
        ("positioning_candidates", 0, "ranking_rationale"),
        ("positioning_candidates", 0, "reasons_to_believe", 0, "statement"),
        (
            "positioning_candidates",
            0,
            "reasons_to_believe",
            0,
            "based_on_fact_ids",
        ),
        (
            "positioning_candidates",
            0,
            "reasons_to_believe",
            0,
            "based_on_insight_ids",
        ),
        ("positioning_candidates", 0, "proof_points", 0, "statement"),
        (
            "positioning_candidates",
            0,
            "proof_points",
            0,
            "based_on_fact_ids",
        ),
        ("comparison_matrix", 0, "candidate_id"),
        ("comparison_matrix", 0, "target_segment"),
        ("comparison_matrix", 0, "core_need"),
        ("comparison_matrix", 0, "primary_value"),
        ("comparison_matrix", 0, "key_differentiation"),
        ("comparison_matrix", 0, "evidence_profile"),
        ("recommendation", "conditions_for_success"),
        ("recommendation", "validation_needed"),
    ],
)
def test_all_nonnullable_paths_reject_null(path: tuple[object, ...]) -> None:
    payload = _payload()
    _set_path(payload, path, None)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_context", "facts_version_id"),
        ("positioning_context", "insights_version_id"),
        ("positioning_context", "business_constraints"),
        ("positioning_context", "input_limitations"),
        ("positioning_candidates", 0, "candidate_id"),
        ("positioning_candidates", 0, "candidate_title"),
        ("positioning_candidates", 0, "strategy_type"),
        ("positioning_candidates", 0, "target_segment"),
        ("positioning_candidates", 0, "usage_context"),
        ("positioning_candidates", 0, "job_or_core_need"),
        ("positioning_candidates", 0, "category_frame"),
        ("positioning_candidates", 0, "value_proposition"),
        ("positioning_candidates", 0, "differentiation"),
        ("positioning_candidates", 0, "evidence_profile"),
        ("positioning_candidates", 0, "ranking_rationale"),
        ("positioning_candidates", 0, "reasons_to_believe", 0, "statement"),
        ("positioning_candidates", 0, "proof_points", 0, "statement"),
        ("comparison_matrix", 0, "candidate_id"),
        ("comparison_matrix", 0, "target_segment"),
        ("comparison_matrix", 0, "core_need"),
        ("comparison_matrix", 0, "primary_value"),
        ("comparison_matrix", 0, "key_differentiation"),
        ("comparison_matrix", 0, "evidence_profile"),
        ("recommendation", "conditions_for_success"),
        ("recommendation", "validation_needed"),
    ],
)
def test_wrong_scalar_or_array_type_is_rejected(path: tuple[object, ...]) -> None:
    payload = _payload()
    _set_path(payload, path, 1)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_candidates", 0, "target_segment_is_hypothesis"),
        ("positioning_candidates", 0, "job_or_core_need_is_hypothesis"),
        ("positioning_candidates", 0, "differentiation_is_opportunity_hypothesis"),
    ],
)
def test_boolean_fields_reject_non_boolean_values(path: tuple[object, ...]) -> None:
    payload = _payload()
    _set_path(payload, path, "true")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_context", "business_constraints"),
        ("positioning_context", "input_limitations"),
        ("positioning_candidates",),
        ("positioning_candidates", 0, "key_benefits"),
        ("positioning_candidates", 0, "reasons_to_believe"),
        ("positioning_candidates", 0, "proof_points"),
        ("positioning_candidates", 0, "based_on_fact_ids"),
        ("positioning_candidates", 0, "based_on_insight_ids"),
        ("positioning_candidates", 0, "competitor_evidence_ids"),
        ("positioning_candidates", 0, "assumptions"),
        ("positioning_candidates", 0, "evidence_limitations"),
        ("positioning_candidates", 0, "strategic_risks"),
        (
            "positioning_candidates",
            0,
            "reasons_to_believe",
            0,
            "based_on_fact_ids",
        ),
        (
            "positioning_candidates",
            0,
            "reasons_to_believe",
            0,
            "based_on_insight_ids",
        ),
        ("positioning_candidates", 0, "proof_points", 0, "based_on_fact_ids"),
        ("comparison_matrix",),
        ("recommendation", "conditions_for_success"),
        ("recommendation", "validation_needed"),
    ],
)
def test_array_fields_reject_wrong_container_and_item_types(
    path: tuple[object, ...],
) -> None:
    payload = _payload()
    _set_path(payload, path, "not-an-array")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )
    payload = _payload()
    if path == ("positioning_candidates",):
        _set_path(payload, path, ["not-an-object"])
    elif path == ("comparison_matrix",):
        _set_path(payload, path, ["not-an-object"])
    elif path[-1] in {"reasons_to_believe", "proof_points"}:
        _set_path(payload, path, [{"bad": "item"}])
    else:
        _set_path(payload, path, [1])
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_candidates", 0, "reasons_to_believe"),
        ("positioning_candidates", 0, "proof_points"),
    ],
)
def test_object_arrays_reject_scalar_items(path: tuple[object, ...]) -> None:
    payload = _payload()
    _set_path(payload, path, [1])
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_candidates", 0, "based_on_fact_ids"),
        ("positioning_candidates", 0, "proof_points", 0, "based_on_fact_ids"),
    ],
)
def test_minimum_fact_references_reject_empty_arrays(path: tuple[object, ...]) -> None:
    payload = _payload()
    _set_path(payload, path, [])
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_context", "facts_version_id"),
        ("positioning_candidates", 0, "candidate_title"),
        ("positioning_candidates", 0, "strategy_type"),
        ("positioning_candidates", 0, "key_benefits", 0),
        ("comparison_matrix", 0, "main_risk"),
        ("recommendation", "recommendation_rationale"),
    ],
)
def test_nonblank_string_boundaries_reject_whitespace(path: tuple[object, ...]) -> None:
    payload = _payload()
    _set_path(payload, path, "   ")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_context", "facts_version_id"),
        ("positioning_context", "insights_version_id"),
        ("positioning_context", "competitor_source_set_version_id"),
        ("positioning_context", "business_constraints", 0),
        ("positioning_context", "input_limitations", 0),
        ("positioning_candidates", 0, "candidate_id"),
        ("positioning_candidates", 0, "candidate_title"),
        ("positioning_candidates", 0, "strategy_type"),
        ("positioning_candidates", 0, "target_segment"),
        ("positioning_candidates", 0, "usage_context"),
        ("positioning_candidates", 0, "job_or_core_need"),
        ("positioning_candidates", 0, "category_frame"),
        ("positioning_candidates", 0, "value_proposition"),
        ("positioning_candidates", 0, "key_benefits", 0),
        ("positioning_candidates", 0, "differentiation"),
        ("positioning_candidates", 0, "based_on_fact_ids", 0),
        ("positioning_candidates", 0, "based_on_insight_ids", 0),
        ("positioning_candidates", 0, "competitor_evidence_ids", 0),
        ("positioning_candidates", 0, "assumptions", 0),
        ("positioning_candidates", 0, "evidence_limitations", 0),
        ("positioning_candidates", 0, "strategic_risks", 0),
        ("positioning_candidates", 0, "evidence_profile"),
        ("positioning_candidates", 0, "ranking_rationale"),
        ("positioning_candidates", 0, "reasons_to_believe", 0, "statement"),
        (
            "positioning_candidates",
            0,
            "reasons_to_believe",
            0,
            "based_on_fact_ids",
            0,
        ),
        (
            "positioning_candidates",
            0,
            "reasons_to_believe",
            0,
            "based_on_insight_ids",
            0,
        ),
        ("positioning_candidates", 0, "proof_points", 0, "statement"),
        (
            "positioning_candidates",
            0,
            "proof_points",
            0,
            "based_on_fact_ids",
            0,
        ),
        ("comparison_matrix", 0, "candidate_id"),
        ("comparison_matrix", 0, "target_segment"),
        ("comparison_matrix", 0, "core_need"),
        ("comparison_matrix", 0, "primary_value"),
        ("comparison_matrix", 0, "key_differentiation"),
        ("comparison_matrix", 0, "evidence_profile"),
        ("comparison_matrix", 0, "main_risk"),
        ("recommendation", "recommended_candidate_id"),
        ("recommendation", "recommendation_rationale"),
        ("recommendation", "conditions_for_success", 0),
        ("recommendation", "validation_needed", 0),
        ("workflow_stage_decision",),
    ],
)
def test_every_nonblank_string_path_rejects_whitespace(
    path: tuple[object, ...],
) -> None:
    payload = _payload(
        "competitor_only" if "competitor_evidence_ids" in path else "sufficient"
    )
    _set_path(payload, path, "   ")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        (),
        ("positioning_context",),
        ("positioning_candidates", 0),
        ("positioning_candidates", 0, "reasons_to_believe", 0),
        ("positioning_candidates", 0, "proof_points", 0),
        ("comparison_matrix", 0),
        ("recommendation",),
    ],
)
def test_every_object_layer_rejects_extra_keys(path: tuple[object, ...]) -> None:
    payload = _payload()
    current: Any = payload
    for key in path:
        current = current[key]
    current["extra"] = "not permitted"
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


def test_nullable_fields_accept_null_without_encoding_membership_rules() -> None:
    payload = _payload("no_competitor")
    recommendation = cast(dict[str, object], payload["recommendation"])
    recommendation["recommended_candidate_id"] = None
    recommendation["recommendation_rationale"] = None
    matrix = cast(list[object], payload["comparison_matrix"])[0]
    cast(dict[str, object], matrix)["main_risk"] = None
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=product_positioning_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    "path",
    [
        ("positioning_context", "competitor_source_set_version_id"),
        ("comparison_matrix", 0, "main_risk"),
        ("recommendation", "recommended_candidate_id"),
        ("recommendation", "recommendation_rationale"),
    ],
)
def test_nullable_string_fields_reject_non_string_non_null(
    path: tuple[object, ...],
) -> None:
    payload = _payload()
    _set_path(payload, path, 1)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )


def test_stage_enum_rejects_unknown_values() -> None:
    payload = _payload()
    payload["workflow_stage_decision"] = "approved"
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_positioning_candidate_output_spec()
        )
