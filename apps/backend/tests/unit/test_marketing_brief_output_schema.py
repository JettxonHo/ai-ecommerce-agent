"""Behavior tests for the Marketing Brief candidate-output schema."""

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
from ai_ecommerce_agent.modules.marketing_brief.application.skills import (
    marketing_brief_generation as _brief,
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
        "marketing_brief_candidate",
        "v1",
        "skill",
        "domain",
        "profile",
        "v1",
        "context",
    )
    metadata = ProviderCallMetadata(
        ModelCallId("call-marketing-brief"),
        (ProviderAttemptId("attempt-marketing-brief"),),
        versions,
        "response-marketing-brief",
        None,
        ModelTokenUsage(1, 2, 3),
        1,
    )
    return ModelCallResult(
        ModelOutputEnvelope(json.dumps(payload, separators=(",", ":"))), metadata
    )


def _candidate(kind: str = "valid") -> dict[str, object]:
    limited = kind == "limited"
    return {
        "objective_and_audience": {
            "communication_objective": {
                "primary_objective": "make the daily commute feel simpler",
                "secondary_objectives": ["make the benefit easy to remember"],
                "business_assumption": True,
            },
            "audience": "daily urban commuters",
            "audience_context": ["carry a bottle between work and transit"],
            "audience_is_hypothesis": limited,
        },
        "message_architecture": {
            "core_message": "carry hydration with less daily friction",
            "message_hierarchy": {
                "primary_message": "a calmer commute starts with simple carrying",
                "secondary_benefits": ["easy access", "less spill worry"],
                "supporting_proof_points": ["fact-commute-1"],
            },
            "benefit_hierarchy": {
                "primary_benefit": "less worry while moving through the day",
                "secondary_benefits": ["quick access"],
                "supporting_features": ["compact bottle sleeve"],
            },
        },
        "reasons_to_believe_and_evidence": {
            "reasons_to_believe": [
                {
                    "statement": "commuters asked for easier bottle access",
                    "based_on_fact_ids": ["fact-commute-1"],
                    "based_on_insight_ids": ["insight-commute-1"],
                }
            ],
            "proof_points": [
                {
                    "proof_point": "the sleeve keeps the bottle within reach",
                    "fact_id": "fact-commute-1",
                    "supporting_fragment_ids": ["fragment-commute-1"],
                    "source_version_id": "source-v1",
                    "approved_wording": "within easy reach",
                }
            ],
        },
        "execution_direction": {
            "objections": ["the audience may already own a bottle"],
            "objection_responses": [
                {
                    "objection": "the audience may already own a bottle",
                    "response": "focus on the carrying experience, not replacement",
                    "based_on_fact_ids": ["fact-commute-1"],
                    "based_on_insight_ids": ["insight-commute-1"],
                    "insufficient_evidence": limited,
                }
            ],
            "content_angles": [
                {
                    "angle_title": "the calm commute angle",
                    "angle_type": "daily_routine",
                    "user_tension": "commuting leaves little room for fumbling",
                    "message_focus": "keep hydration simple",
                    "supporting_benefits": ["easy access"],
                    "proof_points": ["within easy reach"],
                    "hypothesis_status": "hypothesis" if limited else "supported",
                    "requires_validation": limited,
                    "risk_notes": ["avoid claiming universal preference"],
                }
            ],
            "tone_and_voice": {
                "tone": "calm",
                "voice": "practical",
                "suggested_tone": limited,
            },
            "call_to_action_objective": "invite the audience to simplify carrying",
        },
        "constraints_and_honesty": {
            "mandatory_messages": ["keep the claim commute-specific"],
            "prohibited_claims": ["never claim the best solution"],
            "accepted_hypotheses": ["easy access matters to commuters"],
            "hypotheses_to_test": ["test the carrying preference"],
            "evidence_limitations": (
                ["limited direct customer evidence"] if limited else []
            ),
            "risk_notes": ["do not overstate evidence"],
            "platform_adaptation_rules": ["keep the structure platform-neutral"],
        },
    }


