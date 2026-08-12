"""Safe application errors for the Task primary-input slice."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import ProjectError, Revision, SafeContext, TaskId


@dataclass(slots=True)
class PrimaryInputError(Exception):
    """Stable error that can cross the Source Evidence HTTP boundary."""

    error_code: str
    message: str
    task_id: TaskId
    retryability: bool = False
    expected_revision: Revision | None = None
    actual_revision: Revision | None = None

    def __post_init__(self) -> None:
        if not self.error_code.strip() or not self.message.strip():
            raise ValueError("primary input error fields must be non-empty")
        Exception.__init__(self, self.message)


class PrimaryInputNotFound(PrimaryInputError):
    """No current input exists for the requested Task."""

    def __init__(self, task_id: TaskId) -> None:
        super().__init__("not_found", "Primary input was not found", task_id)


class PrimaryInputPersistenceError(ProjectError):
    """A database failure translated to a safe project error."""

    def __init__(self) -> None:
        super().__init__("source_evidence", "primary_input_persistence", SafeContext())


class PrimaryInputOwnershipError(PrimaryInputPersistenceError):
    """A Task foreign-key owner constraint rejected the input row."""


class PrimaryInputConstraintError(PrimaryInputPersistenceError):
    """A named input persistence constraint rejected a write."""


class PrimaryInputRevisionConflictError(PrimaryInputPersistenceError):
    """A compare-and-swap update affected no current input row."""

    def __init__(self, *, expected_revision: Revision) -> None:
        ProjectError.__init__(
            self,
            "source_evidence",
            "primary_input_revision_conflict",
            SafeContext.from_mapping(
                {"expected_revision": str(expected_revision.value)}
            ),
        )


__all__ = [
    "PrimaryInputError",
    "PrimaryInputNotFound",
    "PrimaryInputConstraintError",
    "PrimaryInputOwnershipError",
    "PrimaryInputPersistenceError",
    "PrimaryInputRevisionConflictError",
]
