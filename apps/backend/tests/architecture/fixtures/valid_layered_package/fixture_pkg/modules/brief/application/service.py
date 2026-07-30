"""Application layer: may depend on same-module domain (legal)."""

from fixture_pkg.modules.brief.domain.model import BriefDraft


def compose_draft(title: str, summary: str) -> BriefDraft:
    """Compose a draft through the domain model."""
    return BriefDraft(title=title, summary=summary)