def _payload(kind: str = "valid") -> dict[str, object]:
    decision = {
        "valid": "valid",
        "limited": "valid_with_limitations",
        "strategy_change_required": "strategy_change_required",
        "waiting_input": "waiting_input",
        "paused": "paused",
        "failed": "failed",
    }[kind]
    return {
        "brief_candidate": None
        if kind in {"strategy_change_required", "waiting_input", "paused", "failed"}
        else _candidate(kind),
        "version_and_workflow_context": {
            "approved_strategy_version_id": "strategy-v1",
            "facts_version_id": "facts-v1",
            "insights_version_id": "insights-v1",
            "input_limitations": ["reference tokens are opaque"],
            "stage_decision": decision,
        },
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


def _schema() -> dict[str, object]:
    return cast(
        dict[str, object],
        _brief.marketing_brief_candidate_output_spec().schema.to_mapping(),
    )


_OBJECT_FIELDS: dict[tuple[object, ...], list[str]] = {
    (): ["brief_candidate", "version_and_workflow_context"],
    ("brief_candidate",): [
        "objective_and_audience",
        "message_architecture",
        "reasons_to_believe_and_evidence",
        "execution_direction",
        "constraints_and_honesty",
    ],
    ("brief_candidate", "objective_and_audience"): [
        "communication_objective",
        "audience",
        "audience_context",
        "audience_is_hypothesis",
    ],
    (
        "brief_candidate",
        "objective_and_audience",
        "communication_objective",
    ): ["primary_objective", "secondary_objectives", "business_assumption"],
    ("brief_candidate", "message_architecture"): [
        "core_message",
        "message_hierarchy",
        "benefit_hierarchy",
    ],
    ("brief_candidate", "message_architecture", "message_hierarchy"): [
        "primary_message",
        "secondary_benefits",
        "supporting_proof_points",
    ],
    ("brief_candidate", "message_architecture", "benefit_hierarchy"): [
        "primary_benefit",
        "secondary_benefits",
        "supporting_features",
    ],
    ("brief_candidate", "reasons_to_believe_and_evidence"): [
        "reasons_to_believe",
        "proof_points",
    ],
    (
        "brief_candidate",
        "reasons_to_believe_and_evidence",
        "reasons_to_believe",
        0,
    ): ["statement", "based_on_fact_ids", "based_on_insight_ids"],
    (
        "brief_candidate",
        "reasons_to_believe_and_evidence",
        "proof_points",
        0,
    ): [
        "proof_point",
        "fact_id",
        "supporting_fragment_ids",
        "source_version_id",
        "approved_wording",
    ],
    ("brief_candidate", "execution_direction"): [
        "objections",
        "objection_responses",
        "content_angles",
        "tone_and_voice",
        "call_to_action_objective",
    ],
    ("brief_candidate", "execution_direction", "objection_responses", 0): [
        "objection",
        "response",
        "based_on_fact_ids",
        "based_on_insight_ids",
        "insufficient_evidence",
    ],
    ("brief_candidate", "execution_direction", "content_angles", 0): [
        "angle_title",
        "angle_type",
        "user_tension",
        "message_focus",
        "supporting_benefits",
        "proof_points",
        "hypothesis_status",
        "requires_validation",
        "risk_notes",
    ],
    ("brief_candidate", "execution_direction", "tone_and_voice"): [
        "tone",
        "voice",
        "suggested_tone",
    ],
    ("brief_candidate", "constraints_and_honesty"): [
        "mandatory_messages",
        "prohibited_claims",
        "accepted_hypotheses",
        "hypotheses_to_test",
        "evidence_limitations",
        "risk_notes",
        "platform_adaptation_rules",
    ],
    ("version_and_workflow_context",): [
        "approved_strategy_version_id",
        "facts_version_id",
        "insights_version_id",
        "input_limitations",
        "stage_decision",
    ],
}

_ARRAY_PATHS: tuple[tuple[object, ...], ...] = (
    (
        "brief_candidate",
        "objective_and_audience",
        "communication_objective",
        "secondary_objectives",
    ),
    ("brief_candidate", "objective_and_audience", "audience_context"),
    (
        "brief_candidate",
        "message_architecture",
        "message_hierarchy",
        "secondary_benefits",
    ),
    (
        "brief_candidate",
        "message_architecture",
        "message_hierarchy",
        "supporting_proof_points",
    ),
    (
        "brief_candidate",
        "message_architecture",
        "benefit_hierarchy",
        "secondary_benefits",
    ),
    (
        "brief_candidate",
        "message_architecture",
        "benefit_hierarchy",
        "supporting_features",
    ),
    ("brief_candidate", "reasons_to_believe_and_evidence", "reasons_to_believe"),
    (
        "brief_candidate",
        "reasons_to_believe_and_evidence",
        "reasons_to_believe",
        0,
        "based_on_fact_ids",
    ),
    (
        "brief_candidate",
        "reasons_to_believe_and_evidence",
        "reasons_to_believe",
        0,
        "based_on_insight_ids",
    ),
    ("brief_candidate", "reasons_to_believe_and_evidence", "proof_points"),
    (
        "brief_candidate",
        "reasons_to_believe_and_evidence",
        "proof_points",
        0,
        "supporting_fragment_ids",
    ),
    ("brief_candidate", "execution_direction", "objections"),
    ("brief_candidate", "execution_direction", "objection_responses"),
    (
        "brief_candidate",
        "execution_direction",
        "objection_responses",
        0,
        "based_on_fact_ids",
    ),
    (
        "brief_candidate",
        "execution_direction",
        "objection_responses",
        0,
        "based_on_insight_ids",
    ),
    ("brief_candidate", "execution_direction", "content_angles"),
    (
        "brief_candidate",
        "execution_direction",
        "content_angles",
        0,
        "supporting_benefits",
    ),
    (
        "brief_candidate",
        "execution_direction",
        "content_angles",
        0,
        "proof_points",
    ),
    (
        "brief_candidate",
        "execution_direction",
        "content_angles",
        0,
        "risk_notes",
    ),
    ("brief_candidate", "constraints_and_honesty", "mandatory_messages"),
    ("brief_candidate", "constraints_and_honesty", "prohibited_claims"),
    ("brief_candidate", "constraints_and_honesty", "accepted_hypotheses"),
    ("brief_candidate", "constraints_and_honesty", "hypotheses_to_test"),
    ("brief_candidate", "constraints_and_honesty", "evidence_limitations"),
    ("brief_candidate", "constraints_and_honesty", "risk_notes"),
    (
        "brief_candidate",
        "constraints_and_honesty",
        "platform_adaptation_rules",
    ),
    ("version_and_workflow_context", "input_limitations"),
)


def _object_schema_at(path: tuple[object, ...]) -> dict[str, object]:
    current = _schema()
    for key in path:
        if isinstance(key, int):
            current = cast(dict[str, object], current["items"])
        else:
            assert isinstance(key, str)
            properties = cast(dict[str, object], current["properties"])
            current = cast(dict[str, object], properties[key])
    return current


def _schema_node_at(path: tuple[object, ...]) -> dict[str, object]:
    current = _schema()
    for key in path:
        if isinstance(key, int):
            current = cast(dict[str, object], current["items"])
        else:
            assert isinstance(key, str)
            properties = cast(dict[str, object], current["properties"])
            current = cast(dict[str, object], properties[key])
    return current


def _candidate_paths() -> list[tuple[object, ...]]:
    return [
        ("brief_candidate",),
        ("brief_candidate", "objective_and_audience"),
        ("brief_candidate", "objective_and_audience", "communication_objective"),
        (
            "brief_candidate",
            "objective_and_audience",
            "communication_objective",
            "primary_objective",
        ),
        (
            "brief_candidate",
            "objective_and_audience",
            "communication_objective",
            "secondary_objectives",
        ),
        (
            "brief_candidate",
            "objective_and_audience",
            "communication_objective",
            "business_assumption",
        ),
        ("brief_candidate", "objective_and_audience", "audience"),
        ("brief_candidate", "objective_and_audience", "audience_context"),
        ("brief_candidate", "objective_and_audience", "audience_is_hypothesis"),
        ("brief_candidate", "message_architecture"),
        ("brief_candidate", "message_architecture", "core_message"),
        ("brief_candidate", "message_architecture", "message_hierarchy"),
        (
            "brief_candidate",
            "message_architecture",
            "message_hierarchy",
            "primary_message",
        ),
        (
            "brief_candidate",
            "message_architecture",
            "message_hierarchy",
            "secondary_benefits",
        ),
        (
            "brief_candidate",
            "message_architecture",
            "message_hierarchy",
            "supporting_proof_points",
        ),
        ("brief_candidate", "message_architecture", "benefit_hierarchy"),
        (
            "brief_candidate",
            "message_architecture",
            "benefit_hierarchy",
            "primary_benefit",
        ),
        (
            "brief_candidate",
            "message_architecture",
            "benefit_hierarchy",
            "secondary_benefits",
        ),
        (
            "brief_candidate",
            "message_architecture",
            "benefit_hierarchy",
            "supporting_features",
        ),
        ("brief_candidate", "reasons_to_believe_and_evidence"),
        ("brief_candidate", "reasons_to_believe_and_evidence", "reasons_to_believe"),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "reasons_to_believe",
            0,
            "statement",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "reasons_to_believe",
            0,
            "based_on_fact_ids",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "reasons_to_believe",
            0,
            "based_on_insight_ids",
        ),
        ("brief_candidate", "reasons_to_believe_and_evidence", "proof_points"),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "proof_point",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "fact_id",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "supporting_fragment_ids",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "source_version_id",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "approved_wording",
        ),
        ("brief_candidate", "execution_direction"),
        ("brief_candidate", "execution_direction", "objections"),
        ("brief_candidate", "execution_direction", "objection_responses"),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "objection",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "response",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "based_on_fact_ids",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "based_on_insight_ids",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "insufficient_evidence",
        ),
        ("brief_candidate", "execution_direction", "content_angles"),
        ("brief_candidate", "execution_direction", "content_angles", 0, "angle_title"),
        ("brief_candidate", "execution_direction", "content_angles", 0, "angle_type"),
        ("brief_candidate", "execution_direction", "content_angles", 0, "user_tension"),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "message_focus",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "supporting_benefits",
        ),
        ("brief_candidate", "execution_direction", "content_angles", 0, "proof_points"),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "hypothesis_status",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "requires_validation",
        ),
        ("brief_candidate", "execution_direction", "content_angles", 0, "risk_notes"),
        ("brief_candidate", "execution_direction", "tone_and_voice"),
        ("brief_candidate", "execution_direction", "tone_and_voice", "tone"),
        ("brief_candidate", "execution_direction", "tone_and_voice", "voice"),
        ("brief_candidate", "execution_direction", "tone_and_voice", "suggested_tone"),
        ("brief_candidate", "execution_direction", "call_to_action_objective"),
        ("brief_candidate", "constraints_and_honesty"),
        ("brief_candidate", "constraints_and_honesty", "mandatory_messages"),
        ("brief_candidate", "constraints_and_honesty", "prohibited_claims"),
        ("brief_candidate", "constraints_and_honesty", "accepted_hypotheses"),
        ("brief_candidate", "constraints_and_honesty", "hypotheses_to_test"),
        ("brief_candidate", "constraints_and_honesty", "evidence_limitations"),
        ("brief_candidate", "constraints_and_honesty", "risk_notes"),
        ("brief_candidate", "constraints_and_honesty", "platform_adaptation_rules"),
        ("version_and_workflow_context",),
        ("version_and_workflow_context", "approved_strategy_version_id"),
        ("version_and_workflow_context", "facts_version_id"),
        ("version_and_workflow_context", "insights_version_id"),
        ("version_and_workflow_context", "input_limitations"),
        ("version_and_workflow_context", "stage_decision"),
    ]


