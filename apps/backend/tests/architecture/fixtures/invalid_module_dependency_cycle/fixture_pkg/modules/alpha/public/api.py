"""VIOLATION (with beta): alpha and beta form a cycle through public facades."""

from fixture_pkg.modules.beta.public.api import beta_label


def alpha_label() -> str:
    """Public facade that depends back on beta's facade."""
    return f"alpha+{beta_label()}"
