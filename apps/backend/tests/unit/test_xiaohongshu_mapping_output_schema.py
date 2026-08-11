"""Behavior tests for the Xiaohongshu mapping candidate-output schema."""

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
from ai_ecommerce_agent.modules.xiaohongshu_adapter.application.skills import (
    xiaohongshu_brief_mapping as _mapping,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _schema_compatibility,
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
        "xiaohongshu_brief_candidate",
        "v1",
        "adapter",
        "domain",
        "profile",
        "v1",
        "context",
    )
    metadata = ProviderCallMetadata(
        ModelCallId("call-xiaohongshu-mapping"),
        (ProviderAttemptId("attempt-xiaohongshu-mapping"),),
        versions,
        "response-xiaohongshu-mapping",
        None,
        ModelTokenUsage(1, 2, 3),
        1,
    )
    return ModelCallResult(
        ModelOutputEnvelope(json.dumps(payload, separators=(",", ":"))), metadata
    )


def _candidate(kind: str = "valid") -> dict[str, object]:
    limited = kind == "limited"
    competitor = kind == "competitor_only"
    return {
        "platform_and_campaign_context": {
            "platform": "xiaohongshu",
            "account_type": None if limited else "brand_account",
            "content_relationship": None if limited else "creator_collaboration",
            "commercial_context": None if limited else "paid_campaign",
            "campaign_objective": "awareness",
            "available_asset_types": ["product_photo"],
        },
        "note_format_and_content_mode": {
            "recommended_note_format": (
                "video_note_brief" if limited else "image_text_note_brief"
            ),
            "primary_content_mode": "problem_solution",
            "secondary_content_mode": None if limited else "usage_scenario",
            "platform_objective": "education",
            "source_content_angle_ids": ["angle-1"],
        },
        "creative_structure_directions": {
            "title_directions": [
                {
                    "title_direction": "a calmer commute starts with one small choice",
                    "user_question_or_tension": "how can carrying feel less awkward",
                    "primary_keyword": "commute organization",
                    "message_focus": "show the carrying moment",
                    "proof_required": True,
                    "risk_notes": ["avoid universal claims"],
                }
            ],
            "cover_direction": {
                "cover_message_direction": "show the daily carrying problem",
                "cover_visual_focus": "bottle sleeve in a work bag",
                "cover_information_priority": "problem before product detail",
                "cover_risk_notes": ["direction only, not final copy"],
            },
            "narrative_structure": [
                {
                    "module_name": "opening tension",
                    "content_direction": "name the fumbling moment",
                    "proof_points": ["fact-1"],
                    "limitations": ["single source"],
                    "risk_notes": ["do not imply personal experience"],
                }
            ],
            "content_angle_mappings": [
                {
                    "source_content_angle_id": "angle-1",
                    "xiaohongshu_angle": "commute friction to simple routine",
                    "note_format": (
                        "video_note_brief" if limited else "image_text_note_brief"
                    ),
                    "content_mode": "problem_solution",
                    "narrative_structure": ["opening tension"],
                    "proof_points": ["fact-1"],
                    "customer_language": (
                        [] if limited else ["documented customer phrasing"]
                    ),
                    "hypotheses": ["access matters"],
                    "limitations": ["not a usage review"],
                    "risk_notes": ["keep comparison contextual"],
                }
            ],
            "message_priority": ["simple carrying", "easy access"],
            "proof_placement": [
                {
                    "proof_point": "fact-1",
                    "narrative_module": "opening tension",
                    "placement_direction": "after the problem setup",
                }
            ],
            "fit_boundary": "direction supports planning, not publication",
        },
        "discovery_and_action_directions": {
            "search_intent": "find a practical commute carrying idea",
            "keyword_directions": ["commute organization"],
            "topic_directions": ["daily routine"],
            "hashtag_directions": ["commute routine", "bag organization"],
            "cta_mapping": {
                "source_cta_objective": "invite consideration",
                "cta_direction": "prompt reflection on the carrying moment",
                "risk_notes": ["do not promise conversion"],
            },
            "interaction_prompt_direction": "ask what part of carrying feels hardest",
        },
        "evidence_and_platform_constraints": {
            "proof_points": ["fact-1"],
            "customer_language": []
            if limited
            else [
                {
                    "fragment_id": "competitor-fragment-1"
                    if competitor
                    else "fragment-1",
                    "source_scope": "competitor" if competitor else "current_product",
                    "quote_type": "documented_observation",
                    "locator": "source-1:paragraph-2",
                    "usage_direction": (
                        "category context only"
                        if competitor
                        else "illustrate the carrying tension"
                    ),
                }
            ],
            "mandatory_messages": ["keep the direction evidence-bound"],
            "prohibited_claims": (
                ["avoid unsupported comparisons"]
                if competitor
                else ["never claim universal superiority"]
            ),
            "hypotheses": ["the audience values easy access"],
            "evidence_limitations": (
                ["no direct experience material"]
                if limited
                else ["one documented source"]
            ),
            "platform_risk_notes": ["policy snapshot controls later review"],
            "review_route_notes": ["route uncertain claims to review"],
            "required_qualification_notes": ["qualify unsupported claims"],
            "commercial_disclosure_notes": ["disclose paid context when applicable"],
        },
    }


