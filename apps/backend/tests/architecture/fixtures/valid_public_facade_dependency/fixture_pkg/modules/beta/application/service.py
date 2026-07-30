"""Beta application layer importing alpha THROUGH its public facade (legal)."""

from fixture_pkg.modules.alpha.public.api import AlphaSnapshot, read_alpha


def beta_uses_alpha() -> AlphaSnapshot:
    """Cross-module collaboration via the public facade only."""
    return read_alpha()
