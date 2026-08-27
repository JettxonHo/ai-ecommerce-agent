"""Immutable Needs Input resource state and transitions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

from .evidence import InsufficientResultEvidence


class NeedsInputStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    SUPERSEDED = "superseded"
    CANCELLED = "cancelled"


class NeedsInputExpectedRecovery(StrEnum):
    RESUME = "resume"
    RERUN = "rerun"
    MANUAL_REVIEW = "manual_review"
    NONE = "none"


def _request_id(value: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError("action_request_id must be non-empty")
    if len(value.encode("utf-8")) > 200:
        raise ValueError("action_request_id exceeds its bounded size")
    return value


@dataclass(frozen=True, slots=True)
class NeedsInputActionRequestSnapshot:
    """Task-scoped current/history projection without ORM or HTTP types."""

    action_request_id: str
    task_id: TaskId
    revision: Revision
    status: NeedsInputStatus
    reason_type: str
    reason_summary: str
    affected_stages: tuple[str, ...]
    source_references: tuple[Mapping[str, object], ...]
    conflict_values: tuple[Mapping[str, object], ...]
    allowed_resolution_types: tuple[str, ...]
    expected_recovery: NeedsInputExpectedRecovery
    superseded_by: str | None
    created_at: datetime
    updated_at: datetime
    resolution_idempotency_key: str | None = None
    resolution_type: str | None = None
    resolution_payload: Mapping[str, object] | None = None
    resolved_at: datetime | None = None

    def __post_init__(self) -> None:
        _request_id(self.action_request_id)
        if type(self.task_id) is not TaskId:
            raise TypeError("task_id must be a TaskId")
        if type(self.revision) is not Revision:
            raise TypeError("revision must be a Revision")
        if type(self.status) is not NeedsInputStatus:
            raise TypeError("status must be a NeedsInputStatus")
        if not self.reason_type.strip():
            raise ValueError("reason_type must be non-empty")
        if not self.reason_summary.strip():
            raise ValueError("reason_summary must be non-empty")
        if not self.affected_stages:
            raise ValueError("affected_stages must not be empty")
        if not self.allowed_resolution_types:
            raise ValueError("allowed_resolution_types must not be empty")
        if type(self.expected_recovery) is not NeedsInputExpectedRecovery:
            raise TypeError("expected_recovery must be a NeedsInputExpectedRecovery")
        if self.status is NeedsInputStatus.SUPERSEDED:
            if self.superseded_by == self.action_request_id:
                raise ValueError(
                    "superseded request successor must differ from the request"
                )
        elif self.superseded_by is not None:
            raise ValueError("only a superseded request may reference a successor")
        if self.status in (NeedsInputStatus.OPEN, NeedsInputStatus.SUPERSEDED):
            if any(
                value is not None
                for value in (
                    self.resolution_idempotency_key,
                    self.resolution_type,
                    self.resolution_payload,
                    self.resolved_at,
                )
            ):
                raise ValueError(
                    "non-terminal request cannot carry resolution evidence"
                )
        else:
            if (
                not self.resolution_idempotency_key
                or not self.resolution_type
                or self.resolution_payload is None
                or self.resolved_at is None
            ):
                raise ValueError("terminal request requires resolution evidence")
            if self.status is NeedsInputStatus.CANCELLED:
                if self.resolution_type != "cancel_path":
                    raise ValueError(
                        "cancelled request requires the cancel_path resolution"
                    )
            elif self.resolution_type not in {
                "provide_source_reference",
                "choose_existing_value",
                "submit_correction",
                "confirm_known_limitation",
            }:
                raise ValueError(
                    "resolved request requires a committed non-cancel resolution"
                )
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("request timestamps must be timezone-aware")
        if self.resolved_at is not None and self.resolved_at.tzinfo is None:
            raise ValueError("resolution timestamp must be timezone-aware")

    @classmethod
    def from_evidence(
        cls,
        evidence: InsufficientResultEvidence,
        *,
        action_request_id: str,
        now: datetime,
    ) -> NeedsInputActionRequestSnapshot:
        """Derive one finite request without adding unsupported facts."""

        return cls(
            action_request_id=action_request_id,
            task_id=evidence.task_id,
            revision=Revision.initial(),
            status=NeedsInputStatus.OPEN,
            reason_type="missing_information",
            reason_summary="; ".join(evidence.missing_information),
            affected_stages=evidence.affected_stages,
            source_references=evidence.source_references,
            conflict_values=evidence.conflict_values,
            allowed_resolution_types=(
                "provide_source_reference",
                "submit_correction",
                "confirm_known_limitation",
                "cancel_path",
            ),
            expected_recovery=NeedsInputExpectedRecovery.RERUN,
            superseded_by=None,
            created_at=now,
            updated_at=now,
        )

    def supersede(
        self, successor_action_request_id: str | None, *, now: datetime
    ) -> NeedsInputActionRequestSnapshot:
        """Move the old current request to durable terminal history.

        A newer Needs Input request supplies a same-Task successor identity;
        a newer sufficient result may intentionally supersede without one.
        """

        if self.status is not NeedsInputStatus.OPEN:
            raise ValueError("only an open request may be superseded")
        return replace(
            self,
            revision=self.revision.next(),
            status=NeedsInputStatus.SUPERSEDED,
            superseded_by=(
                _request_id(successor_action_request_id)
                if successor_action_request_id is not None
                else None
            ),
            updated_at=now,
        )

    def resolved(
        self,
        *,
        idempotency_key: str,
        resolution_type: str,
        resolution_payload: Mapping[str, object],
        now: datetime,
        cancelled: bool,
    ) -> NeedsInputActionRequestSnapshot:
        """Commit one validated resolution as the terminal projection."""

        if self.status is not NeedsInputStatus.OPEN:
            raise ValueError("only an open request may be resolved")
        return replace(
            self,
            revision=self.revision.next(),
            status=NeedsInputStatus.CANCELLED
            if cancelled
            else NeedsInputStatus.RESOLVED,
            resolution_idempotency_key=idempotency_key,
            resolution_type=resolution_type,
            resolution_payload=dict(resolution_payload),
            resolved_at=now,
            updated_at=now,
        )


__all__ = [
    "NeedsInputActionRequestSnapshot",
    "NeedsInputExpectedRecovery",
    "NeedsInputStatus",
]
