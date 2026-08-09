"""Immutable application commands for Source processing Current Truth."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.shared_kernel import Revision, SourceVersionId


def _require_timezone_aware(value: datetime) -> None:
    """Reject timestamps that cannot unambiguously represent an instant."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("updated_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class StartSourceProcessing:
    """Request the registered or failed Source Version enter processing."""

    source_version_id: SourceVersionId
    expected_revision: Revision
    updated_at: datetime

    def __post_init__(self) -> None:
        _require_timezone_aware(self.updated_at)


@dataclass(frozen=True, slots=True)
class MarkSourceReady:
    """Request a Source Version transition to ready."""

    source_version_id: SourceVersionId
    expected_revision: Revision
    updated_at: datetime

    def __post_init__(self) -> None:
        _require_timezone_aware(self.updated_at)


@dataclass(frozen=True, slots=True)
class MarkSourceReadyWithRejections:
    """Request a usable Source Version with bounded item rejections."""

    source_version_id: SourceVersionId
    expected_revision: Revision
    updated_at: datetime

    def __post_init__(self) -> None:
        _require_timezone_aware(self.updated_at)


@dataclass(frozen=True, slots=True)
class MarkSourceProcessingFailed:
    """Request a safe failure summary be recorded for a Source Version."""

    source_version_id: SourceVersionId
    expected_revision: Revision
    updated_at: datetime
    failure_summary: str

    def __post_init__(self) -> None:
        _require_timezone_aware(self.updated_at)
        if not self.failure_summary.strip():
            raise ValueError("failure_summary must be non-empty")


@dataclass(frozen=True, slots=True)
class SupersedeSourceVersion:
    """Request a non-superseded Source Version become terminally obsolete."""

    source_version_id: SourceVersionId
    expected_revision: Revision
    updated_at: datetime

    def __post_init__(self) -> None:
        _require_timezone_aware(self.updated_at)


__all__ = [
    "MarkSourceProcessingFailed",
    "MarkSourceReady",
    "MarkSourceReadyWithRejections",
    "StartSourceProcessing",
    "SupersedeSourceVersion",
]