@pytest.mark.parametrize("kind", ["valid", "limited"])
def test_production_shaped_candidates_pass(kind: str) -> None:
    payload = _payload(kind)
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    "kind",
    ["strategy_change_required", "waiting_input", "paused", "failed"],
)
def test_non_success_decisions_preserve_context_with_null_candidate(kind: str) -> None:
    payload = _payload(kind)
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    "kind",
    ["strategy_change_required", "waiting_input", "paused", "failed"],
)
def test_non_success_decisions_can_carry_a_complete_candidate(kind: str) -> None:
    payload = _payload(kind)
    payload["brief_candidate"] = _candidate("valid")
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


def test_nullable_candidate_does_not_encode_stage_relationship() -> None:
    payload = _payload("valid")
    payload["brief_candidate"] = None
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


@pytest.mark.parametrize("value", ["not-an-object", [], 1, True])
def test_nullable_candidate_rejects_non_null_non_object_values(value: object) -> None:
    payload = _payload("valid")
    payload["brief_candidate"] = value
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


def test_schema_has_exact_root_group_and_context_order() -> None:
    schema = _schema()
    properties = cast(dict[str, object], schema["properties"])
    assert list(properties) == [
        "brief_candidate",
        "version_and_workflow_context",
    ]
    assert schema["required"] == [
        "brief_candidate",
        "version_and_workflow_context",
    ]
    candidate = cast(dict[str, object], properties["brief_candidate"])
    assert candidate["required"] == [
        "objective_and_audience",
        "message_architecture",
        "reasons_to_believe_and_evidence",
        "execution_direction",
        "constraints_and_honesty",
    ]
    context = cast(dict[str, object], properties["version_and_workflow_context"])
    assert context["required"] == [
        "approved_strategy_version_id",
        "facts_version_id",
        "insights_version_id",
        "input_limitations",
        "stage_decision",
    ]
    for mapping in (schema, candidate, context):
        assert mapping["additionalProperties"] is False


