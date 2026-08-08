"""Project-owned persistence errors for the Task Management adapter."""

from __future__ import annotations

from collections.abc import Mapping

from ai_ecommerce_agent.shared_kernel import ProjectError, SafeContext


class TaskManagementPersistenceError(ProjectError):
    """Stable application error replacing database-driver exceptions."""

    def __init__(
        self,
        code: str = "persistence_error",
        context: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__("task_management", code, SafeContext.from_mapping(context))


class TaskManagementRevisionConflictError(TaskManagementPersistenceError):
    """An expected-revision compare-and-swap updated no row."""

    def __init__(self, *, resource: str, expected_revision: int) -> None:
        super().__init__(
            "revision_conflict",
            {"resource": resource, "expected_revision": str(expected_revision)},
        )


class TaskManagementOwnershipError(TaskManagementPersistenceError):
    """A named owner foreign key rejected a cross-Task pointer."""

    def __init__(self, *, resource: str, constraint_name: str) -> None:
        super().__init__(
            "ownership_conflict",
            {"resource": resource, "constraint": constraint_name},
        )


class TaskManagementConstraintError(TaskManagementPersistenceError):
    """A non-owner named database constraint rejected a write."""

    def __init__(self, *, constraint_name: str | None) -> None:
        super().__init__(
            "constraint_violation",
            {"constraint": constraint_name} if constraint_name else None,
        )


__all__ = [
    "TaskManagementConstraintError",
    "TaskManagementOwnershipError",
    "TaskManagementPersistenceError",
    "TaskManagementRevisionConflictError",
]
