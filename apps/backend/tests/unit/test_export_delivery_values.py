"""Focused unit coverage for Export Delivery contract values."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime
from typing import Any, cast, get_type_hints

import pytest

from ai_ecommerce_agent.modules.export_delivery.public import (
    ConfirmExportRequest,
    ExportBasis,
    ExportBriefKind,
    ExportPreview,
    ExportSnapshot,
)
from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ExportSnapshotId,
    Revision,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def _basis() -> ExportBasis:
    return ExportBasis(
        task_id=TaskId("task-1"),
        task_revision=Revision(4),
        brief_kind=ExportBriefKind.MARKETING,
        brief_version=DomainVersionReference(
            DomainVersionId("brief-1"), VersionNumber(2)
        ),
        upstream_versions=(
            DomainVersionReference(DomainVersionId("strategy-1"), VersionNumber(1)),
        ),
        hypotheses=("validate durability claim",),
        evidence_limitations=("limited customer feedback",),
        risks=("overclaiming weather resistance",),
    )


def test_export_kind_catalog_is_exact_and_alias_free() -> None:
    assert list(ExportBriefKind.__members__) == ["MARKETING", "XIAOHONGSHU"]
    assert [member.value for member in ExportBriefKind] == [
        "marketing",
        "xiaohongshu",
    ]


def test_export_dtos_are_frozen_slotted_and_exactly_typed() -> None:
    expected_fields = {
        ExportBasis: (
            "task_id",
            "task_revision",
            "brief_kind",
            "brief_version",
            "upstream_versions",
            "hypotheses",
            "evidence_limitations",
            "risks",
        ),
        ExportPreview: ("basis", "template_version", "file_name", "media_type"),
        ConfirmExportRequest: ("basis",),
        ExportSnapshot: (
            "export_snapshot_id",
            "task_id",
            "brief_kind",
            "brief_version",
            "upstream_versions",
            "exported_at",
            "file_name",
            "media_type",
            "content_location",
            "template_version",
        ),
    }
    expected_types = {
        ExportBasis: {
            "task_id": TaskId,
            "task_revision": Revision,
            "brief_kind": ExportBriefKind,
            "brief_version": DomainVersionReference,
            "upstream_versions": tuple[DomainVersionReference, ...],
            "hypotheses": tuple[str, ...],
            "evidence_limitations": tuple[str, ...],
            "risks": tuple[str, ...],
        },
        ExportPreview: {
            "basis": ExportBasis,
            "template_version": str,
            "file_name": str,
            "media_type": str,
        },
        ConfirmExportRequest: {"basis": ExportBasis},
        ExportSnapshot: {
            "export_snapshot_id": ExportSnapshotId,
            "task_id": TaskId,
            "brief_kind": ExportBriefKind,
            "brief_version": DomainVersionReference,
            "upstream_versions": tuple[DomainVersionReference, ...],
            "exported_at": datetime,
            "file_name": str,
            "media_type": str,
            "content_location": str,
            "template_version": str,
        },
    }

    for value_type, names in expected_fields.items():
        assert is_dataclass(value_type)
        assert cast(Any, value_type).__dataclass_params__.frozen
        assert tuple(field.name for field in fields(value_type)) == names
        assert value_type.__slots__ == names
        assert get_type_hints(value_type) == expected_types[value_type]


def test_export_dtos_preserve_supplied_basis_and_metadata() -> None:
    basis = _basis()
    preview = ExportPreview(
        basis=basis,
        template_version="mvp0-markdown-v1",
        file_name="chosen-name.md",
        media_type="text/markdown; charset=utf-8",
    )
    request = ConfirmExportRequest(basis=basis)
    exported_at = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
    snapshot = ExportSnapshot(
        export_snapshot_id=ExportSnapshotId("export-1"),
        task_id=basis.task_id,
        brief_kind=basis.brief_kind,
        brief_version=basis.brief_version,
        upstream_versions=basis.upstream_versions,
        exported_at=exported_at,
        file_name=preview.file_name,
        media_type=preview.media_type,
        content_location="chosen-location",
        template_version=preview.template_version,
    )

    assert preview.basis is basis
    assert request.basis is basis
    assert snapshot.brief_version is basis.brief_version
    assert snapshot.upstream_versions is basis.upstream_versions
    assert snapshot.exported_at is exported_at
    assert snapshot.file_name == "chosen-name.md"
    assert snapshot.content_location == "chosen-location"

    with pytest.raises(FrozenInstanceError):
        preview.media_type = "text/plain"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("factory", "field_name"),
    [
        (
            lambda: ExportPreview(_basis(), "", "name.md", "text/markdown"),
            "template_version",
        ),
        (lambda: ExportPreview(_basis(), "v1", "", "text/markdown"), "file_name"),
        (lambda: ExportPreview(_basis(), "v1", "name.md", ""), "media_type"),
        (
            lambda: ExportSnapshot(
                ExportSnapshotId("export-1"),
                TaskId("task-1"),
                ExportBriefKind.MARKETING,
                _basis().brief_version,
                (),
                datetime(2026, 8, 9, tzinfo=UTC),
                "",
                "text/markdown",
                "location",
                "v1",
            ),
            "file_name",
        ),
    ],
)
def test_export_metadata_guards_reject_empty_strings(
    factory: Any, field_name: str
) -> None:
    with pytest.raises(ValueError, match=field_name):
        factory()
