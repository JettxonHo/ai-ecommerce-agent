"""Framework-neutral Xiaohongshu Brief version contract values."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.shared_kernel import (
    ContentOrigin,
    DomainVersionId,
    ResourceReference,
    StructuredContent,
    TaskId,
    VersionNumber,
)


class XiaohongshuBriefSemanticGroupName(StrEnum):
    """The exact six semantic groups in a Xiaohongshu Brief version."""

    PLATFORM_AND_CAMPAIGN_CONTEXT = "platform_and_campaign_context"
    NOTE_FORMAT_AND_CONTENT_MODE = "note_format_and_content_mode"
    CREATIVE_STRUCTURE_DIRECTIONS = "creative_structure_directions"
    DISCOVERY_AND_ACTION_DIRECTIONS = "discovery_and_action_directions"
    EVIDENCE_AND_PLATFORM_CONSTRAINTS = "evidence_and_platform_constraints"
    WORKFLOW_AND_VERSION_CONTEXT = "workflow_and_version_context"


@dataclass(frozen=True, slots=True)
class XiaohongshuBriefSemanticGroup:
    """Immutable structured content for one Xiaohongshu Brief group."""

    group: XiaohongshuBriefSemanticGroupName
    content: StructuredContent
    origin: ContentOrigin | None = None


@dataclass(frozen=True, slots=True)
class XiaohongshuBriefVersionSnapshot:
    """Immutable projection of one Xiaohongshu Brief domain version."""

    brief_version_id: DomainVersionId
    task_id: TaskId
    version_number: VersionNumber
    valid: bool
    created_at: datetime
    upstream_versions: tuple[DomainVersionReference, ...]
    semantic_groups: tuple[XiaohongshuBriefSemanticGroup, ...]
    hypotheses: tuple[str, ...]
    evidence_limitations: tuple[str, ...]
    risks: tuple[str, ...]
    evidence_references: tuple[ResourceReference, ...]

    def __post_init__(self) -> None:
        expected_names = tuple(XiaohongshuBriefSemanticGroupName)
        supplied_names = tuple(group.group for group in self.semantic_groups)
        if (
            len(supplied_names) != len(expected_names)
            or any(name not in expected_names for name in supplied_names)
            or any(supplied_names.count(name) != 1 for name in expected_names)
        ):
            raise ValueError("invalid Xiaohongshu Brief semantic-group membership")


__all__ = [
    "XiaohongshuBriefSemanticGroupName",
    "XiaohongshuBriefSemanticGroup",
    "XiaohongshuBriefVersionSnapshot",
]
