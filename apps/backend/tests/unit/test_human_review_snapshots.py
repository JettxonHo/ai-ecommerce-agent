"""Focused unit coverage for Human Review metadata snapshots."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.human_review.public import (
    ReviewDecisionBasis,
    ReviewDecisionOutcome,
    ReviewDecisionSnapshot,
    ReviewDraftMetadata,
    ReviewDraftReference,
    ReviewPackageHeader,
    ReviewPackageIdentity,
    ReviewPackageReference,
    ReviewPackageSnapshot,
    ReviewPackageStatus,
    ReviewSemanticGroup,
    ReviewSemanticGroupName,
)
from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.shared_kernel import (
    ContentOrigin,
    DomainVersionId,
    ReviewDecisionId,
    ReviewDraftId,
    ReviewId,
    ReviewPackageId,
    Revision,
    StructuredContent,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def test_review_snapshot_dtos_are_frozen_slotted_and_exactly_typed() -> None:
    expected_fields = {
        ReviewPackageHeader: (
            "identity",
            "status",
            "upstream_versions",
            "required_decisions",
            "limitations",
        ),
        ReviewDraftMetadata: ("reference", "saved_at", "superseded_by"),
        ReviewDecisionSnapshot: (
            "review_decision_id",
            "basis",
            "outcome",
            "decided_at",
        ),
        ReviewPackageSnapshot: ("header", "semantic_groups"),
        ReviewSemanticGroup: ("group", "content", "origin"),
    }
    expected_types = {
        ReviewPackageHeader: {
            "identity": ReviewPackageIdentity,
            "status": ReviewPackageStatus,
            "upstream_versions": tuple[DomainVersionReference, ...],
            "required_decisions": tuple[str, ...],
            "limitations": tuple[str, ...],
        },
        ReviewDraftMetadata: {
            "reference": ReviewDraftReference,
            "saved_at": datetime,
            "superseded_by": ReviewDraftId | None,
        },
        ReviewDecisionSnapshot: {
            "review_decision_id": ReviewDecisionId,
            "basis": ReviewDecisionBasis,
            "outcome": ReviewDecisionOutcome,
            "decided_at": datetime,
        },
        ReviewPackageSnapshot: {
            "header": ReviewPackageHeader,
            "semantic_groups": tuple[ReviewSemanticGroup, ...],
        },
        ReviewSemanticGroup: {
            "group": ReviewSemanticGroupName,
            "content": StructuredContent,
            "origin": ContentOrigin | None,
        },
    }

    for value_type, names in expected_fields.items():
        assert is_dataclass(value_type)
        assert cast(Any, value_type).__dataclass_params__.frozen
        assert tuple(field.name for field in fields(value_type)) == names
        assert value_type.__slots__ == names
        assert get_type_hints(value_type) == expected_types[value_type]


def test_review_snapshot_dtos_preserve_supplied_metadata_and_exact_basis() -> None:
    identity = ReviewPackageIdentity(
        ReviewPackageId("package-1"),
        ReviewId("review-1"),
        TaskId("task-1"),
        VersionNumber(1),
    )
    upstream_versions = (
        DomainVersionReference(DomainVersionId("positioning-1"), VersionNumber(2)),
        DomainVersionReference(DomainVersionId("facts-1"), VersionNumber(1)),
    )
    header = ReviewPackageHeader(
        identity,
        ReviewPackageStatus.ACTIVE,
        upstream_versions,
        ("choose a target segment", "review the evidence"),
        ("limited customer feedback",),
    )
    assert header.identity is identity
    assert header.upstream_versions is upstream_versions
    assert header.required_decisions == (
        "choose a target segment",
        "review the evidence",
    )
    assert header.limitations == ("limited customer feedback",)

    reference = ReviewDraftReference(
        ReviewDraftId("draft-1"),
        ReviewPackageId("package-1"),
        Revision(3),
    )
    saved_at = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
    metadata = ReviewDraftMetadata(reference, saved_at, ReviewDraftId("draft-2"))
    assert metadata.reference is reference
    assert metadata.saved_at is saved_at
    assert metadata.superseded_by == ReviewDraftId("draft-2")

    basis = ReviewDecisionBasis(
        ReviewId("review-1"),
        ReviewPackageReference(ReviewPackageId("package-1"), VersionNumber(1)),
        reference,
    )
    decided_at = datetime(2026, 8, 9, 12, 1, tzinfo=UTC)
    snapshot = ReviewDecisionSnapshot(
        ReviewDecisionId("decision-1"),
        basis,
        ReviewDecisionOutcome.REQUEST_MORE_INFORMATION,
        decided_at,
    )
    assert snapshot.basis is basis
    assert snapshot.outcome is ReviewDecisionOutcome.REQUEST_MORE_INFORMATION
    assert snapshot.decided_at is decided_at
    assert not hasattr(snapshot, "approved_strategy")

    with pytest.raises(FrozenInstanceError):
        header.status = ReviewPackageStatus.SUBMITTED  # type: ignore[misc]


def test_review_draft_metadata_supersession_is_typed_or_absent() -> None:
    reference = ReviewDraftReference(
        ReviewDraftId("draft-1"),
        ReviewPackageId("package-1"),
        Revision(0),
    )
    metadata = ReviewDraftMetadata(
        reference,
        datetime(2026, 8, 9, tzinfo=UTC),
        None,
    )
    assert metadata.superseded_by is None


def test_review_package_snapshot_preserves_group_order_and_content_identity() -> None:
    identity = ReviewPackageIdentity(
        ReviewPackageId("package-1"),
        ReviewId("review-1"),
        TaskId("task-1"),
        VersionNumber(1),
    )
    header = ReviewPackageHeader(
        identity,
        ReviewPackageStatus.ACTIVE,
        (),
        (),
        (),
    )
    content = StructuredContent.from_mapping({"value": {"nested": [1, 2]}})
    names = tuple(ReviewSemanticGroupName)
    groups = tuple(
        ReviewSemanticGroup(
            name,
            content,
            ContentOrigin.MODEL if index % 2 == 0 else None,
        )
        for index, name in enumerate(reversed(names))
    )

    snapshot = ReviewPackageSnapshot(header, groups)

    assert snapshot.header is header
    assert snapshot.semantic_groups is groups
    assert tuple(group.group for group in snapshot.semantic_groups) == tuple(
        reversed(names)
    )
    assert all(group.content is content for group in snapshot.semantic_groups)
    with pytest.raises(FrozenInstanceError):
        snapshot.header = header  # type: ignore[misc]


@pytest.mark.parametrize(
    "semantic_groups",
    [
        tuple(
            ReviewSemanticGroup(name, StructuredContent.from_mapping({}))
            for name in tuple(ReviewSemanticGroupName)[:-1]
        ),
        tuple(
            ReviewSemanticGroup(name, StructuredContent.from_mapping({}))
            for name in (
                *tuple(ReviewSemanticGroupName)[:-1],
                ReviewSemanticGroupName.VERSION_CONTEXT,
            )
        ),
        (
            *tuple(
                ReviewSemanticGroup(name, StructuredContent.from_mapping({}))
                for name in tuple(ReviewSemanticGroupName)[:-1]
            ),
            ReviewSemanticGroup(
                "unknown",  # type: ignore[arg-type]
                StructuredContent.from_mapping({}),
            ),
        ),
    ],
)
def test_review_package_snapshot_rejects_invalid_group_membership(
    semantic_groups: tuple[ReviewSemanticGroup, ...],
) -> None:
    identity = ReviewPackageIdentity(
        ReviewPackageId("package-1"),
        ReviewId("review-1"),
        TaskId("task-1"),
        VersionNumber(1),
    )
    header = ReviewPackageHeader(identity, ReviewPackageStatus.ACTIVE, (), (), ())

    with pytest.raises(ValueError):
        ReviewPackageSnapshot(header, semantic_groups)
