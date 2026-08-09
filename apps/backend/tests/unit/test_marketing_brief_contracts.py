"""Focused unit coverage for Marketing Brief version projections."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.marketing_brief.public import (
    MarketingBriefSemanticGroup,
    MarketingBriefSemanticGroupName,
    MarketingBriefVersionSnapshot,
)
from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.shared_kernel import (
    ContentOrigin,
    DomainVersionId,
    ResourceReference,
    StructuredContent,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def test_marketing_brief_group_catalog_is_exact_and_alias_free() -> None:
    assert list(MarketingBriefSemanticGroupName.__members__) == [
        "OBJECTIVE_AND_AUDIENCE",
        "MESSAGE_ARCHITECTURE",
        "REASONS_TO_BELIEVE_AND_EVIDENCE",
        "EXECUTION_DIRECTION",
        "CONSTRAINTS_AND_HONESTY",
        "VERSION_AND_WORKFLOW_CONTEXT",
    ]
    assert [member.value for member in MarketingBriefSemanticGroupName] == [
        "objective_and_audience",
        "message_architecture",
        "reasons_to_believe_and_evidence",
        "execution_direction",
        "constraints_and_honesty",
        "version_and_workflow_context",
    ]


def test_marketing_brief_contracts_are_frozen_slotted_and_exactly_typed() -> None:
    expected_fields = {
        MarketingBriefSemanticGroup: ("group", "content", "origin"),
        MarketingBriefVersionSnapshot: (
            "brief_version_id",
            "task_id",
            "version_number",
            "valid",
            "created_at",
            "upstream_versions",
            "semantic_groups",
            "hypotheses",
            "evidence_limitations",
            "risks",
            "evidence_references",
        ),
    }
    expected_types = {
        MarketingBriefSemanticGroup: {
            "group": MarketingBriefSemanticGroupName,
            "content": StructuredContent,
            "origin": ContentOrigin | None,
        },
        MarketingBriefVersionSnapshot: {
            "brief_version_id": DomainVersionId,
            "task_id": TaskId,
            "version_number": VersionNumber,
            "valid": bool,
            "created_at": datetime,
            "upstream_versions": tuple[DomainVersionReference, ...],
            "semantic_groups": tuple[MarketingBriefSemanticGroup, ...],
            "hypotheses": tuple[str, ...],
            "evidence_limitations": tuple[str, ...],
            "risks": tuple[str, ...],
            "evidence_references": tuple[ResourceReference, ...],
        },
    }

    for value_type, names in expected_fields.items():
        assert is_dataclass(value_type)
        assert cast(Any, value_type).__dataclass_params__.frozen
        assert tuple(field.name for field in fields(value_type)) == names
        assert value_type.__slots__ == names
        assert get_type_hints(value_type) == expected_types[value_type]


def test_marketing_brief_snapshot_preserves_order_identity_and_projection_data() -> (
    None
):
    content = StructuredContent.from_mapping({"message": {"value": "commute"}})
    names = tuple(reversed(tuple(MarketingBriefSemanticGroupName)))
    semantic_groups = tuple(
        MarketingBriefSemanticGroup(
            name,
            content,
            ContentOrigin.MODEL if index % 2 == 0 else None,
        )
        for index, name in enumerate(names)
    )
    upstream_versions = (
        DomainVersionReference(DomainVersionId("strategy-1"), VersionNumber(2)),
        DomainVersionReference(DomainVersionId("facts-1"), VersionNumber(1)),
    )
    evidence_references = (
        ResourceReference("source_fragment", "fragment-1"),
        ResourceReference("source_fragment", "fragment-2"),
    )
    created_at = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)

    snapshot = MarketingBriefVersionSnapshot(
        DomainVersionId("brief-1"),
        TaskId("task-1"),
        VersionNumber(3),
        False,
        created_at,
        upstream_versions,
        semantic_groups,
        ("commute need",),
        ("no direct customer review",),
        ("claim requires testing",),
        evidence_references,
    )

    assert snapshot.created_at is created_at
    assert snapshot.upstream_versions is upstream_versions
    assert snapshot.semantic_groups is semantic_groups
    assert snapshot.evidence_references is evidence_references
    assert snapshot.hypotheses == ("commute need",)
    assert snapshot.evidence_limitations == ("no direct customer review",)
    assert snapshot.risks == ("claim requires testing",)
    assert snapshot.valid is False
    assert tuple(group.group for group in snapshot.semantic_groups) == names
    assert all(group.content is content for group in snapshot.semantic_groups)
    assert snapshot.semantic_groups[0].origin is ContentOrigin.MODEL
    assert snapshot.semantic_groups[1].origin is None
    assert not hasattr(snapshot, "brief_kind")

    with pytest.raises(FrozenInstanceError):
        snapshot.valid = True  # type: ignore[misc]


@pytest.mark.parametrize("valid", [True, False])
def test_marketing_brief_snapshot_preserves_supplied_valid_projection(
    valid: bool,
) -> None:
    semantic_groups = tuple(
        MarketingBriefSemanticGroup(name, StructuredContent.from_mapping({}))
        for name in MarketingBriefSemanticGroupName
    )

    snapshot = MarketingBriefVersionSnapshot(
        DomainVersionId("brief-1"),
        TaskId("task-1"),
        VersionNumber(1),
        valid,
        datetime(2026, 8, 9, tzinfo=UTC),
        (),
        semantic_groups,
        (),
        (),
        (),
        (),
    )

    assert snapshot.valid is valid


@pytest.mark.parametrize(
    "semantic_groups",
    [
        tuple(
            MarketingBriefSemanticGroup(name, StructuredContent.from_mapping({}))
            for name in tuple(MarketingBriefSemanticGroupName)[:-1]
        ),
        tuple(
            MarketingBriefSemanticGroup(name, StructuredContent.from_mapping({}))
            for name in (
                *tuple(MarketingBriefSemanticGroupName)[:-1],
                MarketingBriefSemanticGroupName.OBJECTIVE_AND_AUDIENCE,
            )
        ),
        (
            *tuple(
                MarketingBriefSemanticGroup(name, StructuredContent.from_mapping({}))
                for name in tuple(MarketingBriefSemanticGroupName)[:-1]
            ),
            MarketingBriefSemanticGroup(
                "unknown",  # type: ignore[arg-type]
                StructuredContent.from_mapping({}),
            ),
        ),
    ],
)
def test_marketing_brief_snapshot_rejects_invalid_group_membership(
    semantic_groups: tuple[MarketingBriefSemanticGroup, ...],
) -> None:
    with pytest.raises(ValueError):
        MarketingBriefVersionSnapshot(
            DomainVersionId("brief-1"),
            TaskId("task-1"),
            VersionNumber(1),
            True,
            datetime(2026, 8, 9, tzinfo=UTC),
            (),
            semantic_groups,
            (),
            (),
            (),
            (),
        )
