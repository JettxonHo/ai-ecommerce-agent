"""Framework-neutral shared value objects.

Only small, domain-neutral values belong here.  Business aggregates, ORM
models, HTTP DTOs and provider/runtime errors remain owned by their layers.
"""

from .errors import ProjectError, SafeContext
from .identity import (
    DomainVersionId,
    ExportSnapshotId,
    OpaqueIdentity,
    ReviewDecisionId,
    ReviewDraftId,
    ReviewId,
    ReviewPackageId,
    RunId,
    SourceAssociationId,
    SourceId,
    SourceVersionId,
    TaskId,
)
from .revision import Revision
from .version import VersionNumber

__all__ = [
    "DomainVersionId",
    "ExportSnapshotId",
    "OpaqueIdentity",
    "ProjectError",
    "ReviewDecisionId",
    "ReviewDraftId",
    "ReviewId",
    "ReviewPackageId",
    "Revision",
    "RunId",
    "SafeContext",
    "SourceAssociationId",
    "SourceId",
    "SourceVersionId",
    "TaskId",
    "VersionNumber",
]
