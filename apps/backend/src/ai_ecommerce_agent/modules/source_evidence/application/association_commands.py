"""Immutable application commands for Source association membership."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceVersionId,
    TaskId,
)


@dataclass(frozen=True, slots=True)
class RemoveSourceAssociation:
    """Request removal of one active Task-to-Source association."""

    task_id: TaskId
    source_association_id: SourceAssociationId
    expected_revision: Revision


@dataclass(frozen=True, slots=True)
class ReplaceSourceAssociation:
    """Request replacement with a distinct association and existing version."""

    task_id: TaskId
    source_association_id: SourceAssociationId
    replacement_association_id: SourceAssociationId
    replacement_source_version_id: SourceVersionId
    expected_revision: Revision


__all__ = ["RemoveSourceAssociation", "ReplaceSourceAssociation"]
