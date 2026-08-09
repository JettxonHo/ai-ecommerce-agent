"""Focused unit coverage for Approved Strategy version projections."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.human_review import public
from ai_ecommerce_agent.modules.human_review.domain import contracts, snapshots
from ai_ecommerce_agent.modules.human_review.public import (
    ApprovedStrategySemanticGroup,
    ApprovedStrategySemanticGroupName,
    ApprovedStrategyVersionSnapshot,
)
from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.shared_kernel import (
    ContentOrigin,
    DomainVersionId,
    StructuredContent,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def test_approved_strategy_group_catalog_is_exact_and_alias_free() -> None:
    assert list(ApprovedStrategySemanticGroupName.__members__) == [
        "TARGET_AND_CONTEXT",
        "POSITIONING",
        "PERSUASION_STRUCTURE",
        "HYPOTHESIS_DECISIONS",
        "EVIDENCE_AND_RISKS",
        "REVIEW_AND_VERSION_METADATA",
    ]
    assert [member.value for member in ApprovedStrategySemanticGroupName] == [
        "target_and_context",
        "positioning",
        "persuasion_structure",
        "hypothesis_decisions",
        "evidence_and_risks",
        "review_and_version_metadata",
    ]


def test_approved_strategy_contracts_are_frozen_slotted_and_exactly_typed() -> None:
    expected_fields = {
        ApprovedStrategySemanticGroup: ("group", "content", "origin"),
        ApprovedStrategyVersionSnapshot: (
            "approved_strategy_version_id",
            "task_id",
            "version_number",
            "valid",
            "created_at",
            "upstream_versions",
            "semantic_groups",
            "hypotheses",
            "evidence_limitations",
            "risks",
        ),
    }
    expected_types = {
        ApprovedStrategySemanticGroup: {
            "group": ApprovedStrategySemanticGroupName,
            "content": StructuredContent,
            "origin": ContentOrigin | None,
        },
        ApprovedStrategyVersionSnapshot: {
            "approved_strategy_version_id": DomainVersionId,
            "task_id": TaskId,
            "version_number": VersionNumber,
            "valid": bool,
            "created_at": datetime,
            "upstream_versions": tuple[DomainVersionReference, ...],
            "semantic_groups": tuple[ApprovedStrategySemanticGroup, ...],
            "hypotheses": tuple[str, ...],
            "evidence_limitations": tuple[str, ...],
            "risks": tuple[str, ...],
        },
    }

    for value_type, names in expected_fields.items():
        assert is_dataclass(value_type)
        assert cast(Any, value_type).__dataclass_params__.frozen
        assert tuple(field.name for field in fields(value_type)) == names
        assert value_type.__slots__ == names
        assert get_type_hints(value_type) == expected_types[value_type]


def test_approved_strategy_snapshot_preserves_order_identity_and_projection_data() -> (
    None
):
    content = StructuredContent.from_mapping({"message": {"value": "commute"}})
    names = tuple(reversed(tuple(ApprovedStrategySemanticGroupName)))
    semantic_groups = tuple(
        ApprovedStrategySemanticGroup(
            name,
            content,
            ContentOrigin.MODEL if index % 2 == 0 else None,
        )
        for index, name in enumerate(names)
    )
    upstream_versions = (
        DomainVersionReference(DomainVersionId("positioning-1"), VersionNumber(2)),
        DomainVersionReference(DomainVersionId("facts-1"), VersionNumber(1)),
    )
    created_at = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)

    snapshot = ApprovedStrategyVersionSnapshot(
        DomainVersionId("strategy-1"),
        TaskId("task-1"),
        VersionNumber(3),
        False,
        created_at,
        upstream_versions,
        semantic_groups,
        ("commute need",),
        ("no direct customer review",),
        ("claim requires testing",),
    )

    assert snapshot.created_at is created_at
    assert snapshot.upstream_versions is upstream_versions
    assert snapshot.semantic_groups is semantic_groups
    assert snapshot.hypotheses == ("commute need",)
    assert snapshot.evidence_limitations == ("no direct customer review",)
    assert snapshot.risks == ("claim requires testing",)
    assert snapshot.valid is False
    assert tuple(group.group for group in snapshot.semantic_groups) == names
    assert all(group.content is content for group in snapshot.semantic_groups)
    assert snapshot.semantic_groups[0].origin is ContentOrigin.MODEL
    assert snapshot.semantic_groups[1].origin is None

    with pytest.raises(FrozenInstanceError):
        snapshot.valid = True  # type: ignore[misc]


@pytest.mark.parametrize("valid", [True, False])
def test_approved_strategy_snapshot_preserves_supplied_valid_projection(
    valid: bool,
) -> None:
    semantic_groups = tuple(
        ApprovedStrategySemanticGroup(name, StructuredContent.from_mapping({}))
        for name in ApprovedStrategySemanticGroupName
    )

    snapshot = ApprovedStrategyVersionSnapshot(
        DomainVersionId("strategy-1"),
        TaskId("task-1"),
        VersionNumber(1),
        valid,
        datetime(2026, 8, 9, tzinfo=UTC),
        (),
        semantic_groups,
        (),
        (),
        (),
    )

    assert snapshot.valid is valid


@pytest.mark.parametrize(
    "semantic_groups",
    [
        tuple(
            ApprovedStrategySemanticGroup(name, StructuredContent.from_mapping({}))
            for name in tuple(ApprovedStrategySemanticGroupName)[:-1]
        ),
        tuple(
            ApprovedStrategySemanticGroup(name, StructuredContent.from_mapping({}))
            for name in (
                *tuple(ApprovedStrategySemanticGroupName)[:-1],
                ApprovedStrategySemanticGroupName.TARGET_AND_CONTEXT,
            )
        ),
        (
            *tuple(
                ApprovedStrategySemanticGroup(name, StructuredContent.from_mapping({}))
                for name in tuple(ApprovedStrategySemanticGroupName)[:-1]
            ),
            ApprovedStrategySemanticGroup(
                "unknown",  # type: ignore[arg-type]
                StructuredContent.from_mapping({}),
            ),
        ),
    ],
)
def test_approved_strategy_snapshot_rejects_invalid_group_membership(
    semantic_groups: tuple[ApprovedStrategySemanticGroup, ...],
) -> None:
    with pytest.raises(ValueError):
        ApprovedStrategyVersionSnapshot(
            DomainVersionId("strategy-1"),
            TaskId("task-1"),
            VersionNumber(1),
            True,
            datetime(2026, 8, 9, tzinfo=UTC),
            (),
            semantic_groups,
            (),
            (),
            (),
        )


def test_approved_strategy_facade_reexports_private_contract_identities() -> None:
    assert (
        public.ApprovedStrategySemanticGroupName
        is contracts.ApprovedStrategySemanticGroupName
    )
    assert (
        public.ApprovedStrategySemanticGroup is snapshots.ApprovedStrategySemanticGroup
    )
    assert (
        public.ApprovedStrategyVersionSnapshot
        is snapshots.ApprovedStrategyVersionSnapshot
    )
