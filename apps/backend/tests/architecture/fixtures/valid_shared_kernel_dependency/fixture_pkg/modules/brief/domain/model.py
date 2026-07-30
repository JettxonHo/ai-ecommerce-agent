"""Domain layer may depend on the approved shared kernel (legal)."""

from fixture_pkg.shared_kernel.money import Money


def sample_budget() -> Money:
    """Use a shared kernel value object from domain code."""
    return Money(amount_cents=1000, currency="CNY")
