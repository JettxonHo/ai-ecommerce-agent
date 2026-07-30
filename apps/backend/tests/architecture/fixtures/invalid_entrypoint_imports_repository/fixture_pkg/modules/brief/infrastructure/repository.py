"""Simulated repository implementation (the illegal target)."""


class BriefRepository:
    """A persistence detail entrypoints must never bypass into."""

    def fetch(self) -> str:
        """Simulated fetch."""
        return "row"
