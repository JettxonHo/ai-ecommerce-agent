"""Focused unit coverage for Human Review semantic-group contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.human_review.public import (
    ReviewSemanticGroup,
    ReviewSemanticGroupName,
)
from ai_ecommerce_agent.shared_kernel import ContentOrigin, StructuredContent

pytestmark = pytest.mark.unit


def test_review_semantic_group_catalog_is_exact_and_alias_free() -> None:
    assert list(ReviewSemanticGroupName.__members__) == [
        "VERSION_CONTEXT",
        "POSITIONING_CANDIDATES",
        "KEY_FACTS_AND_INSIGHTS",
        "HYPOTHESES",
        "EVIDENCE_LIMITATIONS",
        "CONFLICTS_AND_STRATEGIC_RISKS",
        "MODEL_RECOMMENDATION",
    ]
    assert [member.value for member in ReviewSemanticGroupName] == [
        "version_context",
        "positioning_candidates",
        "key_facts_and_insights",
        "hypotheses",
        "evidence_limitations",
        "conflicts_and_strategic_risks",
        "model_recommendation",
    ]


def test_review_semantic_group_is_frozen_slotted_and_exactly_typed() -> None:
    assert is_dataclass(ReviewSemanticGroup)
    assert cast(Any, ReviewSemanticGroup).__dataclass_params__.frozen
    assert tuple(field.name for field in fields(ReviewSemanticGroup)) == (
        "group",
        "content",
        "origin",
    )
    assert ReviewSemanticGroup.__slots__ == ("group", "content", "origin")
    assert get_type_hints(ReviewSemanticGroup) == {
        "group": ReviewSemanticGroupName,
        "content": StructuredContent,
        "origin": ContentOrigin | None,
    }

    content = StructuredContent.from_mapping({"recommendation": {"score": 1}})
    group = ReviewSemanticGroup(
        ReviewSemanticGroupName.MODEL_RECOMMENDATION,
        content,
        ContentOrigin.MODEL,
    )
    assert group.group is ReviewSemanticGroupName.MODEL_RECOMMENDATION
    assert group.content is content
    assert group.origin is ContentOrigin.MODEL

    without_origin = ReviewSemanticGroup(
        ReviewSemanticGroupName.VERSION_CONTEXT,
        content,
    )
    assert without_origin.origin is None
    with pytest.raises(FrozenInstanceError):
        group.origin = ContentOrigin.USER  # type: ignore[misc]