def _payload(kind: str = "valid") -> dict[str, object]:
    decision = {
        "valid": "valid",
        "competitor_only": "valid",
        "limited": "valid_with_limitations",
        "brief_change_required": "brief_change_required",
        "platform_policy_update_required": "platform_policy_update_required",
        "waiting_input": "waiting_input",
        "paused": "paused",
        "failed": "failed",
    }[kind]
    candidate = None
    if kind in {"valid", "limited", "competitor_only"}:
        candidate = _candidate(kind)
    return {
        "xiaohongshu_brief_candidate": candidate,
        "workflow_and_version_context": {
            "marketing_brief_version_id": "brief-v1",
            "approved_strategy_version_id": "strategy-v1",
            "facts_version_id": "facts-v1",
            "platform_policy_snapshot_id": None
            if kind == "platform_policy_update_required"
            else "policy-snapshot-v1",
            "platform_policy_version": None
            if kind == "platform_policy_update_required"
            else "policy-v1",
            "input_limitations": ["mapping remains directional"],
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
        _mapping.xiaohongshu_brief_candidate_output_spec().schema.to_mapping(),
    )


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


def _walk_schema(
    node: dict[str, object], path: tuple[object, ...] = ()
) -> list[tuple[tuple[object, ...], dict[str, object]]]:
    found: list[tuple[tuple[object, ...], dict[str, object]]] = [(path, node)]
    node_type = node.get("type")
    if node_type == "object" or node_type == ["object", "null"]:
        properties = cast(dict[str, object], node["properties"])
        for key, child in properties.items():
            found.extend(_walk_schema(cast(dict[str, object], child), path + (key,)))
    elif node_type == "array":
        item = cast(dict[str, object], node["items"])
        found.extend(_walk_schema(item, path + (0,)))
    return found


_EXPECTED_OBJECT_FIELDS: dict[tuple[object, ...], tuple[str, ...]] = {
    (): ("xiaohongshu_brief_candidate", "workflow_and_version_context"),
    ("xiaohongshu_brief_candidate",): (
        "platform_and_campaign_context",
        "note_format_and_content_mode",
        "creative_structure_directions",
        "discovery_and_action_directions",
        "evidence_and_platform_constraints",
    ),
    ("workflow_and_version_context",): (
        "marketing_brief_version_id",
        "approved_strategy_version_id",
        "facts_version_id",
        "platform_policy_snapshot_id",
        "platform_policy_version",
        "input_limitations",
        "stage_decision",
    ),
    ("xiaohongshu_brief_candidate", "platform_and_campaign_context"): (
        "platform",
        "account_type",
        "content_relationship",
        "commercial_context",
        "campaign_objective",
        "available_asset_types",
    ),
    ("xiaohongshu_brief_candidate", "note_format_and_content_mode"): (
        "recommended_note_format",
        "primary_content_mode",
        "secondary_content_mode",
        "platform_objective",
        "source_content_angle_ids",
    ),
    ("xiaohongshu_brief_candidate", "creative_structure_directions"): (
        "title_directions",
        "cover_direction",
        "narrative_structure",
        "content_angle_mappings",
        "message_priority",
        "proof_placement",
        "fit_boundary",
    ),
    (
        "xiaohongshu_brief_candidate",
        "creative_structure_directions",
        "title_directions",
        0,
    ): (
        "title_direction",
        "user_question_or_tension",
        "primary_keyword",
        "message_focus",
        "proof_required",
        "risk_notes",
    ),
    (
        "xiaohongshu_brief_candidate",
        "creative_structure_directions",
        "cover_direction",
    ): (
        "cover_message_direction",
        "cover_visual_focus",
        "cover_information_priority",
        "cover_risk_notes",
    ),
    (
        "xiaohongshu_brief_candidate",
        "creative_structure_directions",
        "narrative_structure",
        0,
    ): (
        "module_name",
        "content_direction",
        "proof_points",
        "limitations",
        "risk_notes",
    ),
    (
        "xiaohongshu_brief_candidate",
        "creative_structure_directions",
        "content_angle_mappings",
        0,
    ): (
        "source_content_angle_id",
        "xiaohongshu_angle",
        "note_format",
        "content_mode",
        "narrative_structure",
        "proof_points",
        "customer_language",
        "hypotheses",
        "limitations",
        "risk_notes",
    ),
    (
        "xiaohongshu_brief_candidate",
        "creative_structure_directions",
        "proof_placement",
        0,
    ): ("proof_point", "narrative_module", "placement_direction"),
    ("xiaohongshu_brief_candidate", "discovery_and_action_directions"): (
        "search_intent",
        "keyword_directions",
        "topic_directions",
        "hashtag_directions",
        "cta_mapping",
        "interaction_prompt_direction",
    ),
    (
        "xiaohongshu_brief_candidate",
        "discovery_and_action_directions",
        "cta_mapping",
    ): ("source_cta_objective", "cta_direction", "risk_notes"),
    (
        "xiaohongshu_brief_candidate",
        "evidence_and_platform_constraints",
    ): (
        "proof_points",
        "customer_language",
        "mandatory_messages",
        "prohibited_claims",
        "hypotheses",
        "evidence_limitations",
        "platform_risk_notes",
        "review_route_notes",
        "required_qualification_notes",
        "commercial_disclosure_notes",
    ),
    (
        "xiaohongshu_brief_candidate",
        "evidence_and_platform_constraints",
        "customer_language",
        0,
    ): ("fragment_id", "source_scope", "quote_type", "locator", "usage_direction"),
}


def test_object_field_inventory_and_semantic_required_order_are_independent() -> None:
    schema = _schema()
    for path, expected_fields in _EXPECTED_OBJECT_FIELDS.items():
        node = schema if not path else _schema_node_at(path)
        properties = cast(dict[str, object], node["properties"])
        assert list(properties) == sorted(expected_fields)
        assert tuple(cast(list[str], node["required"])) == expected_fields
        assert node["additionalProperties"] is False
    actual_paths = {
        path
        for path, node in _walk_schema(schema)
        if node.get("type") in ("object", ["object", "null"])
    }
    assert actual_paths == set(_EXPECTED_OBJECT_FIELDS)


def _required_paths() -> list[tuple[object, ...]]:
    paths: list[tuple[object, ...]] = []
    for path, node in _walk_schema(_schema()):
        if node.get("type") not in ("object", ["object", "null"]):
            continue
        properties = cast(dict[str, object], node["properties"])
        for name in cast(list[str], node["required"]):
            child = cast(dict[str, object], properties[name])
            child_path = path + (name,)
            paths.append(child_path)
            if child.get("type") == "object" or child.get("type") == [
                "object",
                "null",
            ]:
                paths.extend(
                    child_path + nested for nested in _required_paths_from(child)
                )
            elif child.get("type") == "array":
                item = cast(dict[str, object], child["items"])
                if item.get("type") == "object":
                    paths.extend(
                        child_path + (0,) + nested
                        for nested in _required_paths_from(item)
                    )
    return paths


def _required_paths_from(node: dict[str, object]) -> list[tuple[object, ...]]:
    paths: list[tuple[object, ...]] = []
    properties = cast(dict[str, object], node["properties"])
    for name in cast(list[str], node["required"]):
        child = cast(dict[str, object], properties[name])
        paths.append((name,))
        if child.get("type") == "object":
            paths.extend((name,) + nested for nested in _required_paths_from(child))
        elif child.get("type") == "array":
            item = cast(dict[str, object], child["items"])
            if item.get("type") == "object":
                paths.extend(
                    (name, 0) + nested for nested in _required_paths_from(item)
                )
    return paths


@pytest.mark.parametrize("kind", ["valid", "limited", "competitor_only"])
def test_representative_production_shaped_candidates_pass(kind: str) -> None:
    payload = _payload(kind)
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_mapping.xiaohongshu_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    "kind",
    [
        "brief_change_required",
        "platform_policy_update_required",
        "waiting_input",
        "paused",
        "failed",
    ],
)
def test_non_success_decisions_preserve_context_with_null_candidate(kind: str) -> None:
    payload = _payload(kind)
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_mapping.xiaohongshu_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


