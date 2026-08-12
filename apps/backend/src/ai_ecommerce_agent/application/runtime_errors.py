"""Provider-neutral runtime error values and payload-free diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from ai_ecommerce_agent.application.runtime_diagnostics import (
    CorrelationId,
    RuntimeDiagnosticEvent,
    RuntimeDiagnosticLevel,
)
from ai_ecommerce_agent.shared_kernel import ResourceReference, RunId, TaskId

__all__ = [
    "ErrorId",
    "RuntimeErrorCategory",
    "RuntimeErrorRetryability",
    "RuntimeErrorDisposition",
    "RuntimeErrorIdentity",
    "RuntimeErrorRecord",
    "runtime_error_to_diagnostic_event",
]


def _require_text(value: object, field_name: str) -> None:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be an exact string")
    if not value.strip():
        raise ValueError(f"{field_name} must not be blank")


def _require_optional_text(value: object, field_name: str) -> None:
    if value is not None:
        _require_text(value, field_name)


def _require_timestamp(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise TypeError(f"{field_name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True, slots=True, order=True)
class ErrorId:
    """Opaque application-owned identity for one runtime error record."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "error_id")

    @classmethod
    def new(cls) -> ErrorId:
        return cls(str(uuid4()))


class RuntimeErrorCategory(StrEnum):
    """Accepted physical runtime error categories."""

    TRANSIENT_INFRASTRUCTURE_ERROR = "transient_infrastructure_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    TIMEOUT_ERROR = "timeout_error"
    STRUCTURED_OUTPUT_ERROR = "structured_output_error"
    VALIDATION_ERROR = "validation_error"
    PERMISSION_OR_AUTHENTICATION_ERROR = "permission_or_authentication_error"
    DATA_INTEGRITY_ERROR = "data_integrity_error"
    DEPENDENCY_CONFIGURATION_ERROR = "dependency_configuration_error"
    PROVIDER_CONTENT_REJECTION = "provider_content_rejection"
    CANCELLATION = "cancellation"


class RuntimeErrorRetryability(StrEnum):
    """Retryability classification for a runtime error."""

    RETRYABLE = "retryable"
    CONDITIONALLY_RETRYABLE = "conditionally_retryable"
    NON_RETRYABLE = "non_retryable"
    UNKNOWN = "unknown"


class RuntimeErrorDisposition(StrEnum):
    """Next-step disposition for a runtime error."""

    RETRY = "retry"
    FALLBACK = "fallback"
    WAIT = "wait"
    PAUSE = "pause"
    FAIL = "fail"
    CANCEL = "cancel"
    MANUAL_RECOVERY = "manual_recovery"


@dataclass(frozen=True, slots=True)
class RuntimeErrorIdentity:
    """Exact identity chain attached to a runtime error record."""

    error_id: ErrorId
    correlation_id: CorrelationId
    task_id: TaskId
    run_id: RunId
    skill_run_id: str | None = None
    node_execution_id: str | None = None
    attempt_id: str | None = None

    def __post_init__(self) -> None:
        if type(self.error_id) is not ErrorId:
            raise TypeError("error_id must be an ErrorId")
        if type(self.correlation_id) is not CorrelationId:
            raise TypeError("correlation_id must be a CorrelationId")
        if type(self.task_id) is not TaskId:
            raise TypeError("task_id must be a TaskId")
        if type(self.run_id) is not RunId:
            raise TypeError("run_id must be a RunId")
        for field_name, value in (
            ("skill_run_id", self.skill_run_id),
            ("node_execution_id", self.node_execution_id),
            ("attempt_id", self.attempt_id),
        ):
            _require_optional_text(value, field_name)


@dataclass(frozen=True, slots=True)
class RuntimeErrorRecord:
    """Immutable, payload-free physical runtime error record."""

    identity: RuntimeErrorIdentity
    error_category: RuntimeErrorCategory
    severity: RuntimeDiagnosticLevel
    retryability: RuntimeErrorRetryability
    disposition: RuntimeErrorDisposition
    component: str
    user_safe_message: str
    operator_summary: str
    provider_request_reference: ResourceReference | None
    provider_response_reference: ResourceReference | None
    first_occurred_at: datetime
    last_occurred_at: datetime
    remediation_options: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if type(self.identity) is not RuntimeErrorIdentity:
            raise TypeError("identity must be a RuntimeErrorIdentity")
        if type(self.error_category) is not RuntimeErrorCategory:
            raise TypeError("error_category must be a RuntimeErrorCategory")
        if type(self.severity) is not RuntimeDiagnosticLevel:
            raise TypeError("severity must be a RuntimeDiagnosticLevel")
        if type(self.retryability) is not RuntimeErrorRetryability:
            raise TypeError("retryability must be a RuntimeErrorRetryability")
        if type(self.disposition) is not RuntimeErrorDisposition:
            raise TypeError("disposition must be a RuntimeErrorDisposition")
        _require_text(self.component, "component")
        _require_text(self.user_safe_message, "user_safe_message")
        _require_text(self.operator_summary, "operator_summary")
        for field_name, value in (
            ("provider_request_reference", self.provider_request_reference),
            ("provider_response_reference", self.provider_response_reference),
        ):
            if value is not None and type(value) is not ResourceReference:
                raise TypeError(f"{field_name} must be a ResourceReference or None")
        _require_timestamp(self.first_occurred_at, "first_occurred_at")
        _require_timestamp(self.last_occurred_at, "last_occurred_at")
        if self.last_occurred_at < self.first_occurred_at:
            raise ValueError("last_occurred_at must not precede first_occurred_at")
        if type(self.remediation_options) is not tuple:
            raise TypeError("remediation_options must be an exact tuple")
        seen: set[str] = set()
        for option in self.remediation_options:
            _require_text(option, "remediation option")
            if option in seen:
                raise ValueError("remediation_options must not contain duplicates")
            seen.add(option)


def runtime_error_to_diagnostic_event(
    record: RuntimeErrorRecord, *, service: str, environment: str
) -> RuntimeDiagnosticEvent:
    """Project one error record into the canonical payload-free event."""

    if type(record) is not RuntimeErrorRecord:
        raise TypeError("record must be a RuntimeErrorRecord")
    _require_text(service, "service")
    _require_text(environment, "environment")
    identity = record.identity
    return RuntimeDiagnosticEvent(
        record.last_occurred_at.astimezone(UTC),
        record.severity,
        "runtime.error.recorded",
        service,
        environment,
        identity.correlation_id,
        task_id=identity.task_id.value,
        run_id=identity.run_id.value,
        skill_run_id=identity.skill_run_id,
        node_execution_id=identity.node_execution_id,
        attempt_id=identity.attempt_id,
        error_id=identity.error_id.value,
        error_category=record.error_category.value,
        retryability=record.retryability.value,
        disposition=record.disposition.value,
        component=record.component,
    )
