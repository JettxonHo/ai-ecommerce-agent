"""Focused unit checks for immutable Source snapshot construction."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from ai_ecommerce_agent.modules.source_evidence.public import (
    SourceAssociationMembershipState,
    SourceAssociationSnapshot,
    SourceProcessingStatus,
    SourceVersionSnapshot,
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


def test_source_version_snapshot_keeps_safe_failure_summary_nullable() -> None:
    snapshot = SourceVersionSnapshot(
        source_id=SourceId("source-01"),
        source_version_id=SourceVersionId("source-version-01"),
        version_number=VersionNumber.initial(),
        processing_status=SourceProcessingStatus.REGISTERED,
        processing_revision=Revision.initial(),
        failure_summary=None,
        updated_at=datetime(2026, 8, 9, tzinfo=UTC),
    )

    assert snapshot.failure_summary is None
    assert snapshot.processing_status is SourceProcessingStatus.REGISTERED
    assert snapshot.processing_revision == Revision.initial()
    with pytest.raises(FrozenInstanceError):
        snapshot.processing_status = SourceProcessingStatus.PROCESSING  # type: ignore[misc]


def test_replaced_association_can_link_a_new_identity() -> None:
    snapshot = SourceAssociationSnapshot(
        source_association_id=SourceAssociationId("association-old"),
        task_id=TaskId("task-01"),
        source_id=SourceId("source-01"),
        source_version_id=SourceVersionId("source-version-01"),
        membership_state=SourceAssociationMembershipState.REPLACED,
        revision=Revision(2),
        replaced_by_association_id=SourceAssociationId("association-new"),
    )

    assert snapshot.membership_state is SourceAssociationMembershipState.REPLACED
    assert snapshot.replaced_by_association_id == SourceAssociationId("association-new")


def test_catalog_rejects_unknown_values() -> None:
    with pytest.raises(ValueError):
        SourceProcessingStatus("ready_with_rejection")
    with pytest.raises(ValueError):
        SourceAssociationMembershipState("restored")