def test_every_object_has_exact_order_required_fields_and_closure() -> None:
    for path, fields in _OBJECT_FIELDS.items():
        mapping = _object_schema_at(path)
        assert list(cast(dict[str, object], mapping["properties"])) == sorted(fields)
        assert mapping["required"] == fields
        assert mapping["additionalProperties"] is False


def test_specs_are_equal_and_deeply_detached_and_preflightable() -> None:
    first = _brief.marketing_brief_candidate_output_spec()
    second = _brief.marketing_brief_candidate_output_spec()
    assert first == second and first is not second
    first_mapping = cast(dict[str, object], first.schema.to_mapping())
    second_mapping = cast(dict[str, object], second.schema.to_mapping())
    cast(dict[str, object], first_mapping["properties"])["extra"] = {}
    first_candidate = cast(
        dict[str, object],
        cast(dict[str, object], first_mapping["properties"])["brief_candidate"],
    )
    first_candidate_properties = cast(dict[str, object], first_candidate["properties"])
    cast(dict[str, object], first_candidate_properties["objective_and_audience"])[
        "nested_extra"
    ] = {}
    assert "extra" not in cast(dict[str, object], second_mapping["properties"])
    second_candidate = cast(
        dict[str, object],
        cast(dict[str, object], second_mapping["properties"])["brief_candidate"],
    )
    second_candidate_properties = cast(
        dict[str, object], second_candidate["properties"]
    )
    second_objective = cast(
        dict[str, object], second_candidate_properties["objective_and_audience"]
    )
    assert "nested_extra" not in second_objective


