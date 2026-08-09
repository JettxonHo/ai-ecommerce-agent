"""Public Source and Evidence catalog/snapshot contract tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime
from inspect import signature
from typing import Any, get_protocol_members, get_type_hints

import pytest

from ai_ecommerce_agent.modules.source_evidence import public
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceId,
    SourceVersionId,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.contract

_PUBLIC_NAMES = {
    "MarkSourceProcessingFailed",
    "MarkSourceReady",
    "MarkSourceReadyWithRejections",
    "SourceAssociationMembershipState",
    "SourceAssociationSnapshot",
    "SourceEvidenceApplication",
    "SourceEvidenceError",
    "SourceProcessingStatus",
    "SourceVersionSnapshot",
    "StartSourceProcessing",
    "SupersedeSourceVersion",
}


def test_source_facade_exports_exactly_the_frozen_symbols() -> None:
    assert set(public.__all__) == _PUBLIC_NAMES
    assert not hasattr(public, "Source")
    assert not hasattr(public, "SourceVersion")
    assert not hasattr(public, "SourceVersionProcessing")
    assert not hasattr(public, "TaskSourceAssociation")
    assert not hasattr(public, "Session")
    assert not hasattr(public, "UnitOfWork")


def test_source_processing_commands_are_frozen_slotted_and_exact() -> None:
    command_fields = {
        "StartSourceProcessing": (
            "source_version_id",
            "expected_revision",
            "updated_at",
        ),
        "MarkSourceReady": ("source_version_id", "expected_revision", "updated_at"),
        "MarkSourceReadyWithRejections": (
            "source_version_id",
            "expected_revision",
            "updated_at",
        ),
        "MarkSourceProcessingFailed": (
            "source_version_id",
            "expected_revision",
            "updated_at",
            "failure_summary",
        ),
        "SupersedeSourceVersion": (
            "source_version_id",
            "expected_revision",
            "updated_at",
        ),
    }
    for name, expected_fields in command_fields.items():
        command: Any = getattr(public, name)
        assert bool(is_dataclass(command))
        assert tuple(field.name for field in fields(command)) == expected_fields
        assert hasattr(command, "__slots__")
        hints = get_type_hints(command)
        assert hints["source_version_id"] is SourceVersionId
        assert hints["expected_revision"] is Revision
        assert hints["updated_at"] is datetime
        instance: Any = command(
            SourceVersionId("sv-1"),
            Revision.initial(),
            datetime(2026, 8, 9, tzinfo=UTC),
            *(["failed"] if name == "MarkSourceProcessingFailed" else []),
        )
        with pytest.raises(FrozenInstanceError):
            instance.source_version_id = SourceVersionId("sv-2")
    assert get_type_hints(public.MarkSourceProcessingFailed)["failure_summary"] is str


def test_source_processing_commands_reject_naive_timestamps_and_blank_failures() -> (
    None
):
    for command in (
        public.StartSourceProcessing,
        public.MarkSourceReady,
        public.MarkSourceReadyWithRejections,
        public.SupersedeSourceVersion,
    ):
        with pytest.raises(ValueError, match="timezone-aware"):
            command(
                source_version_id=SourceVersionId("sv-1"),
                expected_revision=Revision.initial(),
                updated_at=datetime(2026, 8, 9),
            )
    with pytest.raises(ValueError, match="non-empty"):
        public.MarkSourceProcessingFailed(
            source_version_id=SourceVersionId("sv-1"),
            expected_revision=Revision.initial(),
            updated_at=datetime(2026, 8, 9, tzinfo=UTC),
            failure_summary=" \t\n ",
        )


def test_source_processing_protocol_has_exact_sync_methods_and_annotations() -> None:
    protocol = public.SourceEvidenceApplication
    assert get_protocol_members(protocol) == {
        "start_source_processing",
        "mark_source_ready",
        "mark_source_ready_with_rejections",
        "mark_source_processing_failed",
        "supersede_source_version",
    }
    expected = {
        "start_source_processing": public.StartSourceProcessing,
        "mark_source_ready": public.MarkSourceReady,
        "mark_source_ready_with_rejections": public.MarkSourceReadyWithRejections,
        "mark_source_processing_failed": public.MarkSourceProcessingFailed,
        "supersede_source_version": public.SupersedeSourceVersion,
    }
    for name, command in expected.items():
        method = getattr(protocol, name)
        parameters = list(signature(method).parameters.values())
        assert [parameter.name for parameter in parameters] == ["self", "command"]
        assert get_type_hints(method)["command"] is command
        assert get_type_hints(method)["return"] is public.SourceVersionSnapshot


def test_source_evidence_error_is_shallow_typed_and_catchable() -> None:
    error = public.SourceEvidenceError(
        error_code="revision_conflict",
        category="source_evidence",
        message="The Source Version changed",
        retryability=False,
        relevant_reference=SourceVersionId("sv-1"),
        expected_revision=Revision(1),
        actual_revision=Revision(2),
        conflicting_state=public.SourceProcessingStatus.PROCESSING,
        recovery_hint="refresh_and_compare",
    )
    assert isinstance(error, Exception)
    assert str(error) == "The Source Version changed"
    assert {field.name for field in fields(public.SourceEvidenceError)} == {
        "error_code",
        "category",
        "message",
        "retryability",
        "relevant_reference",
        "expected_revision",
        "actual_revision",
        "conflicting_state",
        "recovery_hint",
    }
    hints = get_type_hints(public.SourceEvidenceError)
    assert hints["relevant_reference"] is SourceVersionId
    assert hints["expected_revision"] == Revision | None
    assert hints["actual_revision"] == Revision | None
    assert hints["conflicting_state"] == public.SourceProcessingStatus | None
    assert hints["recovery_hint"] == str | None


def test_processing_catalog_has_exactly_six_values_without_aliases() -> None:
    assert public.SourceProcessingStatus.__members__ == {
        "REGISTERED": public.SourceProcessingStatus.REGISTERED,
        "PROCESSING": public.SourceProcessingStatus.PROCESSING,
        "READY": public.SourceProcessingStatus.READY,
        "READY_WITH_REJECTIONS": public.SourceProcessingStatus.READY_WITH_REJECTIONS,
        "FAILED": public.SourceProcessingStatus.FAILED,
        "SUPERSEDED": public.SourceProcessingStatus.SUPERSEDED,
    }
    assert [member.value for member in public.SourceProcessingStatus] == [
        "registered",
        "processing",
        "ready",
        "ready_with_rejections",
        "failed",
        "superseded",
    ]


def test_association_catalog_has_exactly_three_values_without_aliases() -> None:
    assert public.SourceAssociationMembershipState.__members__ == {
        "ACTIVE": public.SourceAssociationMembershipState.ACTIVE,
        "REMOVED": public.SourceAssociationMembershipState.REMOVED,
        "REPLACED": public.SourceAssociationMembershipState.REPLACED,
    }
    assert [member.value for member in public.SourceAssociationMembershipState] == [
        "active",
        "removed",
        "replaced",
    ]


def test_source_version_snapshot_fields_are_separate_from_association_membership() -> (
    None
):
    assert {field.name for field in fields(public.SourceVersionSnapshot)} == {
        "source_id",
        "source_version_id",
        "version_number",
        "processing_status",
        "processing_revision",
        "failure_summary",
        "updated_at",
    }
    assert "membership_state" not in public.SourceVersionSnapshot.__dataclass_fields__
    assert (
        "replaced_by_association_id"
        not in public.SourceVersionSnapshot.__dataclass_fields__
    )
    hints = get_type_hints(public.SourceVersionSnapshot)
    assert hints["source_id"] is SourceId
    assert hints["source_version_id"] is SourceVersionId
    assert hints["version_number"] is VersionNumber
    assert hints["processing_revision"] is Revision
    assert hints["updated_at"] is datetime
    assert hints["failure_summary"] == str | None


def test_source_association_snapshot_fields_are_separate_from_processing() -> None:
    assert {field.name for field in fields(public.SourceAssociationSnapshot)} == {
        "source_association_id",
        "task_id",
        "source_id",
        "source_version_id",
        "membership_state",
        "revision",
        "replaced_by_association_id",
    }
    assert (
        "processing_status" not in public.SourceAssociationSnapshot.__dataclass_fields__
    )
    assert (
        "failure_summary" not in public.SourceAssociationSnapshot.__dataclass_fields__
    )
    hints = get_type_hints(public.SourceAssociationSnapshot)
    assert hints["source_association_id"] is SourceAssociationId
    assert hints["task_id"] is TaskId
    assert hints["source_id"] is SourceId
    assert hints["source_version_id"] is SourceVersionId
    assert hints["revision"] is Revision
    assert hints["replaced_by_association_id"] == SourceAssociationId | None


def test_public_snapshots_are_framework_neutral_frozen_dataclasses() -> None:
    for snapshot in (
        public.SourceVersionSnapshot,
        public.SourceAssociationSnapshot,
    ):
        assert is_dataclass(snapshot)
        assert snapshot.__slots__
        assert not hasattr(snapshot, "from_domain")
        assert not hasattr(snapshot, "to_orm")
