"""Framework-neutral Human Review metadata and decision snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.shared_kernel import (
    ContentOrigin,
    DomainVersionId,
    ReviewDecisionId,
    ReviewDraftId,
    StructuredContent,
    TaskId,
    VersionNumber,
)

from .contracts import (
    ApprovedStrategySemanticGroupName,
    ReviewDecisionBasis,
    ReviewDecisionOutcome,
    ReviewDraftReference,
    ReviewPackageIdentity,
    ReviewPackageStatus,
    ReviewSemanticGroupName,
)


@dataclass(frozen=True, slots=True)
class ReviewSemanticGroup:
    """Immutable structured content for one Review Package semantic group."""

    group: ReviewSemanticGroupName
    content: StructuredContent
    origin: ContentOrigin | None = None


@dataclass(frozen=True, slots=True)
class ReviewPackageHeader:
    """Immutable Package ownership, lifecycle, and upstream-version metadata."""

    identity: ReviewPackageIdentity
    status: ReviewPackageStatus
    upstream_versions: tuple[DomainVersionReference, ...]
    required_decisions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReviewPackageSnapshot:
    """Immutable Review Package header and complete semantic-group projection."""

    header: ReviewPackageHeader
    semantic_groups: tuple[ReviewSemanticGroup, ...]

    def __post_init__(self) -> None:
        expected_names = tuple(ReviewSemanticGroupName)
        supplied_names = tuple(group.group for group in self.semantic_groups)
        if (
            len(supplied_names) != len(expected_names)
            or any(name not in expected_names for name in supplied_names)
            or any(supplied_names.count(name) != 1 for name in expected_names)
        ):
            raise ValueError("invalid review semantic-group membership")


@dataclass(frozen=True, slots=True)
class ReviewDraftMetadata:
    """Immutable metadata for one saved Draft revision, without its content."""

    reference: ReviewDraftReference
    saved_at: datetime
    superseded_by: ReviewDraftId | None


@dataclass(frozen=True, slots=True)
class ReviewDraftSnapshot:
    """Immutable full structured content and metadata Draft projection."""

    metadata: ReviewDraftMetadata
    content: StructuredContent


@dataclass(frozen=True, slots=True)
class ReviewDecisionSnapshot:
    """Immutable outcome projection bound to one exact Package/Draft basis."""

    review_decision_id: ReviewDecisionId
    basis: ReviewDecisionBasis
    outcome: ReviewDecisionOutcome
    decided_at: datetime


@dataclass(frozen=True, slots=True)
class ApprovedStrategySemanticGroup:
    """Immutable structured content for one Approved Strategy semantic group."""

    group: ApprovedStrategySemanticGroupName
    content: StructuredContent
    origin: ContentOrigin | None = None


@dataclass(frozen=True, slots=True)
class ApprovedStrategyVersionSnapshot:
    """Immutable projection of one Approved Strategy domain version."""

    approved_strategy_version_id: DomainVersionId
    task_id: TaskId
    version_number: VersionNumber
    valid: bool
    created_at: datetime
    upstream_versions: tuple[DomainVersionReference, ...]
    semantic_groups: tuple[ApprovedStrategySemanticGroup, ...]
    hypotheses: tuple[str, ...]
    evidence_limitations: tuple[str, ...]
    risks: tuple[str, ...]

    def __post_init__(self) -> None:
        expected_names = tuple(ApprovedStrategySemanticGroupName)
        supplied_names = tuple(group.group for group in self.semantic_groups)
        if (
            len(supplied_names) != len(expected_names)
            or any(name not in expected_names for name in supplied_names)
            or any(supplied_names.count(name) != 1 for name in expected_names)
        ):
            raise ValueError("invalid approved strategy semantic-group membership")


__all__ = [
    "ReviewPackageHeader",
    "ReviewDraftMetadata",
    "ReviewDraftSnapshot",
    "ReviewDecisionSnapshot",
    "ReviewSemanticGroup",
    "ReviewPackageSnapshot",
    "ApprovedStrategySemanticGroup",
    "ApprovedStrategyVersionSnapshot",
]
