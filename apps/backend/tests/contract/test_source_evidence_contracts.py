"""Public Source and Evidence catalog/snapshot contract tests."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from typing import get_type_hints

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
    "SourceAssociationMembershipState",
    "SourceAssociationSnapshot",
    "SourceProcessingStatus",
    "SourceVersionSnapshot",
}


def test_source_facade_exports_exactly_the_four_frozen_symbols() -> None:
    assert set(public.__all__) == _PUBLIC_NAMES
    assert not hasattr(public, "Source")
    assert not hasattr(public, "SourceVersion")
    assert not hasattr(public, "SourceVersionProcessing")
    assert not hasattr(public, "TaskSourceAssociation")
    assert not hasattr(public, "Session")
    assert not hasattr(public, "UnitOfWork")


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
