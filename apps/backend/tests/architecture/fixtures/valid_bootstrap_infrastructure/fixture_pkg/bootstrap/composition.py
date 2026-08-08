"""Bootstrap may bind a module's private infrastructure implementation."""

from fixture_pkg.modules.brief.infrastructure.adapter import BriefAdapter


def compose() -> BriefAdapter:
    return BriefAdapter()