@pytest.mark.parametrize(
    "kind",
    [
        "brief_change_required",
        "platform_policy_update_required",
        "waiting_input",
        "paused",
        "failed",
    ],
)
def test_stage_and_candidate_are_structurally_independent(kind: str) -> None:
    payload = _payload(kind)
    payload["xiaohongshu_brief_candidate"] = _candidate("valid")
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_mapping.xiaohongshu_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


def test_valid_stage_can_have_a_null_candidate() -> None:
    payload = _payload("valid")
    payload["xiaohongshu_brief_candidate"] = None
    parsed = parse_and_validate_structured_output(
        result=_result(payload), spec=_mapping.xiaohongshu_brief_candidate_output_spec()
    )
    assert parsed.to_mapping() == payload


def test_competitor_language_is_scoped_without_current_product_attribution() -> None:
    candidate = _candidate("competitor_only")
    evidence = cast(dict[str, object], candidate["evidence_and_platform_constraints"])
    language = cast(list[object], evidence["customer_language"])
    item = cast(dict[str, object], language[0])
    assert item["source_scope"] == "competitor"
    assert item["usage_direction"] == "category context only"
    assert "current_product" not in repr(candidate)
    assert "superiority" not in repr(candidate)


def test_limited_video_mapping_has_honest_empty_experience_material() -> None:
    candidate = _candidate("limited")
    note = cast(dict[str, object], candidate["note_format_and_content_mode"])
    evidence = cast(dict[str, object], candidate["evidence_and_platform_constraints"])
    assert note["recommended_note_format"] == "video_note_brief"
    assert evidence["customer_language"] == []
    assert "experience_sharing" not in repr(candidate)
    assert "review guarantee" not in repr(candidate)


