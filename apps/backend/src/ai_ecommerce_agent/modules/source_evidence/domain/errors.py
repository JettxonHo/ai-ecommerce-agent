"""Internal errors for Source identity and processing lifecycle rules."""

from __future__ import annotations

from collections.abc import Mapping

from ai_ecommerce_agent.shared_kernel import ProjectError, Revision, SafeContext


def _context(values: Mapping[str, str]) -> SafeContext:
    """Copy already-safe transition metadata into a project error."""

    return SafeContext.from_mapping(values)


class RevisionConflictError(ProjectError):
    """The caller attempted to mutate stale processing Current Truth."""

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
    """A named processing intent is not legal for the current status."""

    def __init__(self, *, resource: str, status: str, intent: str) -> None:
        super().__init__(
            "source_evidence",
            "invalid_transition",
            _context({"resource": resource, "status": status, "intent": intent}),
        )


__all__ = ["InvalidTransitionError", "RevisionConflictError"]
