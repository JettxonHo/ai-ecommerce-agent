"""Immutable Source Version identity and logical version relationship."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from ai_ecommerce_agent.shared_kernel import SourceId, SourceVersionId, VersionNumber


@dataclass(frozen=True, slots=True)
class SourceVersion:
    """The immutable identity/version basis for one Source snapshot.

    Processing Current Truth is deliberately kept in
    :class:`SourceVersionProcessing`; no mutable processing field belongs on
    this identity record.
    """

    source_version_id: SourceVersionId
    source_id: SourceId
    version_number: VersionNumber

    @classmethod
    def create(
        cls,
        source_version_id: SourceVersionId,
        source_id: SourceId,
        version_number: VersionNumber,
    ) -> Self:
        """Create one immutable Source Version identity."""

        return cls(
            source_version_id=source_version_id,
            source_id=source_id,
            version_number=version_number,
        )


__all__ = ["SourceVersion"]