def test_every_required_path_rejects_missing() -> None:
    for path in _required_paths():
        payload = _payload("valid")
        _delete_path(payload, path)
        with pytest.raises(ModelRuntimeError):
            parse_and_validate_structured_output(
                result=_result(payload),
                spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
            )


def test_every_object_is_closed_and_every_array_allows_empty() -> None:
    for path, node in _walk_schema(_schema()):
        if node.get("type") in ("object", ["object", "null"]):
            assert node["additionalProperties"] is False
            if path:
                mutated = _payload("valid")
                current: Any = mutated
                for key in path:
                    current = current[key]
                current["extra"] = "not allowed"
                with pytest.raises(ModelRuntimeError):
                    parse_and_validate_structured_output(
                        result=_result(mutated),
                        spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
                    )
        elif node.get("type") == "array":
            assert "minItems" not in node and "maxItems" not in node
            mutated = _payload("valid")
            _set_path(mutated, path, [])
            parsed = parse_and_validate_structured_output(
                result=_result(mutated),
                spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
            )
            assert parsed.to_mapping() == mutated


def test_every_array_path_rejects_wrong_container_and_item_types() -> None:
    for path, node in _walk_schema(_schema()):
        if node.get("type") != "array":
            continue
        for value in ("not-an-array", [1]):
            payload = _payload("valid")
            _set_path(payload, path, value)
            with pytest.raises(ModelRuntimeError):
                parse_and_validate_structured_output(
                    result=_result(payload),
                    spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
                )


