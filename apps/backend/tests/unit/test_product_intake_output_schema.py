"""Behavior tests for the Product Intake candidate output schema."""

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
from ai_ecommerce_agent.modules.product_intake.application.skills import (
    product_intake_fact_extraction as _fact_extraction,
)

ProductIntakeAssertionType = _fact_extraction.ProductIntakeAssertionType
ProductIntakeCompletenessLevel = _fact_extraction.ProductIntakeCompletenessLevel
product_intake_candidate_output_spec = (
    _fact_extraction.product_intake_candidate_output_spec
)

pytestmark = pytest.mark.unit


def _result(payload: dict[str, object]) -> ModelCallResult:
    call_id = ModelCallId("call-product-intake")
    versions = ModelRuntimeVersionTuple(
        "provider",
        "responses",
        "sdk",
        "configured",
        None,
        "prompt",
        "v1",
        "product_intake_fact_candidate",
        "v1",
        "skill",
        "domain",
        "profile",
        "v1",
        "context",
    )
    metadata = ProviderCallMetadata(
        call_id,
        (ProviderAttemptId("attempt-product-intake"),),
        versions,
        "response-product-intake",
        None,
        ModelTokenUsage(1, 2, 3),
        1,
    )
    return ModelCallResult(
        ModelOutputEnvelope(json.dumps(payload, separators=(",", ":"))), metadata
    )


def _candidate_payload(kind: str) -> dict[str, object]:
    fact = {
        "category": "materials_and_components",
        "attribute_key": "material",
        "raw_value": "304 stainless steel",
        "normalized_value": "304 stainless steel",
        "unit": None,
        "assertion_type": ProductIntakeAssertionType.DIRECT_FACT.value,
        "supporting_fragment_ids": ["fragment-1"],
        "contradicting_fragment_ids": [],
        "notes": [],
    }
    base: dict[str, object] = {
        "intake_assessment": {
            "completeness_level": ProductIntakeCompletenessLevel.STANDARD.value,
            "runnable": True,
            "available_source_types": ["manual_input", "uploaded_document"],
            "excluded_sources": [],
            "missing_information": [],
            "warnings": [],
        },
        "fact_candidates": [fact],
        "claims_requiring_verification": [
            {
                "claim_text": "Keeps drinks cold for twelve hours",
                "supporting_fragment_ids": ["fragment-2"],
                "verification_need": "requires test report",
                "notes": [],
            }
        ],
        "conflicts_and_limitations": {
            "source_conflicts": [],
            "evidence_limitations": [],
            "insufficient_information": [],
            "hypotheses_to_validate": [],
        },
        "workflow_stage_decision": "valid",
    }
    if kind == "limited":
        cast(dict[str, object], base["intake_assessment"])["completeness_level"] = (
            "minimal"
        )
        cast(dict[str, object], base["intake_assessment"])["available_source_types"] = [
            "manual_input"
        ]
        cast(dict[str, object], base["intake_assessment"])["missing_information"] = [
            "usage conditions"
        ]
        cast(dict[str, object], base["intake_assessment"])["warnings"] = [
            "limited source coverage"
        ]
    elif kind == "blocking":
        assessment = cast(dict[str, object], base["intake_assessment"])
        assessment.update(
            {
                "completeness_level": "insufficient",
                "runnable": False,
            }
        )
        cast(dict[str, object], base["conflicts_and_limitations"])[
            "source_conflicts"
        ] = [
            {
                "conflict_kind": "sku",
                "attribute_key": "capacity",
                "observed_values": [
                    {"raw_value": "500 ml", "fragment_ids": ["fragment-3"]},
                    {"raw_value": "750 ml", "fragment_ids": ["fragment-4"]},
                ],
                "blocking": True,
                "impact": "cannot identify the active variant",
            }
        ]
        base["workflow_stage_decision"] = "waiting_input"
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
    if path[:2] == ("conflicts_and_limitations", "source_conflicts"):
        return _candidate_payload("blocking")
    return _candidate_payload("sufficient")


