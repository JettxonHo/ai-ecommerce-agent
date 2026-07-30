"""Structured architecture violation reports (FND-002, RFC-001-DQ-09).

Every architecture failure must be locatable. A violation always carries
four fields — the rule that was broken, the source module, the illegal
target, and the boundary that should have been respected — and renders
them in a stable, greppable format. ``Architecture test failed`` is never
an acceptable failure message.
"""

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Violation:
    """One architecture rule violation with full location context."""

    rule: str
    source: str
    illegal_target: str
    expected_boundary: str

    def render(self) -> str:
        """Render the four required report fields."""
        return (
            f"Rule: {self.rule}\n"
            f"Source: {self.source}\n"
            f"Illegal Target: {self.illegal_target}\n"
            f"Expected Boundary: {self.expected_boundary}"
        )


def render_all(violations: list[Violation]) -> str:
    """Render every violation; used to build pytest failure messages."""
    return "\n\n".join(violation.render() for violation in violations)