def test_nullable_fields_accept_only_null_or_nonblank_string() -> None:
    nullable_paths = [
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "account_type",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "content_relationship",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "commercial_context",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "campaign_objective",
        ),
        (
            "xiaohongshu_brief_candidate",
            "note_format_and_content_mode",
            "secondary_content_mode",
        ),
        ("workflow_and_version_context", "platform_policy_snapshot_id"),
        ("workflow_and_version_context", "platform_policy_version"),
    ]
    for path in nullable_paths:
        payload = _payload("valid")
        _set_path(payload, path, None)
        parse_and_validate_structured_output(
            result=_result(payload),
            spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
        )
        payload = _payload("valid")
        _set_path(payload, path, "   ")
        with pytest.raises(ModelRuntimeError):
            parse_and_validate_structured_output(
                result=_result(payload),
                spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
            )


def test_nonnullable_required_paths_reject_null() -> None:
    nullable = {
        ("xiaohongshu_brief_candidate",),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "account_type",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "content_relationship",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "commercial_context",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "campaign_objective",
        ),
        (
            "xiaohongshu_brief_candidate",
            "note_format_and_content_mode",
            "secondary_content_mode",
        ),
        ("workflow_and_version_context", "platform_policy_snapshot_id"),
        ("workflow_and_version_context", "platform_policy_version"),
    }
    for path in _required_paths():
        if path in nullable:
            continue
        payload = _payload("valid")
        _set_path(payload, path, None)
        with pytest.raises(ModelRuntimeError):
            parse_and_validate_structured_output(
                result=_result(payload),
                spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
            )


def test_all_nonblank_string_paths_reject_whitespace() -> None:
    string_paths = {
        path
        for path, node in _walk_schema(_schema())
        if node.get("type") in ("string", ["string", "null"])
    }
    assert len(string_paths) == 69
    assert (
        "xiaohongshu_brief_candidate",
        "creative_structure_directions",
        "title_directions",
        0,
        "risk_notes",
        0,
    ) in string_paths
    for path in string_paths:
        payload = _payload("valid")
        _set_path(payload, path, "   ")
        with pytest.raises(ModelRuntimeError):
            parse_and_validate_structured_output(
                result=_result(payload),
                spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
            )


def test_boolean_paths_are_exact_booleans() -> None:
    boolean_paths = {
        path for path, node in _walk_schema(_schema()) if node.get("type") == "boolean"
    }
    assert boolean_paths == {
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "title_directions",
            0,
            "proof_required",
        )
    }
    for path in boolean_paths:
        for value in (1, "true", None):
            payload = _payload("valid")
            _set_path(payload, path, value)
            with pytest.raises(ModelRuntimeError):
                parse_and_validate_structured_output(
                    result=_result(payload),
                    spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
                )


def test_both_note_formats_and_all_stage_decisions_are_known() -> None:
    for note_format in _mapping.XiaohongshuNoteFormat:
        payload = _payload("valid")
        candidate = cast(dict[str, object], payload["xiaohongshu_brief_candidate"])
        note = cast(dict[str, object], candidate["note_format_and_content_mode"])
        note["recommended_note_format"] = note_format.value
        angle = cast(
            dict[str, object],
            cast(
                list[object],
                cast(dict[str, object], candidate["creative_structure_directions"])[
                    "content_angle_mappings"
                ],
            )[0],
        )
        angle["note_format"] = note_format.value
        parse_and_validate_structured_output(
            result=_result(payload),
            spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
        )
    for decision in _mapping.XiaohongshuBriefStageDecision:
        payload = _payload("valid")
        cast(dict[str, object], payload["workflow_and_version_context"])[
            "stage_decision"
        ] = decision.value
        parse_and_validate_structured_output(
            result=_result(payload),
            spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
        )


def test_unknown_stage_value_rejects_on_fresh_valid_payload() -> None:
    stage_payload = _payload("valid")
    context = cast(dict[str, object], stage_payload["workflow_and_version_context"])
    context["stage_decision"] = "unknown"
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(stage_payload),
            spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
        )


