"""Internal projections from Source domain values to public snapshots."""

from __future__ import annotations

from ..domain import SourceVersion, SourceVersionProcessing, SourceVersionSnapshot


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
