"""Immutable Source and association application queries."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import (
    SourceAssociationId,
    SourceVersionId,
    TaskId,
)


@dataclass(frozen=True, slots=True)
class GetSourceVersion:
    """Read one immutable Source Version composite snapshot."""

    source_version_id: SourceVersionId


@dataclass(frozen=True, slots=True)
class GetSourceAssociation:
    """Read one Task-scoped Source association snapshot."""

    task_id: TaskId
    source_association_id: SourceAssociationId


__all__ = ["GetSourceAssociation", "GetSourceVersion"]
