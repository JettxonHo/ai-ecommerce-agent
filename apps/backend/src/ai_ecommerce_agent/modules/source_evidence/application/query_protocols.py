"""Publicly implementable Source immutable-read application protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain import SourceAssociationSnapshot, SourceVersionSnapshot
from .queries import GetSourceAssociation, GetSourceVersion


@runtime_checkable
class SourceEvidenceQueryApplication(Protocol):
    """Synchronous, framework-neutral Source immutable-read surface."""

    def get_source_version(self, query: GetSourceVersion) -> SourceVersionSnapshot:
        """Read one Source Version and its processing Current Truth."""

        ...

    def get_source_association(
        self, query: GetSourceAssociation
    ) -> SourceAssociationSnapshot:
        """Read one Task-scoped Source association."""

        ...


__all__ = ["SourceEvidenceQueryApplication"]
