"""Internal domain errors for Task and Run lifecycle rules."""

from __future__ import annotations

from collections.abc import Mapping

from ai_ecommerce_agent.shared_kernel import ProjectError, Revision, SafeContext


def _context(values: Mapping[str, str]) -> SafeContext:
    """Copy already-safe transition metadata into the project error."""

    return SafeContext.from_mapping(values)


class RevisionConflictError(ProjectError):
    """The caller attempted to mutate a stale mutable domain entity."""

    def __init__(
        self,
        *,
        resource: str,
        expected: Revision,
        current: Revision,
    ) -> None:
        super().__init__(
            "task_management",
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
    """A named lifecycle intent is not legal for the current entity state."""

    def __init__(self, *, resource: str, status: str, intent: str) -> None:
        super().__init__(
            "task_management",
            "invalid_transition",
            _context({"resource": resource, "status": status, "intent": intent}),
        )


class OwnershipError(ProjectError):
    """A Task/Run/Stage relationship crosses its owning Task boundary."""

    def __init__(
        self,
        *,
        resource: str,
        context: Mapping[str, str] | None = None,
    ) -> None:
        values = {"resource": resource}
        if context is not None:
            values.update(context)
        super().__init__(
            "task_management",
            "ownership_conflict",
            _context(values),
        )


__all__ = ["InvalidTransitionError", "OwnershipError", "RevisionConflictError"]
