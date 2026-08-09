"""Representative TaskSourceAssociation invariants for #111."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields

import pytest

from ai_ecommerce_agent.modules.source_evidence.domain import (
    AssociationReplacementError,
    InvalidTransitionError,
    OwnershipError,
    RevisionConflictError,
    SourceAssociationMembershipState,
    SourceAssociationReplacement,
    SourceVersion,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceId,
    SourceVersionId,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit

_TASK_ID = TaskId("task-01")
_SOURCE_ID = SourceId("source-01")
_OTHER_SOURCE_ID = SourceId("source-02")
_VERSION_ID = SourceVersionId("source-version-01")
_REPLACEMENT_VERSION_ID = SourceVersionId("source-version-02")
_ASSOCIATION_ID = SourceAssociationId("association-01")
_REPLACEMENT_ASSOCIATION_ID = SourceAssociationId("association-02")


def _version(
    version_id: SourceVersionId = _VERSION_ID,
    source_id: SourceId = _SOURCE_ID,
) -> SourceVersion:
    return SourceVersion.create(version_id, source_id, VersionNumber.initial())


def _association() -> TaskSourceAssociation:
    return TaskSourceAssociation.create(_ASSOCIATION_ID, _TASK_ID, _version())


def test_create_builds_exact_active_association_shape() -> None:
    association = _association()

    assert [field.name for field in fields(association)] == [
        "source_association_id",
        "task_id",
        "source_id",
        "source_version_id",
        "membership_state",
        "revision",
        "replaced_by_association_id",
    ]
    assert association.membership_state is SourceAssociationMembershipState.ACTIVE
    assert association.revision == Revision.initial()
    assert association.replaced_by_association_id is None
    with pytest.raises(FrozenInstanceError):
        association.task_id = TaskId("task-02")  # type: ignore[misc]


def test_remove_uses_revision_cas_and_preserves_identity_and_version() -> None:
    association = _association()

    removed = association.remove(expected_revision=association.revision)

    assert removed.membership_state is SourceAssociationMembershipState.REMOVED
    assert removed.revision == Revision(1)
    assert removed.source_association_id == association.source_association_id
    assert removed.source_version_id == association.source_version_id
    assert removed.replaced_by_association_id is None
    with pytest.raises(RevisionConflictError):
        association.remove(expected_revision=Revision(4))
    with pytest.raises(InvalidTransitionError):
        removed.remove(expected_revision=removed.revision)


def test_replace_returns_replaced_old_value_and_new_active_value() -> None:
    association = _association()
    replacement_version = _version(_REPLACEMENT_VERSION_ID)

    result = association.replace(
        _REPLACEMENT_ASSOCIATION_ID,
        replacement_version,
        expected_revision=association.revision,
    )

    assert isinstance(result, SourceAssociationReplacement)
    assert [field.name for field in fields(result)] == [
        "replaced_association",
        "active_association",
    ]
    old = result.replaced_association
    new = result.active_association
    assert old.membership_state is SourceAssociationMembershipState.REPLACED
    assert old.revision == Revision(1)
    assert old.replaced_by_association_id == _REPLACEMENT_ASSOCIATION_ID
    assert old.source_association_id == association.source_association_id
    assert old.source_version_id == association.source_version_id
    assert new.membership_state is SourceAssociationMembershipState.ACTIVE
    assert new.revision == Revision.initial()
    assert new.replaced_by_association_id is None
    assert new.source_association_id == _REPLACEMENT_ASSOCIATION_ID
    assert new.task_id == association.task_id
    assert new.source_id == association.source_id
    assert new.source_version_id == replacement_version.source_version_id


def test_replace_requires_active_cas_distinct_identity_and_same_source_version() -> (
    None
):
    association = _association()

    with pytest.raises(RevisionConflictError):
        association.replace(
            _REPLACEMENT_ASSOCIATION_ID,
            _version(_REPLACEMENT_VERSION_ID),
            expected_revision=Revision(2),
        )
    with pytest.raises(AssociationReplacementError):
        association.replace(
            _ASSOCIATION_ID,
            _version(_REPLACEMENT_VERSION_ID),
            expected_revision=association.revision,
        )
    with pytest.raises(AssociationReplacementError):
        association.replace(
            _REPLACEMENT_ASSOCIATION_ID,
            _version(),
            expected_revision=association.revision,
        )

    replaced = association.replace(
        _REPLACEMENT_ASSOCIATION_ID,
        _version(_REPLACEMENT_VERSION_ID),
        expected_revision=association.revision,
    ).replaced_association
    with pytest.raises(InvalidTransitionError):
        replaced.replace(
            SourceAssociationId("association-03"),
            _version(SourceVersionId("source-version-03")),
            expected_revision=replaced.revision,
        )


def test_replace_rejects_foreign_source_without_version_number_ordering_rule() -> None:
    association = _association()

    with pytest.raises(OwnershipError):
        association.replace(
            _REPLACEMENT_ASSOCIATION_ID,
            _version(_REPLACEMENT_VERSION_ID, _OTHER_SOURCE_ID),
            expected_revision=association.revision,
        )

    same_number = SourceVersion.create(
        _REPLACEMENT_VERSION_ID,
        _SOURCE_ID,
        VersionNumber.initial(),
    )
    result = association.replace(
        _REPLACEMENT_ASSOCIATION_ID,
        same_number,
        expected_revision=association.revision,
    )
    assert result.active_association.source_version_id == _REPLACEMENT_VERSION_ID


def test_reconstitution_enforces_only_replacement_link_invariant() -> None:
    with pytest.raises(ValueError):
        TaskSourceAssociation(
            source_association_id=_ASSOCIATION_ID,
            task_id=_TASK_ID,
            source_id=_SOURCE_ID,
            source_version_id=_VERSION_ID,
            membership_state=SourceAssociationMembershipState.REPLACED,
            revision=Revision.initial(),
            replaced_by_association_id=None,
        )

    with pytest.raises(ValueError):
        TaskSourceAssociation(
            source_association_id=_ASSOCIATION_ID,
            task_id=_TASK_ID,
            source_id=_SOURCE_ID,
            source_version_id=_VERSION_ID,
            membership_state=SourceAssociationMembershipState.ACTIVE,
            revision=Revision.initial(),
            replaced_by_association_id=_REPLACEMENT_ASSOCIATION_ID,
        )

    reconstituted = TaskSourceAssociation(
        source_association_id=_ASSOCIATION_ID,
        task_id=_TASK_ID,
        source_id=_SOURCE_ID,
        source_version_id=_VERSION_ID,
        membership_state=SourceAssociationMembershipState.REPLACED,
        revision=Revision(4),
        replaced_by_association_id=_ASSOCIATION_ID,
    )
    assert reconstituted.replaced_by_association_id == _ASSOCIATION_ID
