"""Small, provider-neutral runtime diagnostic event contract.

This module owns only strict value validation and deterministic payload-free
projection.  Logging sinks, persistence, propagation, and error records stay
outside this seam.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

__all__ = [
    "CorrelationId",
    "RuntimeDiagnosticLevel",
    "RuntimeDiagnosticEvent",
    "encode_runtime_diagnostic_event",
]

_RUNTIME_ERROR_CATEGORIES = (
    "transient_infrastructure_error",
    "rate_limit_error",
    "timeout_error",
    "structured_output_error",
    "validation_error",
    "permission_or_authentication_error",
    "data_integrity_error",
    "dependency_configuration_error",
    "provider_content_rejection",
    "cancellation",
)
_RUNTIME_ERROR_RETRYABILITIES = (
    "retryable",
    "conditionally_retryable",
    "non_retryable",
    "unknown",
)
_RUNTIME_ERROR_DISPOSITIONS = (
    "retry",
    "fallback",
    "wait",
    "pause",
    "fail",
    "cancel",
    "manual_recovery",
)


def _require_text(value: object, field_name: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be an exact string")
    if not value.strip():
        raise ValueError(f"{field_name} must not be blank")


def _require_identity(value: object, field_name: str) -> None:
    if value is None:
        return
    _require_text(value, field_name)


@dataclass(frozen=True, slots=True, order=True)
class CorrelationId:
    """Opaque server-owned root identity for one runtime execution chain."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "correlation_id")

    @classmethod
    def new(cls) -> CorrelationId:
        """Create a fresh opaque UUID correlation root."""

        return cls(str(uuid4()))


class RuntimeDiagnosticLevel(StrEnum):
    """The accepted severity catalog for diagnostic events."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class RuntimeDiagnosticEvent:
    """Strict payload-free event envelope with an ordered identity chain."""

    occurred_at: datetime
    level: RuntimeDiagnosticLevel
    event_name: str
    service: str
    environment: str
    correlation_id: CorrelationId
    task_id: str | None = None
    run_id: str | None = None
    skill_run_id: str | None = None
    node_execution_id: str | None = None
    attempt_id: str | None = None
    error_id: str | None = None
    model_call_id: str | None = None
    provider_attempt_id: str | None = None
    retrieval_run_id: str | None = None
    review_id: str | None = None
    source_version_id: str | None = None
    error_category: str | None = None
    retryability: str | None = None
    disposition: str | None = None
    component: str | None = None

    def __post_init__(self) -> None:
        if type(self.occurred_at) is not datetime:
            raise TypeError("occurred_at must be an exact datetime")
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        if type(self.level) is not RuntimeDiagnosticLevel:
            raise TypeError("level must be a RuntimeDiagnosticLevel")
        _require_text(self.event_name, "event_name")
        _require_text(self.service, "service")
        _require_text(self.environment, "environment")
        if type(self.correlation_id) is not CorrelationId:
            raise TypeError("correlation_id must be a CorrelationId")
        for field_name, value in (
            ("task_id", self.task_id),
            ("run_id", self.run_id),
            ("skill_run_id", self.skill_run_id),
            ("node_execution_id", self.node_execution_id),
            ("attempt_id", self.attempt_id),
            ("error_id", self.error_id),
            ("model_call_id", self.model_call_id),
            ("provider_attempt_id", self.provider_attempt_id),
            ("retrieval_run_id", self.retrieval_run_id),
            ("review_id", self.review_id),
            ("source_version_id", self.source_version_id),
        ):
            _require_identity(value, field_name)
        details = (
            self.error_category,
            self.retryability,
            self.disposition,
            self.component,
        )
        if any(value is None for value in details):
            if any(value is not None for value in details):
                raise ValueError("runtime error details must be all present or absent")
        else:
            category, retryability, disposition, component = details
            if type(category) is not str or category not in _RUNTIME_ERROR_CATEGORIES:
                raise ValueError("error_category must be an accepted runtime value")
            if (
                type(retryability) is not str
                or retryability not in _RUNTIME_ERROR_RETRYABILITIES
            ):
                raise ValueError("retryability must be an accepted runtime value")
            if (
                type(disposition) is not str
                or disposition not in _RUNTIME_ERROR_DISPOSITIONS
            ):
                raise ValueError("disposition must be an accepted runtime value")
            _require_text(component, "component")


def encode_runtime_diagnostic_event(event: RuntimeDiagnosticEvent) -> str:
    """Encode one event as compact deterministic JSON without a newline."""

    if type(event) is not RuntimeDiagnosticEvent:
        raise TypeError("event must be a RuntimeDiagnosticEvent")
    payload: dict[str, str] = {
        "occurred_at": event.occurred_at.astimezone(UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "level": event.level.value,
        "event_name": event.event_name,
        "service": event.service,
        "environment": event.environment,
        "correlation_id": event.correlation_id.value,
    }
    for field_name, value in (
        ("task_id", event.task_id),
        ("run_id", event.run_id),
        ("skill_run_id", event.skill_run_id),
        ("node_execution_id", event.node_execution_id),
        ("attempt_id", event.attempt_id),
        ("error_id", event.error_id),
        ("model_call_id", event.model_call_id),
        ("provider_attempt_id", event.provider_attempt_id),
        ("retrieval_run_id", event.retrieval_run_id),
        ("review_id", event.review_id),
        ("source_version_id", event.source_version_id),
    ):
        if value is not None:
            payload[field_name] = value
    for field_name, value in (
        ("error_category", event.error_category),
        ("retryability", event.retryability),
        ("disposition", event.disposition),
        ("component", event.component),
    ):
        if value is not None:
            payload[field_name] = value
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
