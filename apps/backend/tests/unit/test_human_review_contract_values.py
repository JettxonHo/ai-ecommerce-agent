"""Focused unit coverage for Human Review contract values."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.human_review.public import (
    ReviewDecisionBasis,
    ReviewDecisionOutcome,
    ReviewDraftReference,
    ReviewPackageIdentity,
    ReviewPackageReference,
    ReviewPackageStatus,
)
from ai_ecommerce_agent.shared_kernel import (
    ReviewDraftId,
    ReviewId,
    ReviewPackageId,
    Revision,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def test_review_catalogs_are_exact_and_alias_free() -> None:
    assert list(ReviewPackageStatus.__members__) == [
        "ACTIVE",
        "SUPERSEDED",
        "SUBMITTED",
        "WITHDRAWN",
    ]
    assert [member.value for member in ReviewPackageStatus] == [
        "active",
        "superseded",
        "submitted",
        "withdrawn",
    ]
    assert list(ReviewDecisionOutcome.__members__) == [
        "APPROVED",
        "REQUEST_MORE_INFORMATION",
        "REJECTED_FOR_REGENERATION",
        "WITHDRAWN",
    ]
    assert [member.value for member in ReviewDecisionOutcome] == [
        "approved",
        "request_more_information",
        "rejected_for_regeneration",
        "withdrawn",
    ]


def test_identity_reference_values_are_frozen_slotted_and_exactly_typed() -> None:
    expected_fields = {
        ReviewPackageIdentity: (
            "review_package_id",
            "review_id",
            "task_id",
            "package_version",
        ),
        ReviewPackageReference: ("review_package_id", "package_version"),
        ReviewDraftReference: ("review_draft_id", "review_package_id", "revision"),
        ReviewDecisionBasis: ("review_id", "review_package", "review_draft"),
    }
    expected_types = {
        ReviewPackageIdentity: {
            "review_package_id": ReviewPackageId,
            "review_id": ReviewId,
            "task_id": TaskId,
            "package_version": VersionNumber,
        },
        ReviewPackageReference: {
            "review_package_id": ReviewPackageId,
            "package_version": VersionNumber,
        },
        ReviewDraftReference: {
            "review_draft_id": ReviewDraftId,
            "review_package_id": ReviewPackageId,
            "revision": Revision,
        },
        ReviewDecisionBasis: {
            "review_id": ReviewId,
            "review_package": ReviewPackageReference,
            "review_draft": ReviewDraftReference,
        },
    }

    for value_type, names in expected_fields.items():
        assert is_dataclass(value_type)
        assert cast(Any, value_type).__dataclass_params__.frozen
        assert tuple(field.name for field in fields(value_type)) == names
        assert value_type.__slots__ == names
        assert get_type_hints(value_type) == expected_types[value_type]

    identity = ReviewPackageIdentity(
        ReviewPackageId("package-1"),
        ReviewId("review-1"),
        TaskId("task-1"),
        VersionNumber(1),
    )
    with pytest.raises(FrozenInstanceError):
        identity.review_id = ReviewId("review-2")  # type: ignore[misc]


def test_decision_basis_requires_matching_package_identity() -> None:
    package = ReviewPackageReference(ReviewPackageId("package-1"), VersionNumber(2))
    draft = ReviewDraftReference(
        ReviewDraftId("draft-1"),
        ReviewPackageId("package-1"),
        Revision(3),
    )
    basis = ReviewDecisionBasis(ReviewId("review-1"), package, draft)
    assert basis.review_package is package
    assert basis.review_draft is draft

    mismatched_draft = ReviewDraftReference(
        ReviewDraftId("draft-2"),
        ReviewPackageId("package-2"),
        Revision(3),
    )
    with pytest.raises(ValueError, match="review_package_id values must match"):
        ReviewDecisionBasis(ReviewId("review-1"), package, mismatched_draft)
