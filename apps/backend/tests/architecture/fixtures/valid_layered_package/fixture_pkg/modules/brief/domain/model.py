"""Pure domain layer: standard library only (legal)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BriefDraft:
    """A draft business artifact (test-only)."""

    title: str
    summary: str
