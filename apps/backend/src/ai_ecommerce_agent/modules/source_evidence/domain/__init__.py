"""Framework-neutral Source and Evidence domain contracts."""

from .association import SourceAssociationReplacement, TaskSourceAssociation
from .errors import (
    AssociationReplacementError,
    InvalidTransitionError,
    OwnershipError,
    RevisionConflictError,
)
from .primary_input import (
    PRIMARY_INPUT_MAX_BYTES,
    PrimaryInputKind,
    TaskPrimaryInput,
    normalize_primary_content,
    validate_primary_content,
    validate_primary_file_name,
)
from .processing import SourceVersionProcessing
from .snapshots import (
    PrimaryInputSnapshot,
    SourceAssociationMembershipState,
    SourceAssociationSnapshot,
    SourceProcessingStatus,
    SourceVersionSnapshot,
)
from .source_version import SourceVersion

__all__ = [
    "AssociationReplacementError",
    "SourceAssociationMembershipState",
    "SourceAssociationReplacement",
    "SourceAssociationSnapshot",
    "InvalidTransitionError",
    "OwnershipError",
    "RevisionConflictError",
    "SourceProcessingStatus",
    "SourceVersion",
    "SourceVersionProcessing",
    "SourceVersionSnapshot",
    "PRIMARY_INPUT_MAX_BYTES",
    "PrimaryInputKind",
    "PrimaryInputSnapshot",
    "TaskPrimaryInput",
    "normalize_primary_content",
    "validate_primary_content",
    "validate_primary_file_name",
    "TaskSourceAssociation",
]
