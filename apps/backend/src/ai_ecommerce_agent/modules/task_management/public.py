"""Only stable cross-module facade for Task Management.

The facade exports immutable, framework-neutral snapshots, exact state
catalogs, and semantic errors.  Repository and Unit of Work ports deliberately
remain application-owned and are not imported here.
"""

from .application.errors import (
    RunNotFoundError,
    StageNotFoundError,
    TaskManagementApplicationError,
    TaskNotFoundError,
)
from .domain import (
    DomainVersionReference,
    InvalidTransitionError,
    RevisionConflictError,
    RunSnapshot,
    RunStatus,
    StageReference,
    StageSnapshot,
    StageStatus,
    TaskManagementDomainError,
    TaskSnapshot,
    TaskStatus,
)

__all__ = [
    "DomainVersionReference",
    "InvalidTransitionError",
    "RevisionConflictError",
    "RunNotFoundError",
    "RunSnapshot",
    "RunStatus",
    "StageNotFoundError",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "TaskManagementApplicationError",
    "TaskManagementDomainError",
    "TaskNotFoundError",
    "TaskSnapshot",
    "TaskStatus",
]
