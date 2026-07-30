"""Simulated repository implementation (illegal skill dependency)."""


class BriefRepository:
    """A persistence detail skills must not import or receive."""

    def fetch(self) -> str:
        """Simulated fetch."""
        return "row"
