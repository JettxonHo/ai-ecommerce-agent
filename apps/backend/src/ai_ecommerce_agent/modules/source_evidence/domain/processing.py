"""Revisioned Source Version processing Current Truth."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self

from ai_ecommerce_agent.shared_kernel import Revision, SourceVersionId

from .errors import InvalidTransitionError, RevisionConflictError
from .snapshots import SourceProcessingStatus


def _require_revision(current: Revision, expected: Revision) -> None:
    if current != expected:
        raise RevisionConflictError(
            resource="source_version_processing",
            expected=expected,
            current=current,
        )


def _require_text(value: str, *, field: str) -> None:
    if not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _invalid(
    processing: SourceVersionProcessing,
    *,
    intent: str,
) -> InvalidTransitionError:
    return InvalidTransitionError(
        resource="source_version_processing",
        status=processing.status.value,
        intent=intent,
    )


@dataclass(frozen=True, slots=True)
class SourceVersionProcessing:
    """Mutable processing state represented as an immutable transition value.

    The application persists the returned value with an expected-revision CAS;
    this domain object itself never mutates in place or owns persistence.
    """

    source_version_id: SourceVersionId
    status: SourceProcessingStatus
    revision: Revision
    failure_summary: str | None
    updated_at: datetime

    def __post_init__(self) -> None:
        if self.status is SourceProcessingStatus.FAILED:
            if self.failure_summary is None:
                raise ValueError("failed processing requires failure_summary")
            _require_text(self.failure_summary, field="failure_summary")
        elif self.failure_summary is not None:
            raise ValueError(
                "failure_summary is only retained while processing is failed"
            )

    @classmethod
    def create(
        cls,
        source_version_id: SourceVersionId,
        *,
        updated_at: datetime,
    ) -> Self:
        """Register a Source Version before processing begins."""

        return cls(
            source_version_id=source_version_id,
            status=SourceProcessingStatus.REGISTERED,
            revision=Revision.initial(),
            failure_summary=None,
            updated_at=updated_at,
        )

    def start_processing(
        self,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Start processing from ``registered`` or retry from ``failed``."""

        _require_revision(self.revision, expected_revision)
        if self.status not in {
            SourceProcessingStatus.REGISTERED,
            SourceProcessingStatus.FAILED,
        }:
            raise _invalid(self, intent="start_processing")
        return replace(
            self,
            status=SourceProcessingStatus.PROCESSING,
            revision=self.revision.next(),
            failure_summary=None,
            updated_at=updated_at,
        )

    def mark_ready(
        self,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Mark processing ready when all accepted input is usable."""

        _require_revision(self.revision, expected_revision)
        self._require_completion_source(intent="mark_ready")
        return replace(
            self,
            status=SourceProcessingStatus.READY,
            revision=self.revision.next(),
            failure_summary=None,
            updated_at=updated_at,
        )

    def mark_ready_with_rejections(
        self,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Mark processing usable while retaining bounded item rejections."""

        _require_revision(self.revision, expected_revision)
        self._require_completion_source(intent="mark_ready_with_rejections")
        return replace(
            self,
            status=SourceProcessingStatus.READY_WITH_REJECTIONS,
            revision=self.revision.next(),
            failure_summary=None,
            updated_at=updated_at,
        )

    def mark_failed(
        self,
        failure_summary: str,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Record a safe summary for a registered or running failure."""

        _require_revision(self.revision, expected_revision)
        _require_text(failure_summary, field="failure_summary")
        if self.status not in {
            SourceProcessingStatus.REGISTERED,
            SourceProcessingStatus.PROCESSING,
        }:
            raise _invalid(self, intent="mark_failed")
        return replace(
            self,
            status=SourceProcessingStatus.FAILED,
            revision=self.revision.next(),
            failure_summary=failure_summary,
            updated_at=updated_at,
        )

    def supersede(
        self,
        *,
        expected_revision: Revision,
        updated_at: datetime,
    ) -> Self:
        """Mark any non-superseded processing record terminally obsolete."""

        _require_revision(self.revision, expected_revision)
        if self.status is SourceProcessingStatus.SUPERSEDED:
            raise _invalid(self, intent="supersede")
        return replace(
            self,
            status=SourceProcessingStatus.SUPERSEDED,
            revision=self.revision.next(),
            failure_summary=None,
            updated_at=updated_at,
        )

    def _require_completion_source(self, *, intent: str) -> None:
        if self.status not in {
            SourceProcessingStatus.REGISTERED,
            SourceProcessingStatus.PROCESSING,
        }:
            raise _invalid(self, intent=intent)


__all__ = ["SourceVersionProcessing"]
