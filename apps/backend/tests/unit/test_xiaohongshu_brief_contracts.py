"""Focused unit coverage for Xiaohongshu Brief version projections."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.modules.xiaohongshu_adapter.public import (
    XiaohongshuBriefSemanticGroup,
    XiaohongshuBriefSemanticGroupName,
    XiaohongshuBriefVersionSnapshot,
)
from ai_ecommerce_agent.shared_kernel import (
    ContentOrigin,
    DomainVersionId,
    ResourceReference,
    StructuredContent,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def test_xiaohongshu_brief_group_catalog_is_exact_and_alias_free() -> None:
    assert list(XiaohongshuBriefSemanticGroupName.__members__) == [
        "PLATFORM_AND_CAMPAIGN_CONTEXT",
        "NOTE_FORMAT_AND_CONTENT_MODE",
        "CREATIVE_STRUCTURE_DIRECTIONS",
        "DISCOVERY_AND_ACTION_DIRECTIONS",
        "EVIDENCE_AND_PLATFORM_CONSTRAINTS",
        "WORKFLOW_AND_VERSION_CONTEXT",
    ]
    assert [member.value for member in XiaohongshuBriefSemanticGroupName] == [
        "platform_and_campaign_context",
        "note_format_and_content_mode",
        "creative_structure_directions",
        "discovery_and_action_directions",
        "evidence_and_platform_constraints",
        "workflow_and_version_context",
    ]


def test_xiaohongshu_brief_contracts_are_frozen_slotted_and_exactly_typed() -> None:
    expected_fields = {
        XiaohongshuBriefSemanticGroup: ("group", "content", "origin"),
        XiaohongshuBriefVersionSnapshot: (
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
        XiaohongshuBriefSemanticGroup: {
            "group": XiaohongshuBriefSemanticGroupName,
            "content": StructuredContent,
            "origin": ContentOrigin | None,
        },
        XiaohongshuBriefVersionSnapshot: {
            "brief_version_id": DomainVersionId,
            "task_id": TaskId,
            "version_number": VersionNumber,
            "valid": bool,
            "created_at": datetime,
            "upstream_versions": tuple[DomainVersionReference, ...],
            "semantic_groups": tuple[XiaohongshuBriefSemanticGroup, ...],
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


def test_xiaohongshu_brief_snapshot_preserves_order_identity_and_projection_data() -> (
    None
):
    content = StructuredContent.from_mapping({"direction": {"value": "commute"}})
    names = tuple(reversed(tuple(XiaohongshuBriefSemanticGroupName)))
    semantic_groups = tuple(
        XiaohongshuBriefSemanticGroup(
            name,
            content,
            ContentOrigin.MODEL if index % 2 == 0 else None,
        )
        for index, name in enumerate(names)
    )
    upstream_versions = (
        DomainVersionReference(DomainVersionId("marketing-1"), VersionNumber(2)),
        DomainVersionReference(DomainVersionId("strategy-1"), VersionNumber(1)),
    )
    evidence_references = (
        ResourceReference("source_fragment", "fragment-1"),
        ResourceReference("source_fragment", "fragment-2"),
    )
    created_at = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)

    snapshot = XiaohongshuBriefVersionSnapshot(
        DomainVersionId("xiaohongshu-brief-1"),
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
def test_xiaohongshu_brief_snapshot_preserves_supplied_valid_projection(
    valid: bool,
) -> None:
    semantic_groups = tuple(
        XiaohongshuBriefSemanticGroup(name, StructuredContent.from_mapping({}))
        for name in XiaohongshuBriefSemanticGroupName
    )

    snapshot = XiaohongshuBriefVersionSnapshot(
        DomainVersionId("xiaohongshu-brief-1"),
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
            XiaohongshuBriefSemanticGroup(name, StructuredContent.from_mapping({}))
            for name in tuple(XiaohongshuBriefSemanticGroupName)[:-1]
        ),
        tuple(
            XiaohongshuBriefSemanticGroup(name, StructuredContent.from_mapping({}))
            for name in (
                *tuple(XiaohongshuBriefSemanticGroupName)[:-1],
                XiaohongshuBriefSemanticGroupName.PLATFORM_AND_CAMPAIGN_CONTEXT,
            )
        ),
        (
            *tuple(
                XiaohongshuBriefSemanticGroup(name, StructuredContent.from_mapping({}))
                for name in tuple(XiaohongshuBriefSemanticGroupName)[:-1]
            ),
            XiaohongshuBriefSemanticGroup(
                "unknown",  # type: ignore[arg-type]
                StructuredContent.from_mapping({}),
            ),
        ),
    ],
)
def test_xiaohongshu_brief_snapshot_rejects_invalid_group_membership(
    semantic_groups: tuple[XiaohongshuBriefSemanticGroup, ...],
) -> None:
    with pytest.raises(ValueError):
        XiaohongshuBriefVersionSnapshot(
            DomainVersionId("xiaohongshu-brief-1"),
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
