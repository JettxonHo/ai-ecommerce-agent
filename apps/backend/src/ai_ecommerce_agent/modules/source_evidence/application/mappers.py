"""Internal projections from Source domain values to public snapshots."""

from __future__ import annotations

from ..domain import (
    SourceAssociationReplacement,
    SourceAssociationSnapshot,
    SourceVersion,
    SourceVersionProcessing,
    SourceVersionSnapshot,
    TaskSourceAssociation,
)
from .association_results import SourceAssociationReplacementSnapshot


def source_version_to_snapshot(
    source_version: SourceVersion, processing: SourceVersionProcessing
) -> SourceVersionSnapshot:
    """Project matching Source identity and processing Current Truth."""

    if source_version.source_version_id != processing.source_version_id:
        raise ValueError("Source Version and processing identities must match")
    return SourceVersionSnapshot(
        source_id=source_version.source_id,
        source_version_id=source_version.source_version_id,
        version_number=source_version.version_number,
        processing_status=processing.status,
        processing_revision=processing.revision,
        failure_summary=processing.failure_summary,
        updated_at=processing.updated_at,
    )


def task_source_association_to_snapshot(
    association: TaskSourceAssociation,
) -> SourceAssociationSnapshot:
    """Project one association without changing its domain value."""

    return SourceAssociationSnapshot(
        source_association_id=association.source_association_id,
        task_id=association.task_id,
        source_id=association.source_id,
        source_version_id=association.source_version_id,
        membership_state=association.membership_state,
        revision=association.revision,
        replaced_by_association_id=association.replaced_by_association_id,
    )


def source_association_replacement_to_snapshot(
    replacement: SourceAssociationReplacement,
) -> SourceAssociationReplacementSnapshot:
    """Project replacement values in replaced-then-active order."""

    return SourceAssociationReplacementSnapshot(
        replaced_association=task_source_association_to_snapshot(
            replacement.replaced_association
        ),
        active_association=task_source_association_to_snapshot(
            replacement.active_association
        ),
    )
