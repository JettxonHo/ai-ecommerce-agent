"""Only stable cross-module facade for Task Management.

The facade intentionally exports immutable operation contracts, the
application protocol, stable application errors, and A1 snapshots.  Domain
entities, repository/UoW ports, SQLAlchemy adapters, and concrete services
remain module-private.
"""

from .application.commands import CreateDraftTask, PrepareInitialRun
from .application.errors import (
    TaskManagementError,
    TaskManagementResourceKind,
    TaskManagementResourceReference,
)
from .application.protocols import TaskManagementApplication
from .application.queries import GetRun, GetStage, GetTask, ListTasks
from .application.results import PrepareInitialRunResult
from .domain import (
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
    "CreateDraftTask",
    "DomainVersionReference",
    "GetRun",
    "GetStage",
    "GetTask",
    "ListTasks",
    "RunSnapshot",
    "RunStatus",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "PrepareInitialRun",
    "PrepareInitialRunResult",
    "TaskManagementApplication",
    "TaskManagementError",
    "TaskManagementResourceKind",
    "TaskManagementResourceReference",
    "TaskSnapshot",
    "TaskStatus",
]
