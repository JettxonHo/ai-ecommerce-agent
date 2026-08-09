"""Technology-neutral errors for Source association application intents."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceAssociationMembershipState,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
)


@dataclass(slots=True)
class SourceAssociationError(Exception):
    """Stable, catchable error for one Source association application intent."""

    error_code: str
    category: str
    message: str
    retryability: bool
    relevant_reference: SourceAssociationId
    expected_revision: Revision | None = None
    actual_revision: Revision | None = None
    conflicting_state: SourceAssociationMembershipState | None = None
    recovery_hint: str | None = None

    def __post_init__(self) -> None:
        for name in ("error_code", "category", "message"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        Exception.__init__(self, self.message)


__all__ = ["SourceAssociationError"]
