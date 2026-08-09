"""Internal errors for Source identity and membership lifecycle rules."""

from __future__ import annotations

from collections.abc import Mapping

from ai_ecommerce_agent.shared_kernel import ProjectError, Revision, SafeContext


def _context(values: Mapping[str, str]) -> SafeContext:
    """Copy already-safe transition metadata into a project error."""

    return SafeContext.from_mapping(values)


class RevisionConflictError(ProjectError):
    """The caller attempted to mutate stale Source Current Truth."""

    def __init__(
        self,
        *,
        resource: str,
        expected: Revision,
        current: Revision,
    ) -> None:
        super().__init__(
            "source_evidence",
            "revision_conflict",
            _context(
                {
                    "resource": resource,
                    "expected_revision": str(expected.value),
                    "current_revision": str(current.value),
                }
            ),
        )


class InvalidTransitionError(ProjectError):
    """A named Source intent is not legal for the current state."""

    def __init__(self, *, resource: str, status: str, intent: str) -> None:
        super().__init__(
            "source_evidence",
            "invalid_transition",
            _context({"resource": resource, "status": status, "intent": intent}),
        )


class OwnershipError(ProjectError):
    """A Source relationship crosses its owning Source boundary."""

    def __init__(self, *, resource: str) -> None:
        super().__init__(
            "source_evidence",
            "ownership_conflict",
            _context({"resource": resource}),
        )


class AssociationReplacementError(ProjectError):
    """A replacement violates a stable association identity invariant."""

    def __init__(self, *, reason: str) -> None:
        super().__init__(
            "source_evidence",
            "invalid_replacement",
            _context({"resource": "task_source_association", "reason": reason}),
        )


__all__ = [
    "AssociationReplacementError",
    "InvalidTransitionError",
    "OwnershipError",
    "RevisionConflictError",
]
