"""Unit coverage for Source association application contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from inspect import iscoroutinefunction, signature
from typing import Any, cast, get_protocol_members, get_type_hints

import pytest

from ai_ecommerce_agent.modules.source_evidence import public
from ai_ecommerce_agent.modules.source_evidence.application.mappers import (
    source_association_replacement_to_snapshot,
    task_source_association_to_snapshot,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceAssociationMembershipState,
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


_SOURCE_ID = SourceId("source-01")
_TASK_ID = TaskId("task-01")
_SOURCE_VERSION = SourceVersion(
    source_version_id=SourceVersionId("source-version-01"),
    source_id=_SOURCE_ID,
    version_number=VersionNumber(1),
)


def _association() -> TaskSourceAssociation:
    return TaskSourceAssociation.create(
        SourceAssociationId("association-01"),
        _TASK_ID,
        _SOURCE_VERSION,
    )


def test_association_commands_are_frozen_slotted_and_identity_preserving() -> None:
    expected_fields = {
        public.RemoveSourceAssociation: (
            "task_id",
            "source_association_id",
            "expected_revision",
        ),
        public.ReplaceSourceAssociation: (
            "task_id",
            "source_association_id",
            "replacement_association_id",
            "replacement_source_version_id",
            "expected_revision",
        ),
    }
    expected_types = {
        public.RemoveSourceAssociation: {
            "task_id": TaskId,
            "source_association_id": SourceAssociationId,
            "expected_revision": Revision,
        },
        public.ReplaceSourceAssociation: {
            "task_id": TaskId,
            "source_association_id": SourceAssociationId,
            "replacement_association_id": SourceAssociationId,
            "replacement_source_version_id": SourceVersionId,
            "expected_revision": Revision,
        },
    }

    task_id = TaskId("task-command")
    association_id = SourceAssociationId("association-command")
    replacement_id = SourceAssociationId("association-replacement")
    replacement_version_id = SourceVersionId("source-version-replacement")
    revision = Revision(3)
    values: dict[Any, tuple[Any, ...]] = {
        public.RemoveSourceAssociation: (task_id, association_id, revision),
        public.ReplaceSourceAssociation: (
            task_id,
            association_id,
            replacement_id,
            replacement_version_id,
            revision,
        ),
    }

    for command, names in expected_fields.items():
        assert is_dataclass(command)
        assert cast(Any, command).__dataclass_params__.frozen
        assert command.__slots__ == names
        assert tuple(field.name for field in fields(command)) == names
        assert get_type_hints(command) == expected_types[command]
        instance = cast(Any, command)(*values[command])
        assert instance.task_id is task_id
        assert instance.source_association_id is association_id
        assert instance.expected_revision is revision
        with pytest.raises(FrozenInstanceError):
            instance.task_id = TaskId("other-task")  # type: ignore[misc]

    replacement = cast(Any, public.ReplaceSourceAssociation)(
        *values[public.ReplaceSourceAssociation]
    )
    assert replacement.replacement_association_id is replacement_id
    assert replacement.replacement_source_version_id is replacement_version_id


def test_replacement_result_is_frozen_slotted_and_identity_preserving() -> None:
    replaced = public.SourceAssociationSnapshot(
        source_association_id=SourceAssociationId("association-old"),
        task_id=_TASK_ID,
        source_id=_SOURCE_ID,
        source_version_id=_SOURCE_VERSION.source_version_id,
        membership_state=SourceAssociationMembershipState.REPLACED,
        revision=Revision(1),
        replaced_by_association_id=SourceAssociationId("association-new"),
    )
    active = public.SourceAssociationSnapshot(
        source_association_id=SourceAssociationId("association-new"),
        task_id=_TASK_ID,
        source_id=_SOURCE_ID,
        source_version_id=SourceVersionId("source-version-02"),
        membership_state=SourceAssociationMembershipState.ACTIVE,
        revision=Revision.initial(),
        replaced_by_association_id=None,
    )

    result = public.SourceAssociationReplacementSnapshot(replaced, active)

    assert is_dataclass(result)
    assert cast(
        Any, public.SourceAssociationReplacementSnapshot
    ).__dataclass_params__.frozen
    assert public.SourceAssociationReplacementSnapshot.__slots__ == (
        "replaced_association",
        "active_association",
    )
    assert tuple(field.name for field in fields(result)) == (
        "replaced_association",
        "active_association",
    )
    assert get_type_hints(public.SourceAssociationReplacementSnapshot) == {
        "replaced_association": public.SourceAssociationSnapshot,
        "active_association": public.SourceAssociationSnapshot,
    }
    assert result.replaced_association is replaced
    assert result.active_association is active
    with pytest.raises(FrozenInstanceError):
        result.active_association = replaced  # type: ignore[misc]


def test_association_protocol_is_runtime_checkable_sync_and_exact() -> None:
    protocol = public.SourceAssociationApplication
    assert get_protocol_members(protocol) == {
        "remove_source_association",
        "replace_source_association",
    }
    expected = {
        "remove_source_association": (
            public.RemoveSourceAssociation,
            public.SourceAssociationSnapshot,
        ),
        "replace_source_association": (
            public.ReplaceSourceAssociation,
            public.SourceAssociationReplacementSnapshot,
        ),
    }
    for name, (command, result) in expected.items():
        method = getattr(protocol, name)
        assert not iscoroutinefunction(method)
        assert [
            parameter.name for parameter in signature(method).parameters.values()
        ] == [
            "self",
            "command",
        ]
        hints = get_type_hints(method)
        assert hints["command"] is command
        assert hints["return"] is result

    class SynchronousImplementation:
        def remove_source_association(
            self, command: public.RemoveSourceAssociation
        ) -> public.SourceAssociationSnapshot:
            raise NotImplementedError

        def replace_source_association(
            self, command: public.ReplaceSourceAssociation
        ) -> public.SourceAssociationReplacementSnapshot:
            raise NotImplementedError

    implementation = SynchronousImplementation()
    assert isinstance(implementation, protocol)
    assert not isinstance(object(), protocol)


def test_association_error_is_slotted_catchable_and_shallowly_typed() -> None:
    error = public.SourceAssociationError(
        error_code="revision_conflict",
        category="source_association",
        message="The association changed",
        retryability=False,
        relevant_reference=SourceAssociationId("association-01"),
        expected_revision=Revision(1),
        actual_revision=Revision(2),
        conflicting_state=SourceAssociationMembershipState.ACTIVE,
        recovery_hint="refresh_and_compare",
    )

    assert isinstance(error, Exception)
    assert str(error) == "The association changed"
    assert not cast(Any, public.SourceAssociationError).__dataclass_params__.frozen
    assert public.SourceAssociationError.__slots__ == (
        "error_code",
        "category",
        "message",
        "retryability",
        "relevant_reference",
        "expected_revision",
        "actual_revision",
        "conflicting_state",
        "recovery_hint",
    )
    assert get_type_hints(public.SourceAssociationError) == {
        "error_code": str,
        "category": str,
        "message": str,
        "retryability": bool,
        "relevant_reference": SourceAssociationId,
        "expected_revision": Revision | None,
        "actual_revision": Revision | None,
        "conflicting_state": SourceAssociationMembershipState | None,
        "recovery_hint": str | None,
    }

    for field_name in ("error_code", "category", "message"):
        values: dict[str, Any] = {
            "error_code": "error",
            "category": "source_association",
            "message": "safe message",
            "retryability": False,
            "relevant_reference": SourceAssociationId("association-01"),
        }
        values[field_name] = " \t\n "
        with pytest.raises(ValueError, match="non-empty"):
            public.SourceAssociationError(**values)


def test_association_mappers_preserve_domain_projection_identity_and_order() -> None:
    association = _association()
    snapshot = task_source_association_to_snapshot(association)

    assert snapshot.source_association_id is association.source_association_id
    assert snapshot.task_id is association.task_id
    assert snapshot.source_id is association.source_id
    assert snapshot.source_version_id is association.source_version_id
    assert snapshot.membership_state is association.membership_state
    assert snapshot.revision is association.revision
    assert snapshot.replaced_by_association_id is association.replaced_by_association_id

    replacement = association.replace(
        SourceAssociationId("association-02"),
        SourceVersion(
            source_version_id=SourceVersionId("source-version-02"),
            source_id=_SOURCE_ID,
            version_number=VersionNumber(2),
        ),
        expected_revision=association.revision,
    )
    result = source_association_replacement_to_snapshot(replacement)

    assert result.replaced_association.source_association_id is (
        replacement.replaced_association.source_association_id
    )
    assert result.active_association.source_association_id is (
        replacement.active_association.source_association_id
    )
    assert result.replaced_association.membership_state is (
        SourceAssociationMembershipState.REPLACED
    )
    assert result.active_association.membership_state is (
        SourceAssociationMembershipState.ACTIVE
    )
