"""Publicly implementable Source association application protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain import SourceAssociationSnapshot
from .association_commands import RemoveSourceAssociation, ReplaceSourceAssociation
from .association_results import SourceAssociationReplacementSnapshot


@runtime_checkable
class SourceAssociationApplication(Protocol):
    """Synchronous, framework-neutral Source association use-case surface."""

    def remove_source_association(
        self, command: RemoveSourceAssociation
    ) -> SourceAssociationSnapshot:
        """Remove one active Task-to-Source association."""

        ...

    def replace_source_association(
        self, command: ReplaceSourceAssociation
    ) -> SourceAssociationReplacementSnapshot:
        """Replace one active association with a distinct active association."""

        ...


__all__ = ["SourceAssociationApplication"]
