"""Revisioned Task-to-Source membership domain value."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Self

from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceId,
    SourceVersionId,
    TaskId,
)

from .errors import (
    AssociationReplacementError,
    InvalidTransitionError,
    OwnershipError,
    RevisionConflictError,
)
from .snapshots import SourceAssociationMembershipState
from .source_version import SourceVersion


def _require_revision(current: Revision, expected: Revision) -> None:
    if current != expected:
        raise RevisionConflictError(
            resource="task_source_association",
            expected=expected,
            current=current,
        )


def _invalid(
    association: TaskSourceAssociation, *, intent: str
) -> InvalidTransitionError:
    return InvalidTransitionError(
        resource="task_source_association",
        status=association.membership_state.value,
        intent=intent,
    )


@dataclass(frozen=True, slots=True)
class SourceAssociationReplacement:
    """The old replaced association and its newly-created active successor."""

    replaced_association: TaskSourceAssociation
    active_association: TaskSourceAssociation


@dataclass(frozen=True, slots=True)
class TaskSourceAssociation:
    """A revisioned Task membership binding to one exact Source Version."""

    source_association_id: SourceAssociationId
    task_id: TaskId
    source_id: SourceId
    source_version_id: SourceVersionId
    membership_state: SourceAssociationMembershipState
    revision: Revision
    replaced_by_association_id: SourceAssociationId | None

    def __post_init__(self) -> None:
        if self.membership_state is SourceAssociationMembershipState.REPLACED:
            if self.replaced_by_association_id is None:
                raise ValueError("replaced association requires replacement link")
        elif self.replaced_by_association_id is not None:
            raise ValueError("only replaced association may have a replacement link")

    @classmethod
    def create(
        cls,
        source_association_id: SourceAssociationId,
        task_id: TaskId,
        source_version: SourceVersion,
    ) -> Self:
        """Create an active association for the exact supplied version."""

        return cls(
            source_association_id=source_association_id,
            task_id=task_id,
            source_id=source_version.source_id,
            source_version_id=source_version.source_version_id,
            membership_state=SourceAssociationMembershipState.ACTIVE,
            revision=Revision.initial(),
            replaced_by_association_id=None,
        )

    def remove(self, *, expected_revision: Revision) -> Self:
        """Remove active membership while preserving its identity and version."""

        _require_revision(self.revision, expected_revision)
        if self.membership_state is not SourceAssociationMembershipState.ACTIVE:
            raise _invalid(self, intent="remove")
        return replace(
            self,
            membership_state=SourceAssociationMembershipState.REMOVED,
            revision=self.revision.next(),
            replaced_by_association_id=None,
        )

    def replace(
        self,
        replacement_association_id: SourceAssociationId,
        replacement_source_version: SourceVersion,
        *,
        expected_revision: Revision,
    ) -> SourceAssociationReplacement:
        """Replace active membership with a distinct association identity."""

        _require_revision(self.revision, expected_revision)
        if self.membership_state is not SourceAssociationMembershipState.ACTIVE:
            raise _invalid(self, intent="replace")
        if replacement_association_id == self.source_association_id:
            raise AssociationReplacementError(reason="association_identity_must_differ")
        if replacement_source_version.source_id != self.source_id:
            raise OwnershipError(resource="task_source_association")
        if replacement_source_version.source_version_id == self.source_version_id:
            raise AssociationReplacementError(
                reason="source_version_identity_must_differ"
            )

        old_association = replace(
            self,
            membership_state=SourceAssociationMembershipState.REPLACED,
            revision=self.revision.next(),
            replaced_by_association_id=replacement_association_id,
        )
        new_association = type(self).create(
            replacement_association_id,
            self.task_id,
            replacement_source_version,
        )
        return SourceAssociationReplacement(old_association, new_association)


__all__ = ["SourceAssociationReplacement", "TaskSourceAssociation"]
