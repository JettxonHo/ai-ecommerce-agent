"""Framework-neutral Marketing Brief version contract values."""

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


class MarketingBriefSemanticGroupName(StrEnum):
    """The exact six semantic groups in a Marketing Brief version."""

    OBJECTIVE_AND_AUDIENCE = "objective_and_audience"
    MESSAGE_ARCHITECTURE = "message_architecture"
    REASONS_TO_BELIEVE_AND_EVIDENCE = "reasons_to_believe_and_evidence"
    EXECUTION_DIRECTION = "execution_direction"
    CONSTRAINTS_AND_HONESTY = "constraints_and_honesty"
    VERSION_AND_WORKFLOW_CONTEXT = "version_and_workflow_context"


@dataclass(frozen=True, slots=True)
class MarketingBriefSemanticGroup:
    """Immutable structured content for one Marketing Brief semantic group."""

    group: MarketingBriefSemanticGroupName
    content: StructuredContent
    origin: ContentOrigin | None = None


@dataclass(frozen=True, slots=True)
class MarketingBriefVersionSnapshot:
    """Immutable projection of one Marketing Brief domain version."""

    brief_version_id: DomainVersionId
    task_id: TaskId
    version_number: VersionNumber
    valid: bool
    created_at: datetime
    upstream_versions: tuple[DomainVersionReference, ...]
    semantic_groups: tuple[MarketingBriefSemanticGroup, ...]
    hypotheses: tuple[str, ...]
    evidence_limitations: tuple[str, ...]
    risks: tuple[str, ...]
    evidence_references: tuple[ResourceReference, ...]

    def __post_init__(self) -> None:
        expected_names = tuple(MarketingBriefSemanticGroupName)
        supplied_names = tuple(group.group for group in self.semantic_groups)
        if (
            len(supplied_names) != len(expected_names)
            or any(name not in expected_names for name in supplied_names)
            or any(supplied_names.count(name) != 1 for name in expected_names)
        ):
            raise ValueError("invalid marketing brief semantic-group membership")


__all__ = [
    "MarketingBriefSemanticGroupName",
    "MarketingBriefSemanticGroup",
    "MarketingBriefVersionSnapshot",
]