@pytest.mark.parametrize("path", _candidate_paths())
def test_required_paths_reject_missing(path: tuple[object, ...]) -> None:
    if path == ("brief_candidate",):
        payload = _payload("valid")
        _delete_path(payload, path)
    else:
        payload = _payload("valid")
        _delete_path(payload, path)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [path for path in _candidate_paths() if path != ("brief_candidate",)],
)
def test_nonnullable_paths_reject_null(path: tuple[object, ...]) -> None:
    payload = _payload("valid")
    _set_path(payload, path, None)
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        (
            "brief_candidate",
            "objective_and_audience",
            "communication_objective",
            "primary_objective",
        ),
        (
            "brief_candidate",
            "objective_and_audience",
            "communication_objective",
            "secondary_objectives",
            0,
        ),
        ("brief_candidate", "objective_and_audience", "audience"),
        ("brief_candidate", "objective_and_audience", "audience_context", 0),
        ("brief_candidate", "message_architecture", "core_message"),
        (
            "brief_candidate",
            "message_architecture",
            "message_hierarchy",
            "primary_message",
        ),
        (
            "brief_candidate",
            "message_architecture",
            "message_hierarchy",
            "secondary_benefits",
            0,
        ),
        (
            "brief_candidate",
            "message_architecture",
            "message_hierarchy",
            "supporting_proof_points",
            0,
        ),
        (
            "brief_candidate",
            "message_architecture",
            "benefit_hierarchy",
            "primary_benefit",
        ),
        (
            "brief_candidate",
            "message_architecture",
            "benefit_hierarchy",
            "secondary_benefits",
            0,
        ),
        (
            "brief_candidate",
            "message_architecture",
            "benefit_hierarchy",
            "supporting_features",
            0,
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "reasons_to_believe",
            0,
            "statement",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "reasons_to_believe",
            0,
            "based_on_fact_ids",
            0,
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "reasons_to_believe",
            0,
            "based_on_insight_ids",
            0,
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "proof_point",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "fact_id",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "supporting_fragment_ids",
            0,
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "source_version_id",
        ),
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "approved_wording",
        ),
        ("brief_candidate", "execution_direction", "call_to_action_objective"),
        ("brief_candidate", "execution_direction", "objections", 0),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "objection",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "response",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "based_on_fact_ids",
            0,
        ),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "based_on_insight_ids",
            0,
        ),
        ("brief_candidate", "execution_direction", "content_angles", 0, "angle_title"),
        ("brief_candidate", "execution_direction", "content_angles", 0, "angle_type"),
        ("brief_candidate", "execution_direction", "content_angles", 0, "user_tension"),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "message_focus",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "supporting_benefits",
            0,
        ),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "proof_points",
            0,
        ),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "hypothesis_status",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "risk_notes",
            0,
        ),
        ("brief_candidate", "execution_direction", "tone_and_voice", "tone"),
        ("brief_candidate", "execution_direction", "tone_and_voice", "voice"),
        ("brief_candidate", "constraints_and_honesty", "mandatory_messages", 0),
        ("brief_candidate", "constraints_and_honesty", "prohibited_claims", 0),
        ("brief_candidate", "constraints_and_honesty", "accepted_hypotheses", 0),
        ("brief_candidate", "constraints_and_honesty", "hypotheses_to_test", 0),
        ("brief_candidate", "constraints_and_honesty", "evidence_limitations", 0),
        ("brief_candidate", "constraints_and_honesty", "risk_notes", 0),
        ("brief_candidate", "constraints_and_honesty", "platform_adaptation_rules", 0),
        ("version_and_workflow_context", "approved_strategy_version_id"),
        ("version_and_workflow_context", "facts_version_id"),
        ("version_and_workflow_context", "insights_version_id"),
        ("version_and_workflow_context", "input_limitations", 0),
        ("version_and_workflow_context", "stage_decision"),
    ],
)
def test_nonblank_strings_reject_whitespace(path: tuple[object, ...]) -> None:
    payload = _payload("limited" if "evidence_limitations" in path else "valid")
    _set_path(payload, path, "   ")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    _ARRAY_PATHS,
)
def test_array_fields_reject_wrong_container_and_scalar_items(
    path: tuple[object, ...],
) -> None:
    payload = _payload("valid")
    _set_path(payload, path, "not-an-array")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )
    payload = _payload("valid")
    _set_path(payload, path, [1])
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [
        ("brief_candidate", "reasons_to_believe_and_evidence", "reasons_to_believe"),
        ("brief_candidate", "reasons_to_believe_and_evidence", "proof_points"),
        ("brief_candidate", "execution_direction", "objection_responses"),
        ("brief_candidate", "execution_direction", "content_angles"),
    ],
)
def test_object_arrays_reject_malformed_and_scalar_items(
    path: tuple[object, ...],
) -> None:
    for item in ([1], [{"unexpected": "shape"}]):
        payload = _payload("valid")
        _set_path(payload, path, item)
        with pytest.raises(ModelRuntimeError):
            parse_and_validate_structured_output(
                result=_result(payload),
                spec=_brief.marketing_brief_candidate_output_spec(),
            )


