"""VIOLATION: entrypoint bypasses the application layer into a repository."""

from fixture_pkg.modules.brief.infrastructure.repository import BriefRepository

REPO = BriefRepository()
