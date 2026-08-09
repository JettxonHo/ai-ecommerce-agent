"""Immutable results for Source association application intents."""

from __future__ import annotations

from dataclasses import dataclass

from ..domain import SourceAssociationSnapshot


@dataclass(frozen=True, slots=True)
class SourceAssociationReplacementSnapshot:
    """The replaced association and its distinct active successor."""

    replaced_association: SourceAssociationSnapshot
    active_association: SourceAssociationSnapshot


__all__ = ["SourceAssociationReplacementSnapshot"]