@pytest.mark.parametrize(
    "path",
    [
        (
            "xiaohongshu_brief_candidate",
            "note_format_and_content_mode",
            "recommended_note_format",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "note_format",
        ),
    ],
)
def test_each_note_format_path_rejects_unknown(path: tuple[object, ...]) -> None:
    payload = _payload("valid")
    _set_path(payload, path, "unknown-note-format")
    with pytest.raises(ModelRuntimeError):
        parse_and_validate_structured_output(
            result=_result(payload),
            spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
        )


def test_open_taxonomies_accept_distinct_nonblank_strings() -> None:
    paths = [
        ("xiaohongshu_brief_candidate", "platform_and_campaign_context", "platform"),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "account_type",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "content_relationship",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "commercial_context",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "campaign_objective",
        ),
        (
            "xiaohongshu_brief_candidate",
            "platform_and_campaign_context",
            "available_asset_types",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "note_format_and_content_mode",
            "primary_content_mode",
        ),
        (
            "xiaohongshu_brief_candidate",
            "note_format_and_content_mode",
            "secondary_content_mode",
        ),
        (
            "xiaohongshu_brief_candidate",
            "note_format_and_content_mode",
            "platform_objective",
        ),
        (
            "xiaohongshu_brief_candidate",
            "note_format_and_content_mode",
            "source_content_angle_ids",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "title_directions",
            0,
            "title_direction",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "title_directions",
            0,
            "user_question_or_tension",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "title_directions",
            0,
            "primary_keyword",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "title_directions",
            0,
            "message_focus",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "title_directions",
            0,
            "risk_notes",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "cover_direction",
            "cover_message_direction",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "cover_direction",
            "cover_visual_focus",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "cover_direction",
            "cover_information_priority",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "cover_direction",
            "cover_risk_notes",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "narrative_structure",
            0,
            "module_name",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "narrative_structure",
            0,
            "content_direction",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "narrative_structure",
            0,
            "proof_points",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "narrative_structure",
            0,
            "limitations",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "narrative_structure",
            0,
            "risk_notes",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "source_content_angle_id",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "xiaohongshu_angle",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "content_mode",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "narrative_structure",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "proof_points",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "customer_language",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "hypotheses",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "limitations",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "content_angle_mappings",
            0,
            "risk_notes",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "message_priority",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "proof_placement",
            0,
            "proof_point",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "proof_placement",
            0,
            "narrative_module",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "proof_placement",
            0,
            "placement_direction",
        ),
        (
            "xiaohongshu_brief_candidate",
            "creative_structure_directions",
            "fit_boundary",
        ),
        (
            "xiaohongshu_brief_candidate",
            "discovery_and_action_directions",
            "search_intent",
        ),
        (
            "xiaohongshu_brief_candidate",
            "discovery_and_action_directions",
            "keyword_directions",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "discovery_and_action_directions",
            "topic_directions",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "discovery_and_action_directions",
            "hashtag_directions",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "discovery_and_action_directions",
            "cta_mapping",
            "source_cta_objective",
        ),
        (
            "xiaohongshu_brief_candidate",
            "discovery_and_action_directions",
            "cta_mapping",
            "cta_direction",
        ),
        (
            "xiaohongshu_brief_candidate",
            "discovery_and_action_directions",
            "cta_mapping",
            "risk_notes",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "discovery_and_action_directions",
            "interaction_prompt_direction",
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "proof_points",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "customer_language",
            0,
            "fragment_id",
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "customer_language",
            0,
            "source_scope",
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "customer_language",
            0,
            "quote_type",
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "customer_language",
            0,
            "locator",
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "customer_language",
            0,
            "usage_direction",
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "mandatory_messages",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "prohibited_claims",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "hypotheses",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "evidence_limitations",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "platform_risk_notes",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "review_route_notes",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "required_qualification_notes",
            0,
        ),
        (
            "xiaohongshu_brief_candidate",
            "evidence_and_platform_constraints",
            "commercial_disclosure_notes",
            0,
        ),
    ]
    values = [f"open-taxonomy-{index}" for index in range(len(paths))]
    assert len(set(values)) == len(paths)
    for path, value in zip(paths, values, strict=True):
        payload = _payload("valid")
        _set_path(payload, path, value)
        parse_and_validate_structured_output(
            result=_result(payload),
            spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
        )
    keyword_path = (
        "xiaohongshu_brief_candidate",
        "discovery_and_action_directions",
        "keyword_directions",
        0,
    )
    keyword_payload = _payload("valid")
    _set_path(keyword_payload, keyword_path, "keyword-not-in-a-frozen-enum")
    assert (
        parse_and_validate_structured_output(
            result=_result(keyword_payload),
            spec=_mapping.xiaohongshu_brief_candidate_output_spec(),
        ).to_mapping()
        == keyword_payload
    )


