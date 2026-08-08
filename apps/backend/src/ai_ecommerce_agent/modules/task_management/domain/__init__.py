"""Framework-neutral Task Management domain contracts."""

from .errors import (
    InvalidTransitionError,
    OwnershipError,
    RevisionConflictError,
    TaskManagementDomainError,
)
from .ownership import (
    require_stage_run,
    require_task_current_run,
    require_task_owns_run,
    require_task_owns_stage,
)
from .snapshots import (
    DomainVersionReference,
    Run,
    RunSnapshot,
    RunStatus,
    Stage,
    StageReference,
    StageSnapshot,
    StageStatus,
    Task,
    TaskSnapshot,
    TaskStatus,
)

__all__ = [
    "DomainVersionReference",
    "InvalidTransitionError",
    "OwnershipError",
    "RevisionConflictError",
    "Run",
    "RunSnapshot",
    "RunStatus",
    "Stage",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "Task",
    "TaskManagementDomainError",
    "TaskSnapshot",
    "TaskStatus",
    "require_stage_run",
    "require_task_current_run",
    "require_task_owns_run",
    "require_task_owns_stage",
]
