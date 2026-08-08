"""Bootstrap may bind a module's private infrastructure implementation."""

from fixture_pkg.modules.brief.application.service import BriefService
from fixture_pkg.modules.brief.infrastructure.adapter import BriefAdapter


def compose() -> tuple[BriefAdapter, BriefService]:
    return BriefAdapter(), BriefService()
