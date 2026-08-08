"""Stable, framework-neutral domain errors for Task Management.

The domain exposes project-owned semantic errors only.  Database, ORM,
LangGraph and HTTP errors belong to their respective adapters and must be
translated before reaching these contracts.
"""

from __future__ import annotations

from collections.abc import Mapping

from ai_ecommerce_agent.shared_kernel import ProjectError, SafeContext


class TaskManagementDomainError(ProjectError):
    """Base error for a rejected Task/Run/Stage domain operation."""

    def __init__(
        self,
        code: str,
        context: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            "task_management.domain", code, SafeContext.from_mapping(context)
        )


class RevisionConflictError(TaskManagementDomainError):
    """The caller supplied a stale expected revision."""

    def __init__(self, context: Mapping[str, str] | None = None) -> None:
        super().__init__("revision_conflict", context)


class InvalidTransitionError(TaskManagementDomainError):
    """A named lifecycle intent is not legal from the current state."""

    def __init__(self, context: Mapping[str, str] | None = None) -> None:
        super().__init__("invalid_transition", context)


__all__ = [
    "InvalidTransitionError",
    "RevisionConflictError",
    "TaskManagementDomainError",
]
