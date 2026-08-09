"""Framework-neutral Human Review metadata and decision snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.shared_kernel import ReviewDecisionId, ReviewDraftId

from .contracts import (
    ReviewDecisionBasis,
    ReviewDecisionOutcome,
    ReviewDraftReference,
    ReviewPackageIdentity,
    ReviewPackageStatus,
)


@dataclass(frozen=True, slots=True)
class ReviewPackageHeader:
    """Immutable Package ownership, lifecycle, and upstream-version metadata."""

    identity: ReviewPackageIdentity
    status: ReviewPackageStatus
    upstream_versions: tuple[DomainVersionReference, ...]
    required_decisions: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReviewDraftMetadata:
    """Immutable metadata for one saved Draft revision, without its content."""

    reference: ReviewDraftReference
    saved_at: datetime
    superseded_by: ReviewDraftId | None


@dataclass(frozen=True, slots=True)
class ReviewDecisionSnapshot:
    """Immutable outcome projection bound to one exact Package/Draft basis."""

    review_decision_id: ReviewDecisionId
    basis: ReviewDecisionBasis
    outcome: ReviewDecisionOutcome
    decided_at: datetime


__all__ = [
    "ReviewPackageHeader",
    "ReviewDraftMetadata",
    "ReviewDecisionSnapshot",
]