def test_supporting_fragment_ids_require_one_item() -> None:
    payload = _payload("valid")
    _set_path(
        payload,
        (
            "brief_candidate",
            "reasons_to_believe_and_evidence",
            "proof_points",
            0,
            "supporting_fragment_ids",
        ),
        [],
    )
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


def test_only_supporting_fragment_ids_has_min_items_and_other_arrays_allow_empty() -> (
    None
):
    supporting_path = (
        "brief_candidate",
        "reasons_to_believe_and_evidence",
        "proof_points",
        0,
        "supporting_fragment_ids",
    )
    for path in _ARRAY_PATHS:
        node = _schema_node_at(path)
        if path == supporting_path:
            assert node["minItems"] == 1
        else:
            assert "minItems" not in node
        payload = _payload("valid")
        _set_path(payload, path, [])
        if path == supporting_path:
            with pytest.raises(ModelRuntimeError):
                parse_and_validate_structured_output(
                    result=_result(payload),
                    spec=_brief.marketing_brief_candidate_output_spec(),
                )
        else:
            parsed = parse_and_validate_structured_output(
                result=_result(payload),
                spec=_brief.marketing_brief_candidate_output_spec(),
            )
            assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    "path",
    [
        (
            "brief_candidate",
            "objective_and_audience",
            "communication_objective",
            "business_assumption",
        ),
        ("brief_candidate", "objective_and_audience", "audience_is_hypothesis"),
        (
            "brief_candidate",
            "execution_direction",
            "objection_responses",
            0,
            "insufficient_evidence",
        ),
        (
            "brief_candidate",
            "execution_direction",
            "content_angles",
            0,
            "requires_validation",
        ),
        ("brief_candidate", "execution_direction", "tone_and_voice", "suggested_tone"),
    ],
)
def test_boolean_fields_reject_non_boolean_values(path: tuple[object, ...]) -> None:
    payload = _payload("valid")
    _set_path(payload, path, "true")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "path",
    [path for path in _OBJECT_FIELDS if path],
)
def test_nested_object_fields_reject_scalar_values(path: tuple[object, ...]) -> None:
    payload = _payload("valid")
    _set_path(payload, path, "not-an-object")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


