"""Shared kernel value object (legal dependency for orchestration)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Minimal shared value type."""

    amount_cents: int
    currency: str
