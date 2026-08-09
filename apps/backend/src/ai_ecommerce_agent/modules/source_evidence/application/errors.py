"""Technology-neutral persistence errors owned by Source and Evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceProcessingStatus,
)
from ai_ecommerce_agent.shared_kernel import (
    ProjectError,
    Revision,
    SafeContext,
    SourceVersionId,
)


@dataclass(slots=True)
class SourceEvidenceError(Exception):
    """Stable, technology-neutral application error for one Source Version."""

    error_code: str
    category: str
    message: str
    retryability: bool
    relevant_reference: SourceVersionId
    expected_revision: Revision | None = None
    actual_revision: Revision | None = None
    conflicting_state: SourceProcessingStatus | None = None
    recovery_hint: str | None = None

    def __post_init__(self) -> None:
        for name in ("error_code", "category", "message"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        Exception.__init__(self, self.message)


class SourceEvidencePersistenceError(ProjectError):
    """A non-integrity SQLAlchemy failure at the persistence boundary."""

    def __init__(self, context: Mapping[str, str] | None = None) -> None:
        super().__init__(
            "source_evidence", "persistence_error", SafeContext.from_mapping(context)
        )


class SourceEvidenceRevisionConflictError(SourceEvidencePersistenceError):
    """A compare-and-swap update affected no row."""

    def __init__(
        self,
        *,
        resource: str,
        identity: str,
        expected_revision: Revision,
    ) -> None:
        ProjectError.__init__(
            self,
            "source_evidence",
            "revision_conflict",
            SafeContext.from_mapping(
                {
                    "resource": resource,
                    "identity": identity,
                    "expected_revision": str(expected_revision.value),
                }
            ),
        )


class SourceEvidenceOwnershipError(SourceEvidencePersistenceError):
    """A named Source-owned foreign key rejected an ownership relation."""

    def __init__(self, *, resource: str, constraint_name: str) -> None:
        ProjectError.__init__(
            self,
            "source_evidence",
            "ownership_conflict",
            SafeContext.from_mapping(
                {"resource": resource, "constraint": constraint_name}
            ),
        )


class SourceEvidenceConstraintError(SourceEvidencePersistenceError):
    """A non-owner integrity constraint rejected a persistence operation."""

    def __init__(self, *, constraint_name: str | None) -> None:
        ProjectError.__init__(
            self,
            "source_evidence",
            "constraint_violation",
            SafeContext.from_mapping(
                {"constraint": constraint_name} if constraint_name is not None else None
            ),
        )


__all__ = [
    "SourceEvidenceConstraintError",
    "SourceEvidenceError",
    "SourceEvidenceOwnershipError",
    "SourceEvidencePersistenceError",
    "SourceEvidenceRevisionConflictError",
]
