"""Framework-neutral Task Management catalog and snapshot contracts."""

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
    "RunSnapshot",
    "RunStatus",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "TaskSnapshot",
    "TaskStatus",
]