@pytest.mark.parametrize(
    "kind", [item.value for item in _brief.MarketingBriefStageDecision]
)
def test_all_stage_decisions_are_known_and_unknown_values_reject(kind: str) -> None:
    payload = _payload("valid")
    cast(dict[str, object], payload["version_and_workflow_context"])[
        "stage_decision"
    ] = kind
    parse_and_validate_structured_output(
        result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
    )
    cast(dict[str, object], payload["version_and_workflow_context"])[
        "stage_decision"
    ] = "unknown"
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


@pytest.mark.parametrize("value", [None, 1, True, []])
def test_stage_decision_rejects_non_string_values(value: object) -> None:
    payload = _payload("valid")
    cast(dict[str, object], payload["version_and_workflow_context"])[
        "stage_decision"
    ] = value
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


def test_structural_empty_arrays_and_opaque_tokens_are_allowed() -> None:
    payload = _payload("valid")
    candidate = cast(dict[str, object], payload["brief_candidate"])
    evidence = cast(dict[str, object], candidate["reasons_to_believe_and_evidence"])
    execution = cast(dict[str, object], candidate["execution_direction"])
    evidence["reasons_to_believe"] = []
    evidence["proof_points"] = []
    execution["objections"] = []
    execution["objection_responses"] = []
    execution["content_angles"] = []
    context = cast(dict[str, object], payload["version_and_workflow_context"])
    context["approved_strategy_version_id"] = "opaque://unverified/reference"
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    "path",
    list(_OBJECT_FIELDS),
)
def test_object_layers_reject_extra_keys(path: tuple[object, ...]) -> None:
    payload = _payload("valid")
    current: Any = payload
    for key in path:
        current = current[key]
    current["extra"] = "not permitted"
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )


@pytest.mark.parametrize("group", list(_candidate("valid")))
def test_five_groups_are_atomic_when_candidate_is_not_null(group: str) -> None:
    payload = _payload("valid")
    candidate = cast(dict[str, object], payload["brief_candidate"])
    del candidate[group]
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload), spec=_brief.marketing_brief_candidate_output_spec()
        )
