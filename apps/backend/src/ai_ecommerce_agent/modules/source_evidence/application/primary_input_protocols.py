"""Publicly implementable primary-input application protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain import PrimaryInputSnapshot
from .primary_input_commands import SavePrimaryInput
from .primary_input_queries import GetPrimaryInput


@runtime_checkable
class PrimaryInputApplication(Protocol):
    """Synchronous save/read surface consumed by the HTTP adapter."""

    def save_primary_input(self, command: SavePrimaryInput) -> PrimaryInputSnapshot:
        """Persist or replay the current Task primary input."""

        ...

    def get_primary_input(self, query: GetPrimaryInput) -> PrimaryInputSnapshot:
        """Read the current Task primary input."""

        ...


__all__ = ["PrimaryInputApplication"]
