"""Infrastructure layer: may depend on application and domain (legal)."""

from fixture_pkg.modules.brief.application.service import compose_draft
from fixture_pkg.modules.brief.domain.model import BriefDraft


def compose_and_serialize(title: str, summary: str) -> str:
    """Implement an outward-facing adapter over the use case."""
    draft: BriefDraft = compose_draft(title, summary)
    return f"{draft.title}:{draft.summary}"
