"""The narrow Source and Evidence public facade.

Only the two accepted catalogs and two immutable snapshots cross the module
boundary.  Entities, transition helpers, repositories, UoW, ORM, and runtime
types remain private to later implementation slices.
"""

from .domain.snapshots import (
    SourceAssociationMembershipState,
    SourceAssociationSnapshot,
    SourceProcessingStatus,
    SourceVersionSnapshot,
)

__all__ = [
    "SourceAssociationMembershipState",
    "SourceAssociationSnapshot",
    "SourceProcessingStatus",
    "SourceVersionSnapshot",
]
