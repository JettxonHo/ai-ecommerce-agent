"""Shared kernel value object: depends on nothing above it (legal)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Minimal shared value type."""

    amount_cents: int
    currency: str
