"""The narrow Source and Evidence public facade.

Only typed processing commands, immutable-read queries, association commands,
application protocols/errors, accepted catalogs, and immutable snapshots cross
the module boundary. Entities, transition helpers, repositories, UoW, ORM, and
runtime types remain private.
"""

from .application.association_commands import (
    RemoveSourceAssociation,
    ReplaceSourceAssociation,
)
from .application.association_errors import SourceAssociationError
from .application.association_protocols import SourceAssociationApplication
from .application.association_results import SourceAssociationReplacementSnapshot
from .application.commands import (
    MarkSourceProcessingFailed,
    MarkSourceReady,
    MarkSourceReadyWithRejections,
    StartSourceProcessing,
    SupersedeSourceVersion,
)
from .application.errors import SourceEvidenceError
from .application.primary_input_commands import SavePrimaryInput
from .application.primary_input_errors import PrimaryInputError, PrimaryInputNotFound
from .application.primary_input_protocols import PrimaryInputApplication
from .application.primary_input_queries import GetPrimaryInput
from .application.protocols import SourceEvidenceApplication
from .application.queries import GetSourceAssociation, GetSourceVersion
from .application.query_protocols import SourceEvidenceQueryApplication
from .domain.primary_input import (
    PRIMARY_INPUT_MAX_BYTES,
    validate_primary_content,
    validate_primary_file_name,
)
from .domain.snapshots import (
    PrimaryInputKind,
    PrimaryInputSnapshot,
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
    "GetPrimaryInput",
    "PrimaryInputApplication",
    "PRIMARY_INPUT_MAX_BYTES",
    "PrimaryInputError",
    "PrimaryInputKind",
    "PrimaryInputNotFound",
    "validate_primary_content",
    "validate_primary_file_name",
    "PrimaryInputSnapshot",
    "SavePrimaryInput",
    "MarkSourceProcessingFailed",
    "MarkSourceReady",
    "MarkSourceReadyWithRejections",
    "StartSourceProcessing",
    "SupersedeSourceVersion",
    "RemoveSourceAssociation",
    "ReplaceSourceAssociation",
    "SourceAssociationApplication",
    "SourceAssociationError",
    "SourceAssociationReplacementSnapshot",
    "GetSourceVersion",
    "GetSourceAssociation",
    "SourceEvidenceQueryApplication",
]
