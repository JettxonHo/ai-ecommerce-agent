"""Stable application and persistence errors for Task Management.

The application error is the only error value that crosses the module public
facade.  Adapter errors remain private implementation details and are
translated by the application service before they reach a caller.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from ai_ecommerce_agent.modules.task_management.domain import StageReference
from ai_ecommerce_agent.shared_kernel import ProjectError, RunId, SafeContext, TaskId


class TaskManagementResourceKind(StrEnum):
    """Resource kinds that can be referenced by a public error."""

    TASK = "task"
    RUN = "run"
    STAGE = "stage"


@dataclass(frozen=True, slots=True)
class TaskManagementResourceReference:
    """Typed, immutable reference used in public error context."""

    kind: TaskManagementResourceKind
    task_id: TaskId | None = None
    run_id: RunId | None = None
    stage: StageReference | None = None

    def __post_init__(self) -> None:
        if self.kind is TaskManagementResourceKind.TASK:
            valid = (
                self.task_id is not None and self.run_id is None and self.stage is None
            )
        elif self.kind is TaskManagementResourceKind.RUN:
            valid = (
                self.task_id is None and self.run_id is not None and self.stage is None
            )
        else:
            valid = (
                self.task_id is not None
                and self.run_id is None
                and self.stage is not None
            )
        if not valid:
            raise ValueError("resource reference fields do not match resource kind")


@dataclass(slots=True)
class TaskManagementError(Exception):
    """Structured, technology-neutral failure returned by application use cases.

    ``error_code`` is the stable machine-facing discriminator.  The remaining
    fields are deliberately shallow and safe so an HTTP, worker, or graph
    adapter can map the value without inspecting a driver exception or an ORM
    object.  ``retryability`` is false for semantic conflicts and domain
    validation; only an unavailable persistence boundary is retryable here.
    """

    error_code: str
    category: str
    message: str
    retryability: bool
    relevant_reference: TaskManagementResourceReference
    expected_revision: int | None = None
    actual_revision: int | None = None
    conflicting_state: str | None = None
    recovery_hint: str | None = None

    def __post_init__(self) -> None:
        for name in ("error_code", "category", "message"):
            value = getattr(self, name)
            if not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        Exception.__init__(self, self.message)


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
    "TaskManagementError",
    "TaskManagementOwnershipError",
    "TaskManagementPersistenceError",
    "TaskManagementRevisionConflictError",
    "TaskManagementResourceKind",
    "TaskManagementResourceReference",
]
