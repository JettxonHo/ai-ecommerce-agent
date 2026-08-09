"""Unit coverage for Source processing application contracts."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone, tzinfo

import pytest

from ai_ecommerce_agent.modules.source_evidence import public
from ai_ecommerce_agent.modules.source_evidence.application.mappers import (
    source_version_to_snapshot,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceVersion,
    SourceVersionProcessing,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceId,
    SourceVersionId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def test_commands_preserve_caller_timestamp_and_failure_text() -> None:
    timestamp = datetime(2026, 8, 9, 10, 30, tzinfo=timezone(timedelta(hours=8)))
    source_version_id = SourceVersionId("sv-1")
    command = public.MarkSourceProcessingFailed(
        source_version_id,
        Revision(3),
        timestamp,
        "  parser rejected one row  ",
    )
    assert command.source_version_id == source_version_id
    assert command.expected_revision == Revision(3)
    assert command.updated_at is timestamp
    assert command.failure_summary == "  parser rejected one row  "


def test_commands_reject_tzinfo_without_offset() -> None:
    # A real tzinfo implementation can carry a tzinfo object while still
    # returning no offset; the command must reject that ambiguous timestamp.
    class NullOffset(tzinfo):
        def utcoffset(self, _value: datetime | None) -> None:
            return None

        def dst(self, _value: datetime | None) -> None:
            return None

        def tzname(self, _value: datetime | None) -> str:
            return "null"

    timestamp = datetime(2026, 8, 9, tzinfo=NullOffset())
    with pytest.raises(ValueError, match="timezone-aware"):
        public.StartSourceProcessing(SourceVersionId("sv-1"), Revision(0), timestamp)


def test_mapper_projects_exact_identity_and_processing_fields() -> None:
    source_version_id = SourceVersionId("sv-1")
    updated_at = datetime(2026, 8, 9, tzinfo=UTC)
    source_version = SourceVersion(
        source_version_id=source_version_id,
        source_id=SourceId("source-1"),
        version_number=VersionNumber(2),
    )
    processing = SourceVersionProcessing(
        source_version_id=source_version_id,
        status=public.SourceProcessingStatus.FAILED,
        revision=Revision(4),
        failure_summary="parser unavailable",
        updated_at=updated_at,
    )
    snapshot = source_version_to_snapshot(source_version, processing)
    assert snapshot.source_id == SourceId("source-1")
    assert snapshot.source_version_id == source_version_id
    assert snapshot.version_number == VersionNumber(2)
    assert snapshot.processing_status is public.SourceProcessingStatus.FAILED
    assert snapshot.processing_revision == Revision(4)
    assert snapshot.failure_summary == "parser unavailable"
    assert snapshot.updated_at is updated_at


def test_mapper_rejects_mismatched_source_version_identity() -> None:
    updated_at = datetime(2026, 8, 9, tzinfo=UTC)
    source_version = SourceVersion(
        source_version_id=SourceVersionId("sv-1"),
        source_id=SourceId("source-1"),
        version_number=VersionNumber.initial(),
    )
    processing = SourceVersionProcessing(
        source_version_id=SourceVersionId("sv-2"),
        status=public.SourceProcessingStatus.REGISTERED,
        revision=Revision.initial(),
        failure_summary=None,
        updated_at=updated_at,
    )
    with pytest.raises(ValueError, match="identities must match"):
        source_version_to_snapshot(source_version, processing)
