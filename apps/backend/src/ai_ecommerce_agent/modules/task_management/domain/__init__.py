"""Framework-neutral Task Management domain contracts."""

from .errors import (
    InvalidTransitionError,
    RevisionConflictError,
    TaskManagementDomainError,
)
from .snapshots import (
    DomainVersionReference,
    RunSnapshot,
    RunStatus,
    StageReference,
    StageSnapshot,
    StageStatus,
    TaskSnapshot,
    TaskStatus,
)

__all__ = [
    "DomainVersionReference",
    "InvalidTransitionError",
    "RevisionConflictError",
    "RunSnapshot",
    "RunStatus",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "TaskManagementDomainError",
    "TaskSnapshot",
    "TaskStatus",
]
