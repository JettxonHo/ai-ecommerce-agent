"""Stable Source catalogs and immutable read snapshots.

This first Source slice freezes only the framework-neutral public data
contracts.  Source entities, processing transitions, repositories, and
persistence adapters remain owned by later slices.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceId,
    SourceVersionId,
    TaskId,
    VersionNumber,
)


class SourceProcessingStatus(StrEnum):
    """The exact six-value SourceVersion processing lifecycle."""

    REGISTERED = "registered"
    PROCESSING = "processing"
    READY = "ready"
    READY_WITH_REJECTIONS = "ready_with_rejections"
    FAILED = "failed"
    SUPERSEDED = "superseded"


class SourceAssociationMembershipState(StrEnum):
    """The exact membership states for a TaskSourceAssociation."""

    ACTIVE = "active"
    REMOVED = "removed"
    REPLACED = "replaced"


@dataclass(frozen=True, slots=True)
class SourceVersionSnapshot:
    """Immutable projection of Source identity and processing Current Truth.

    Association membership is deliberately absent: it is owned by the
    separate :class:`SourceAssociationSnapshot` contract.
    """

    source_id: SourceId
    source_version_id: SourceVersionId
    version_number: VersionNumber
    processing_status: SourceProcessingStatus
    processing_revision: Revision
    failure_summary: str | None
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class SourceAssociationSnapshot:
    """Immutable projection of one revisioned TaskSourceAssociation."""

    source_association_id: SourceAssociationId
    task_id: TaskId
    source_id: SourceId
    source_version_id: SourceVersionId
    membership_state: SourceAssociationMembershipState
    revision: Revision
    replaced_by_association_id: SourceAssociationId | None


__all__ = [
    "SourceAssociationMembershipState",
    "SourceAssociationSnapshot",
    "SourceProcessingStatus",
    "SourceVersionSnapshot",
]