@pytest.mark.parametrize("kind", ["sufficient", "limited", "blocking"])
def test_production_shaped_payloads_pass_existing_validator(kind: str) -> None:
    parsed = parse_and_validate_structured_output(
        result=_result(_candidate_payload(kind)),
        spec=product_intake_candidate_output_spec(),
    )
    assert parsed.to_mapping() == _candidate_payload(kind)


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("workflow_stage_decision",), "unsupported"),
        (("intake_assessment", "completeness_level"), "unsupported"),
        (("intake_assessment", "runnable"), "yes"),
        (("fact_candidates", 0, "raw_value"), ""),
        (("fact_candidates", 0, "normalized_value"), 3),
        (("fact_candidates", 0, "supporting_fragment_ids"), []),
        (("fact_candidates", 0, "supporting_fragment_ids", 0), ""),
        (("claims_requiring_verification", 0, "supporting_fragment_ids"), []),
        (
            (
                "conflicts_and_limitations",
                "source_conflicts",
                0,
                "observed_values",
            ),
            [],
        ),
        (
            (
                "conflicts_and_limitations",
                "source_conflicts",
                0,
                "observed_values",
                0,
                "fragment_ids",
            ),
            [],
        ),
    ],
)
def test_single_mutations_are_rejected(path: tuple[object, ...], value: object) -> None:
    payload = _payload_for_path(path)
    _set_path(payload, path, value)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_intake_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("extra",),
        ("intake_assessment", "extra"),
        ("fact_candidates", 0, "extra"),
        ("claims_requiring_verification", 0, "extra"),
        ("conflicts_and_limitations", "extra"),
        ("conflicts_and_limitations", "source_conflicts", 0, "extra"),
        (
            "conflicts_and_limitations",
            "source_conflicts",
            0,
            "observed_values",
            0,
            "extra",
        ),
    ],
)
def test_every_object_is_closed_against_extra_keys(path: tuple[object, ...]) -> None:
    payload = _payload_for_path(path)
    _set_path(payload, path, True)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_intake_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("intake_assessment",),
        ("fact_candidates",),
        ("claims_requiring_verification",),
        ("conflicts_and_limitations",),
        ("workflow_stage_decision",),
        ("intake_assessment", "completeness_level"),
        ("intake_assessment", "runnable"),
        ("intake_assessment", "available_source_types"),
        ("intake_assessment", "excluded_sources"),
        ("intake_assessment", "missing_information"),
        ("intake_assessment", "warnings"),
        ("fact_candidates", 0, "category"),
        ("fact_candidates", 0, "attribute_key"),
        ("fact_candidates", 0, "raw_value"),
        ("fact_candidates", 0, "normalized_value"),
        ("fact_candidates", 0, "unit"),
        ("fact_candidates", 0, "assertion_type"),
        ("fact_candidates", 0, "supporting_fragment_ids"),
        ("fact_candidates", 0, "contradicting_fragment_ids"),
        ("fact_candidates", 0, "notes"),
        ("claims_requiring_verification", 0, "claim_text"),
        ("claims_requiring_verification", 0, "supporting_fragment_ids"),
        ("claims_requiring_verification", 0, "verification_need"),
        ("claims_requiring_verification", 0, "notes"),
        ("conflicts_and_limitations", "source_conflicts"),
        ("conflicts_and_limitations", "evidence_limitations"),
        ("conflicts_and_limitations", "insufficient_information"),
        ("conflicts_and_limitations", "hypotheses_to_validate"),
        (
            "conflicts_and_limitations",
            "source_conflicts",
            0,
            "conflict_kind",
        ),
        (
            "conflicts_and_limitations",
            "source_conflicts",
            0,
            "attribute_key",
        ),
        (
            "conflicts_and_limitations",
            "source_conflicts",
            0,
            "observed_values",
        ),
        (
            "conflicts_and_limitations",
            "source_conflicts",
            0,
            "blocking",
        ),
        ("conflicts_and_limitations", "source_conflicts", 0, "impact"),
        (
            "conflicts_and_limitations",
            "source_conflicts",
            0,
            "observed_values",
            0,
            "raw_value",
        ),
        (
            "conflicts_and_limitations",
            "source_conflicts",
            0,
            "observed_values",
            0,
            "fragment_ids",
        ),
    ],
)
def test_every_frozen_required_field_is_required(path: tuple[object, ...]) -> None:
    payload = _payload_for_path(path)
    _delete_path(payload, path)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_intake_candidate_output_spec()
        )


