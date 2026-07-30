"""Orchestration: may depend on module public contracts + shared kernel (legal)."""

from fixture_pkg.modules.brief.public.api import compose_brief
from fixture_pkg.shared_kernel.money import Money


def run_flow() -> str:
    """Coordinate through public contracts only."""
    budget = Money(amount_cents=500, currency="CNY")
    return f"{compose_brief('seed')}@{budget.currency}"
