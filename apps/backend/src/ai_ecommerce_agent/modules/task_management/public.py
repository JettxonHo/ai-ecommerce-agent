"""Only stable cross-module facade for Task Management.

The A1 facade exports only exact state/reference catalogs and immutable,
framework-neutral snapshot DTOs.  Complete public error contracts are
deferred to #89, where the accepted RFC-001 message/retryability/reference
requirements will be defined.
"""

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
    "DomainVersionReference",
    "RunSnapshot",
    "RunStatus",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "TaskSnapshot",
    "TaskStatus",
]
