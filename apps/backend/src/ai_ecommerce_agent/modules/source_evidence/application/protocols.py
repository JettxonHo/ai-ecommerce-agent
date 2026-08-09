"""Publicly implementable Source processing application protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain import SourceVersionSnapshot
from .commands import (
    MarkSourceProcessingFailed,
    MarkSourceReady,
    MarkSourceReadyWithRejections,
    StartSourceProcessing,
    SupersedeSourceVersion,
)


@runtime_checkable
class SourceEvidenceApplication(Protocol):
    """Synchronous, framework-neutral Source processing use-case surface."""

    def start_source_processing(
        self, command: StartSourceProcessing
    ) -> SourceVersionSnapshot:
        """Start processing for one Source Version."""

        ...

    def mark_source_ready(self, command: MarkSourceReady) -> SourceVersionSnapshot:
        """Mark one Source Version ready."""

        ...

    def mark_source_ready_with_rejections(
        self, command: MarkSourceReadyWithRejections
    ) -> SourceVersionSnapshot:
        """Mark one Source Version ready with bounded rejections."""

        ...

    def mark_source_processing_failed(
        self, command: MarkSourceProcessingFailed
    ) -> SourceVersionSnapshot:
        """Record a safe processing failure summary."""

        ...

    def supersede_source_version(
        self, command: SupersedeSourceVersion
    ) -> SourceVersionSnapshot:
        """Supersede one Source Version."""

        ...


__all__ = ["SourceEvidenceApplication"]