@pytest.mark.parametrize(
    ("path", "values"),
    [
        (
            ("intake_assessment", "completeness_level"),
            ["insufficient", "minimal", "standard", "evidence_rich"],
        ),
        (
            ("fact_candidates", 0, "assertion_type"),
            [
                "direct_fact",
                "documented_claim",
                "certified_or_tested_fact",
                "marketing_expression",
                "unknown_or_ambiguous",
            ],
        ),
        (
            ("workflow_stage_decision",),
            ["valid", "waiting_input", "paused", "failed"],
        ),
    ],
)
def test_all_frozen_enum_values_are_accepted(
    path: tuple[object, ...], values: list[str]
) -> None:
    for value in values:
        payload = _candidate_payload("sufficient")
        _set_path(payload, path, value)
        parsed = parse_and_validate_structured_output(
            result=_result(payload), spec=product_intake_candidate_output_spec()
        )
        assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("intake_assessment", "available_source_types", 0), 1),
        (("intake_assessment", "excluded_sources"), [1]),
        (("fact_candidates", 0, "supporting_fragment_ids", 0), 1),
        (("fact_candidates", 0, "contradicting_fragment_ids"), [False]),
        (("claims_requiring_verification", 0, "supporting_fragment_ids"), [None]),
        (("conflicts_and_limitations", "source_conflicts"), {}),
        (
            ("conflicts_and_limitations", "source_conflicts", 0, "conflict_kind"),
            1,
        ),
        (
            ("conflicts_and_limitations", "source_conflicts", 0, "attribute_key"),
            None,
        ),
        (
            (
                "conflicts_and_limitations",
                "source_conflicts",
                0,
                "observed_values",
            ),
            {},
        ),
        (
            ("conflicts_and_limitations", "source_conflicts", 0, "blocking"),
            "yes",
        ),
        (
            ("conflicts_and_limitations", "source_conflicts", 0, "impact"),
            1,
        ),
        (
            (
                "conflicts_and_limitations",
                "source_conflicts",
                0,
                "observed_values",
                0,
                "raw_value",
            ),
            1,
        ),
        (
            (
                "conflicts_and_limitations",
                "source_conflicts",
                0,
                "observed_values",
                0,
                "fragment_ids",
            ),
            [1],
        ),
        (
            (
                "conflicts_and_limitations",
                "source_conflicts",
                0,
                "observed_values",
            ),
            [{"raw_value": "500 ml", "fragment_ids": ["fragment-3"]}],
        ),
    ],
)
def test_nested_types_and_fragment_tokens_are_strict(
    path: tuple[object, ...], value: object
) -> None:
    payload = _payload_for_path(path)
    _set_path(payload, path, value)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_intake_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path", [("fact_candidates", 0, "normalized_value"), ("fact_candidates", 0, "unit")]
)
def test_nullable_boundaries_accept_null_but_reject_blank_text(
    path: tuple[object, ...],
) -> None:
    payload = _candidate_payload("sufficient")
    _set_path(payload, path, None)
    parse_and_validate_structured_output(
        result=_result(payload), spec=product_intake_candidate_output_spec()
    )
    _set_path(payload, path, "   ")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=product_intake_candidate_output_spec()
        )


def test_claims_and_marketing_expressions_remain_candidates_not_verified_facts() -> (
    None
):
    payload = _candidate_payload("sufficient")
    fact = cast(list[object], payload["fact_candidates"])[0]
    cast(dict[str, object], fact)["assertion_type"] = "marketing_expression"
    cast(list[object], payload["claims_requiring_verification"])[0] = {
        "claim_text": "Certified leakproof",
        "supporting_fragment_ids": ["fragment-claim"],
        "verification_need": "requires certification",
        "notes": [],
    }
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=product_intake_candidate_output_spec()
    )
    output = parsed.to_mapping()
    assert (
        cast(list[object], output["fact_candidates"])[0]
        == cast(list[object], payload["fact_candidates"])[0]
    )
    assert "verified" not in cast(dict[str, object], output).keys()
