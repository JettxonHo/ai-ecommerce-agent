"""The narrow Source and Evidence public facade.

Only typed processing commands, the application protocol/error, the accepted
catalogs and immutable snapshots cross the module boundary. Entities,
transition helpers, repositories, UoW, ORM, and runtime types remain private.
"""

from .application.commands import (
    MarkSourceProcessingFailed,
    MarkSourceReady,
    MarkSourceReadyWithRejections,
    StartSourceProcessing,
    SupersedeSourceVersion,
)
from .application.errors import SourceEvidenceError
from .application.protocols import SourceEvidenceApplication
from .domain.snapshots import (
    SourceAssociationMembershipState,
    SourceAssociationSnapshot,
    SourceProcessingStatus,
    SourceVersionSnapshot,
)

__all__ = [
    "SourceAssociationMembershipState",
    "SourceAssociationSnapshot",
    "SourceEvidenceApplication",
    "SourceEvidenceError",
    "SourceProcessingStatus",
    "SourceVersionSnapshot",
    "MarkSourceProcessingFailed",
    "MarkSourceReady",
    "MarkSourceReadyWithRejections",
    "StartSourceProcessing",
    "SupersedeSourceVersion",
]
