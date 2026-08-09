"""Framework-neutral Human Review identity and lifecycle reference values."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ai_ecommerce_agent.shared_kernel import (
    ReviewDraftId,
    ReviewId,
    ReviewPackageId,
    Revision,
    TaskId,
    VersionNumber,
)


class ReviewPackageStatus(StrEnum):
    """The exact lifecycle catalog for an immutable Review Package snapshot."""

    ACTIVE = "active"
    SUPERSEDED = "superseded"
    SUBMITTED = "submitted"
    WITHDRAWN = "withdrawn"


class ReviewDecisionOutcome(StrEnum):
    """The exact explicit outcomes available to a Human Review decision."""

    APPROVED = "approved"
    REQUEST_MORE_INFORMATION = "request_more_information"
    REJECTED_FOR_REGENERATION = "rejected_for_regeneration"
    WITHDRAWN = "withdrawn"


class ReviewSemanticGroupName(StrEnum):
    """The exact seven semantic groups in a Human Review Package."""

    VERSION_CONTEXT = "version_context"
    POSITIONING_CANDIDATES = "positioning_candidates"
    KEY_FACTS_AND_INSIGHTS = "key_facts_and_insights"
    HYPOTHESES = "hypotheses"
    EVIDENCE_LIMITATIONS = "evidence_limitations"
    CONFLICTS_AND_STRATEGIC_RISKS = "conflicts_and_strategic_risks"
    MODEL_RECOMMENDATION = "model_recommendation"


@dataclass(frozen=True, slots=True)
class ReviewPackageIdentity:
    """Immutable owner and identity tuple for one Review Package snapshot."""

    review_package_id: ReviewPackageId
    review_id: ReviewId
    task_id: TaskId
    package_version: VersionNumber


@dataclass(frozen=True, slots=True)
class ReviewPackageReference:
    """Compact reference to one exact immutable Review Package snapshot."""

    review_package_id: ReviewPackageId
    package_version: VersionNumber


@dataclass(frozen=True, slots=True)
class ReviewDraftReference:
    """Reference to one mutable Review Draft revision."""

    review_draft_id: ReviewDraftId
    review_package_id: ReviewPackageId
    revision: Revision


@dataclass(frozen=True, slots=True)
class ReviewDecisionBasis:
    """Exact Review, Package-version, and Draft-revision decision basis."""

    review_id: ReviewId
    review_package: ReviewPackageReference
    review_draft: ReviewDraftReference

    def __post_init__(self) -> None:
        if self.review_package.review_package_id != self.review_draft.review_package_id:
            raise ValueError("review_package_id values must match")


__all__ = [
    "ReviewPackageStatus",
    "ReviewDecisionOutcome",
    "ReviewPackageIdentity",
    "ReviewPackageReference",
    "ReviewDraftReference",
    "ReviewDecisionBasis",
    "ReviewSemanticGroupName",
]
