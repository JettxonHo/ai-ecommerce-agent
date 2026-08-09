"""Unit checks for the Source Evidence primitive row mappings."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta

import pytest

from ai_ecommerce_agent.modules.source_evidence.domain import (
    AssociationReplacementError,
    SourceAssociationMembershipState,
    SourceProcessingStatus,
    SourceVersion,
    SourceVersionProcessing,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.mappings import (
    source_version_domain_to_row,
    source_version_processing_domain_to_row,
    source_version_processing_row_to_domain,
    source_version_row_to_domain,
    task_source_association_domain_to_row,
    task_source_association_row_to_domain,
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

_T0 = datetime(2026, 8, 9, 0, 0, tzinfo=UTC)
_T1 = _T0 + timedelta(minutes=1)
_SOURCE_ID = SourceId("source-01")
_VERSION_ID = SourceVersionId("source-version-01")
_TASK_ID = TaskId("task-01")
_ASSOCIATION_ID = SourceAssociationId("association-01")


def test_source_version_row_mapping_preserves_primitive_columns_and_values() -> None:
    source_version = SourceVersion(
        source_version_id=_VERSION_ID,
        source_id=_SOURCE_ID,
        version_number=VersionNumber(7),
    )

    row = source_version_domain_to_row(source_version)

    assert row == {
        "source_version_id": "source-version-01",
        "source_id": "source-01",
        "version_number": 7,
    }
    assert source_version_row_to_domain(row) == source_version


def test_processing_row_mapping_preserves_failed_summary_and_timezone() -> None:
    processing = SourceVersionProcessing(
        source_version_id=_VERSION_ID,
        status=SourceProcessingStatus.FAILED,
        revision=Revision(4),
        failure_summary="parser unavailable",
        updated_at=_T1,
    )

    row = source_version_processing_domain_to_row(processing)

    assert row == {
        "source_version_id": "source-version-01",
        "status": "failed",
        "revision": 4,
        "failure_summary": "parser unavailable",
        "updated_at": _T1,
    }
    restored = source_version_processing_row_to_domain(row)
    assert restored == processing
    assert restored.updated_at.tzinfo is UTC


def test_processing_row_mapping_preserves_nullable_failure_summary() -> None:
    processing = SourceVersionProcessing.create(_VERSION_ID, updated_at=_T0)

    row = source_version_processing_domain_to_row(processing)

    assert row["failure_summary"] is None
    assert source_version_processing_row_to_domain(row) == processing


def test_association_row_mapping_preserves_replacement_link() -> None:
    source_version = SourceVersion(
        source_version_id=_VERSION_ID,
        source_id=_SOURCE_ID,
        version_number=VersionNumber.initial(),
    )
    association = TaskSourceAssociation.create(
        _ASSOCIATION_ID,
        _TASK_ID,
        source_version,
    )
    replaced = association.replace(
        SourceAssociationId("association-02"),
        SourceVersion(
            source_version_id=SourceVersionId("source-version-02"),
            source_id=_SOURCE_ID,
            version_number=VersionNumber(2),
        ),
        expected_revision=association.revision,
    ).replaced_association

    row = task_source_association_domain_to_row(replaced)

    assert row == {
        "source_association_id": "association-01",
        "task_id": "task-01",
        "source_id": "source-01",
        "source_version_id": "source-version-01",
        "membership_state": "replaced",
        "revision": 1,
        "replaced_by_association_id": "association-02",
    }
    restored = task_source_association_row_to_domain(row)
    assert restored == replaced
    assert restored.membership_state is SourceAssociationMembershipState.REPLACED


def test_association_row_mapping_preserves_nullable_replacement_link() -> None:
    source_version = SourceVersion(
        source_version_id=_VERSION_ID,
        source_id=_SOURCE_ID,
        version_number=VersionNumber.initial(),
    )
    association = TaskSourceAssociation.create(
        _ASSOCIATION_ID,
        _TASK_ID,
        source_version,
    )

    row = task_source_association_domain_to_row(association)

    assert row["replaced_by_association_id"] is None
    assert task_source_association_row_to_domain(row) == association


@pytest.mark.parametrize(
    ("mapping", "mapper", "error"),
    [
        (
            {
                "source_version_id": "source-version-01",
                "source_id": "source-01",
                "version_number": 0,
            },
            source_version_row_to_domain,
            ValueError,
        ),
        (
            {
                "source_version_id": "source-version-01",
                "status": "unknown",
                "revision": 0,
                "failure_summary": None,
                "updated_at": _T0,
            },
            source_version_processing_row_to_domain,
            ValueError,
        ),
        (
            {
                "source_version_id": "source-version-01",
                "status": "registered",
                "revision": -1,
                "failure_summary": None,
                "updated_at": _T0,
            },
            source_version_processing_row_to_domain,
            ValueError,
        ),
        (
            {
                "source_association_id": "association-01",
                "task_id": "task-01",
                "source_id": "source-01",
                "source_version_id": "source-version-01",
                "membership_state": "replaced",
                "revision": 0,
                "replaced_by_association_id": "association-01",
            },
            task_source_association_row_to_domain,
            AssociationReplacementError,
        ),
        (
            {
                "source_association_id": "association-01",
                "task_id": "task-01",
                "source_id": "source-01",
                "source_version_id": "source-version-01",
                "membership_state": "active",
                "revision": 0,
                "replaced_by_association_id": "association-02",
            },
            task_source_association_row_to_domain,
            ValueError,
        ),
    ],
)
def test_invalid_rows_are_rejected_by_value_objects_or_domain_invariants(
    mapping: dict[str, object],
    mapper: Callable[[Mapping[str, object]], object],
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        mapper(mapping)
