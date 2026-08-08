"""Task Management catalogs, snapshots, and internal domain entities."""

from .errors import InvalidTransitionError, OwnershipError, RevisionConflictError
from .ownership import (
    require_stage_run,
    require_task_current_run,
    require_task_owns_run,
    require_task_owns_stage,
)
from .run import Run
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
from .stage import Stage
from .task import Task

__all__ = [
    "DomainVersionReference",
    "InvalidTransitionError",
    "OwnershipError",
    "RevisionConflictError",
    "Run",
    "RunSnapshot",
    "RunStatus",
    "StageReference",
    "Stage",
    "StageSnapshot",
    "StageStatus",
    "TaskSnapshot",
    "Task",
    "TaskStatus",
    "require_stage_run",
    "require_task_current_run",
    "require_task_owns_run",
    "require_task_owns_stage",
]
