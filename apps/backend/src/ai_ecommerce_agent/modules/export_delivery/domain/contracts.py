"""Framework-neutral immutable Export Delivery contract values."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.shared_kernel import ExportSnapshotId, Revision, TaskId


class ExportBriefKind(StrEnum):
    """The two brief families that can be exported."""

    MARKETING = "marketing"
    XIAOHONGSHU = "xiaohongshu"


def _require_non_empty(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if not value.strip():
        raise ValueError(f"{field_name} must be non-empty")


@dataclass(frozen=True, slots=True)
class ExportBasis:
    """Exact version and evidence context selected for one export."""

    task_id: TaskId
    task_revision: Revision
    brief_kind: ExportBriefKind
    brief_version: DomainVersionReference
    upstream_versions: tuple[DomainVersionReference, ...]
    hypotheses: tuple[str, ...]
    evidence_limitations: tuple[str, ...]
    risks: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExportPreview:
    """Immutable preview metadata bound to one exact export basis."""

    basis: ExportBasis
    template_version: str
    file_name: str
    media_type: str

    def __post_init__(self) -> None:
        _require_non_empty(self.template_version, "template_version")
        _require_non_empty(self.file_name, "file_name")
        _require_non_empty(self.media_type, "media_type")


@dataclass(frozen=True, slots=True)
class ConfirmExportRequest:
    """Typed confirmation carrying the exact preview basis."""

    basis: ExportBasis


@dataclass(frozen=True, slots=True)
class ExportSnapshot:
    """Immutable record of one confirmed Markdown export."""

    export_snapshot_id: ExportSnapshotId
    task_id: TaskId
    brief_kind: ExportBriefKind
    brief_version: DomainVersionReference
    upstream_versions: tuple[DomainVersionReference, ...]
    exported_at: datetime
    file_name: str
    media_type: str
    content_location: str
    template_version: str

    def __post_init__(self) -> None:
        _require_non_empty(self.file_name, "file_name")
        _require_non_empty(self.media_type, "media_type")
        _require_non_empty(self.content_location, "content_location")
        _require_non_empty(self.template_version, "template_version")


__all__ = [
    "ExportBriefKind",
    "ExportBasis",
    "ExportPreview",
    "ConfirmExportRequest",
    "ExportSnapshot",
]