def test_specs_are_equal_detached_and_preflightable() -> None:
    first = _mapping.xiaohongshu_brief_candidate_output_spec()
    second = _mapping.xiaohongshu_brief_candidate_output_spec()
    assert first == second and first is not second
    _schema_compatibility.ensure_openai_responses_schema_compatible(
        structured_output=first, model_call_id=ModelCallId("xiaohongshu-schema")
    )
    first_mapping = cast(dict[str, object], first.schema.to_mapping())
    second_mapping = cast(dict[str, object], second.schema.to_mapping())
    first_props = cast(dict[str, object], first_mapping["properties"])
    first_context = cast(dict[str, object], first_props["workflow_and_version_context"])
    cast(dict[str, object], first_context["properties"])["nested_extra"] = {}
    first_candidate = cast(
        dict[str, object], first_props["xiaohongshu_brief_candidate"]
    )
    first_candidate_properties = cast(dict[str, object], first_candidate["properties"])
    first_note = cast(
        dict[str, object], first_candidate_properties["note_format_and_content_mode"]
    )
    first_note_properties = cast(dict[str, object], first_note["properties"])
    cast(
        list[object],
        cast(dict[str, object], first_note_properties["recommended_note_format"])[
            "enum"
        ],
    ).append("unexpected")
    first_platform = cast(
        dict[str, object], first_candidate_properties["platform_and_campaign_context"]
    )
    cast(list[object], first_platform["required"]).append("unexpected")
    first_creative = cast(
        dict[str, object], first_candidate_properties["creative_structure_directions"]
    )
    first_title_array = cast(
        dict[str, object],
        cast(dict[str, object], first_creative["properties"])["title_directions"],
    )
    cast(
        list[object], cast(dict[str, object], first_title_array["items"])["required"]
    ).append("unexpected")
    second_props = cast(dict[str, object], second_mapping["properties"])
    second_context = cast(
        dict[str, object], second_props["workflow_and_version_context"]
    )
    assert "nested_extra" not in cast(dict[str, object], second_context["properties"])
    second_candidate = cast(
        dict[str, object], second_props["xiaohongshu_brief_candidate"]
    )
    second_candidate_properties = cast(
        dict[str, object], second_candidate["properties"]
    )
    second_note = cast(
        dict[str, object], second_candidate_properties["note_format_and_content_mode"]
    )
    second_note_properties = cast(dict[str, object], second_note["properties"])
    assert cast(
        list[object],
        cast(dict[str, object], second_note_properties["recommended_note_format"])[
            "enum"
        ],
    ) == ["image_text_note_brief", "video_note_brief"]
    second_platform = cast(
        dict[str, object], second_candidate_properties["platform_and_campaign_context"]
    )
    assert cast(list[object], second_platform["required"]) == [
        "platform",
        "account_type",
        "content_relationship",
        "commercial_context",
        "campaign_objective",
        "available_asset_types",
    ]
    second_creative = cast(
        dict[str, object], second_candidate_properties["creative_structure_directions"]
    )
    second_title_array = cast(
        dict[str, object],
        cast(dict[str, object], second_creative["properties"])["title_directions"],
    )
    assert "unexpected" not in cast(
        list[object], cast(dict[str, object], second_title_array["items"])["required"]
    )


def test_no_final_content_inventory() -> None:
    serialized = repr(_schema())
    for forbidden in (
        "final_title",
        "final_body",
        "final_hashtags",
        "cover_copy",
        "experience_sharing",
        "review_guarantee",
    ):
        assert forbidden not in serialized
