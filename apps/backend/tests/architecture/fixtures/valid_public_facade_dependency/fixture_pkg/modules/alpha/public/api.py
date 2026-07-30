"""Alpha public facade: the only legal cross-module entry point."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AlphaSnapshot:
    """Immutable cross-module snapshot."""

    label: str


def read_alpha() -> AlphaSnapshot:
    """Expose a technology-neutral snapshot."""
    return AlphaSnapshot(label="alpha")
