"""VIOLATION (with alpha): beta and alpha form a cycle through public facades."""

from fixture_pkg.modules.alpha.public.api import alpha_label


def beta_label() -> str:
    """Public facade that depends back on alpha's facade."""
    return f"beta+{alpha_label()}"
