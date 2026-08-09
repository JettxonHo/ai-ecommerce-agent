"""Representative Source Version identity and processing invariants for #110."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from datetime import UTC, datetime, timedelta

import pytest

from ai_ecommerce_agent.modules.source_evidence.domain import (
    InvalidTransitionError,
    RevisionConflictError,
    SourceVersion,
    SourceVersionProcessing,
)
from ai_ecommerce_agent.modules.source_evidence.public import SourceProcessingStatus
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceId,
    SourceVersionId,
    VersionNumber,
)

pytestmark = pytest.mark.unit

_T0 = datetime(2026, 8, 9, 0, 0, tzinfo=UTC)
_T1 = _T0 + timedelta(minutes=1)
_T2 = _T0 + timedelta(minutes=2)
_T3 = _T0 + timedelta(minutes=3)
_SOURCE_ID = SourceId("source-01")
_VERSION_ID = SourceVersionId("source-version-01")


def _registered() -> SourceVersionProcessing:
    return SourceVersionProcessing.create(_VERSION_ID, updated_at=_T0)


def _processing() -> SourceVersionProcessing:
    registered = _registered()
    return registered.start_processing(
        expected_revision=registered.revision,
        updated_at=_T1,
    )


def test_source_version_is_immutable_and_contains_only_identity_relationship() -> None:
    source_version = SourceVersion.create(
        _VERSION_ID,
        _SOURCE_ID,
        VersionNumber.initial(),
    )

    assert [field.name for field in fields(source_version)] == [
        "source_version_id",
        "source_id",
        "version_number",
    ]
    assert source_version.source_version_id == _VERSION_ID
    assert source_version.source_id == _SOURCE_ID
    assert source_version.version_number == VersionNumber.initial()
    with pytest.raises(FrozenInstanceError):
        source_version.source_id = SourceId("source-02")  # type: ignore[misc]


def test_registered_start_and_completion_paths_increment_revision() -> None:
    registered = _registered()
    processing = registered.start_processing(
        expected_revision=registered.revision,
        updated_at=_T1,
    )
    ready = processing.mark_ready(
        expected_revision=processing.revision,
        updated_at=_T2,
    )

    assert registered.status is SourceProcessingStatus.REGISTERED
    assert registered.revision == Revision.initial()
    assert processing.status is SourceProcessingStatus.PROCESSING
    assert processing.revision == Revision(1)
    assert ready.status is SourceProcessingStatus.READY
    assert ready.revision == Revision(2)
    assert ready.failure_summary is None
    assert ready.updated_at == _T2

    with pytest.raises(FrozenInstanceError):
        ready.status = SourceProcessingStatus.SUPERSEDED  # type: ignore[misc]


def test_registered_can_complete_with_rejections_or_fail() -> None:
    with_rejections = _registered().mark_ready_with_rejections(
        expected_revision=Revision.initial(),
        updated_at=_T1,
    )
    failed = _registered().mark_failed(
        "unsupported text encoding",
        expected_revision=Revision.initial(),
        updated_at=_T1,
    )

    assert with_rejections.status is SourceProcessingStatus.READY_WITH_REJECTIONS
    assert with_rejections.revision == Revision(1)
    assert failed.status is SourceProcessingStatus.FAILED
    assert failed.failure_summary == "unsupported text encoding"
    assert failed.revision == Revision(1)


def test_registered_can_be_marked_ready_directly() -> None:
    registered = _registered()

    ready = registered.mark_ready(
        expected_revision=Revision.initial(),
        updated_at=_T1,
    )

    assert ready.status is SourceProcessingStatus.READY
    assert ready.revision == Revision(1)
    assert ready.updated_at == _T1
    assert ready.failure_summary is None


def test_failed_retry_clears_summary_then_can_become_ready() -> None:
    failed = _processing().mark_failed(
        "parser unavailable",
        expected_revision=Revision(1),
        updated_at=_T2,
    )
    processing = failed.start_processing(
        expected_revision=failed.revision,
        updated_at=_T3,
    )
    ready_with_rejections = processing.mark_ready_with_rejections(
        expected_revision=processing.revision,
        updated_at=_T3,
    )

    assert failed.failure_summary == "parser unavailable"
    assert processing.status is SourceProcessingStatus.PROCESSING
    assert processing.failure_summary is None
    assert processing.revision == Revision(3)
    assert ready_with_rejections.status is SourceProcessingStatus.READY_WITH_REJECTIONS
    assert ready_with_rejections.failure_summary is None


def test_supersede_is_allowed_from_representative_nonterminal_states() -> None:
    states = (
        _registered(),
        _processing(),
        _processing().mark_ready(
            expected_revision=Revision(1),
            updated_at=_T2,
        ),
        _processing().mark_ready_with_rejections(
            expected_revision=Revision(1),
            updated_at=_T2,
        ),
        _processing().mark_failed(
            "parser unavailable",
            expected_revision=Revision(1),
            updated_at=_T2,
        ),
    )

    for processing in states:
        superseded = processing.supersede(
            expected_revision=processing.revision,
            updated_at=_T3,
        )
        assert superseded.status is SourceProcessingStatus.SUPERSEDED
        assert superseded.revision == processing.revision.next()
        assert superseded.failure_summary is None


def test_superseded_is_terminal_and_ready_cannot_arbitrarily_roll_back() -> None:
    processing = _processing()
    with pytest.raises(InvalidTransitionError):
        processing.start_processing(
            expected_revision=processing.revision,
            updated_at=_T3,
        )

    ready = _processing().mark_ready(
        expected_revision=Revision(1),
        updated_at=_T2,
    )
    superseded = ready.supersede(
        expected_revision=ready.revision,
        updated_at=_T3,
    )

    with pytest.raises(InvalidTransitionError):
        superseded.start_processing(
            expected_revision=superseded.revision,
            updated_at=_T3,
        )
    with pytest.raises(InvalidTransitionError):
        superseded.mark_ready(
            expected_revision=superseded.revision,
            updated_at=_T3,
        )
    with pytest.raises(InvalidTransitionError):
        superseded.supersede(
            expected_revision=superseded.revision,
            updated_at=_T3,
        )
    with pytest.raises(InvalidTransitionError):
        ready.start_processing(expected_revision=ready.revision, updated_at=_T3)
    with pytest.raises(InvalidTransitionError):
        ready.mark_failed(
            "cannot roll back ready",
            expected_revision=ready.revision,
            updated_at=_T3,
        )


def test_processing_revision_conflict_is_project_owned() -> None:
    registered = _registered()

    with pytest.raises(RevisionConflictError) as caught:
        registered.start_processing(
            expected_revision=Revision(3),
            updated_at=_T1,
        )

    assert caught.value.category == "source_evidence"
    assert caught.value.code == "revision_conflict"
    assert caught.value.safe_context == {
        "current_revision": "0",
        "expected_revision": "3",
        "resource": "source_version_processing",
    }


def test_failed_requires_nonempty_safe_summary() -> None:
    with pytest.raises(ValueError):
        _processing().mark_failed(
            "   ",
            expected_revision=Revision(1),
            updated_at=_T2,
        )

    with pytest.raises(ValueError):
        SourceVersionProcessing(
            source_version_id=_VERSION_ID,
            status=SourceProcessingStatus.FAILED,
            revision=Revision.initial(),
            failure_summary=None,
            updated_at=_T0,
        )
