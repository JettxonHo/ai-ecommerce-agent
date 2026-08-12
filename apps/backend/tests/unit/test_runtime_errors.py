"""Behavioral tests for runtime error values and safe diagnostic projection."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, cast

import pytest

from ai_ecommerce_agent.application import runtime_errors
from ai_ecommerce_agent.application.runtime_diagnostics import (
    CorrelationId,
    RuntimeDiagnosticLevel,
    encode_runtime_diagnostic_event,
)
from ai_ecommerce_agent.shared_kernel import ResourceReference, RunId, TaskId

pytestmark = pytest.mark.unit


class _TextSubclass(str):
    pass


class _DatetimeSubclass(datetime):
    pass


class _ErrorIdSubclass(runtime_errors.ErrorId):
    pass


def _identity(**changes: Any) -> runtime_errors.RuntimeErrorIdentity:
    values: dict[str, Any] = {
        "error_id": runtime_errors.ErrorId("error-1"),
        "correlation_id": CorrelationId("corr-1"),
        "task_id": TaskId("task-1"),
        "run_id": RunId("run-1"),
        "skill_run_id": None,
        "node_execution_id": None,
        "attempt_id": None,
    }
    values.update(changes)
    return runtime_errors.RuntimeErrorIdentity(**values)


def _record(**changes: Any) -> runtime_errors.RuntimeErrorRecord:
    values: dict[str, Any] = {
        "identity": _identity(),
        "error_category": runtime_errors.RuntimeErrorCategory.TIMEOUT_ERROR,
        "severity": RuntimeDiagnosticLevel.ERROR,
        "retryability": runtime_errors.RuntimeErrorRetryability.RETRYABLE,
        "disposition": runtime_errors.RuntimeErrorDisposition.RETRY,
        "component": "worker",
        "user_safe_message": "The operation timed out.",
        "operator_summary": "Provider timeout while running the worker.",
        "provider_request_reference": ResourceReference("provider_request", "req-1"),
        "provider_response_reference": ResourceReference("provider_response", "resp-1"),
        "first_occurred_at": datetime(2026, 1, 1, tzinfo=UTC),
        "last_occurred_at": datetime(2026, 1, 1, 1, tzinfo=UTC),
        "remediation_options": ("retry", "pause"),
    }
    values.update(changes)
    return runtime_errors.RuntimeErrorRecord(**values)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("error_id", "raw"),
        ("error_id", None),
        ("error_id", _ErrorIdSubclass("error-1")),
        ("correlation_id", "raw"),
        ("task_id", "raw"),
        ("run_id", "raw"),
        ("skill_run_id", _TextSubclass("skill")),
        ("node_execution_id", ""),
        ("attempt_id", 1),
    ],
)
def test_identity_rejects_raw_null_subclass_and_wrong_optional_values(
    field: str, value: object
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _identity(**{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("error_category", "timeout_error"),
        ("error_category", None),
        ("severity", "error"),
        ("retryability", None),
        ("disposition", "retry"),
        ("component", _TextSubclass("worker")),
        ("user_safe_message", "   "),
        ("operator_summary", None),
        ("provider_request_reference", "raw"),
        ("provider_response_reference", object()),
        ("first_occurred_at", datetime(2026, 1, 1)),
        ("last_occurred_at", _DatetimeSubclass(2026, 1, 1, tzinfo=UTC)),
        ("remediation_options", ["retry"]),
        ("remediation_options", ("retry", _TextSubclass("pause"))),
        ("remediation_options", ("retry", "retry")),
    ],
)
def test_record_rejects_raw_subclass_null_and_invalid_value_shapes(
    field: str, value: object
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _record(**{field: value})


def test_record_accepts_four_representative_categories() -> None:
    records = (
        _record(
            error_category=runtime_errors.RuntimeErrorCategory.TRANSIENT_INFRASTRUCTURE_ERROR,
            retryability=runtime_errors.RuntimeErrorRetryability.RETRYABLE,
            disposition=runtime_errors.RuntimeErrorDisposition.RETRY,
        ),
        _record(
            error_category=runtime_errors.RuntimeErrorCategory.DATA_INTEGRITY_ERROR,
            retryability=runtime_errors.RuntimeErrorRetryability.NON_RETRYABLE,
            disposition=runtime_errors.RuntimeErrorDisposition.MANUAL_RECOVERY,
        ),
        _record(
            error_category=runtime_errors.RuntimeErrorCategory.PROVIDER_CONTENT_REJECTION,
            retryability=runtime_errors.RuntimeErrorRetryability.UNKNOWN,
            disposition=runtime_errors.RuntimeErrorDisposition.PAUSE,
        ),
        _record(
            error_category=runtime_errors.RuntimeErrorCategory.CANCELLATION,
            retryability=runtime_errors.RuntimeErrorRetryability.CONDITIONALLY_RETRYABLE,
            disposition=runtime_errors.RuntimeErrorDisposition.CANCEL,
        ),
    )
    events = [
        runtime_errors.runtime_error_to_diagnostic_event(
            record, service="worker", environment="test"
        )
        for record in records
    ]
    assert all(record.identity.task_id.value == "task-1" for record in records)
    assert [event.error_category for event in events] == [
        "transient_infrastructure_error",
        "data_integrity_error",
        "provider_content_rejection",
        "cancellation",
    ]
    assert [event.retryability for event in events] == [
        "retryable",
        "non_retryable",
        "unknown",
        "conditionally_retryable",
    ]
    assert [event.disposition for event in events] == [
        "retry",
        "manual_recovery",
        "pause",
        "cancel",
    ]
    assert {event.component for event in events} == {"worker"}


@pytest.mark.parametrize(
    "changes",
    [
        {"first_occurred_at": datetime(2026, 1, 2, tzinfo=UTC)},
        {"last_occurred_at": datetime(2025, 12, 31, tzinfo=UTC)},
        {"first_occurred_at": datetime(2026, 1, 1)},
        {"last_occurred_at": datetime(2026, 1, 1)},
    ],
)
def test_record_requires_comparable_ordered_aware_timestamps(
    changes: dict[str, Any],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _record(**changes)


def test_projection_is_fixed_payload_free_and_detached() -> None:
    record = _record(
        identity=_identity(
            skill_run_id="skill-1", node_execution_id="node-1", attempt_id="attempt-1"
        ),
        severity=RuntimeDiagnosticLevel.CRITICAL,
        provider_request_reference=ResourceReference("provider_request", "SECRET-REQ"),
        provider_response_reference=ResourceReference(
            "provider_response", "SECRET-RESP"
        ),
        remediation_options=("retry SECRET",),
    )
    event = runtime_errors.runtime_error_to_diagnostic_event(
        record, service="worker", environment="test"
    )
    assert event.occurred_at == record.last_occurred_at
    assert event.level is RuntimeDiagnosticLevel.CRITICAL
    assert event.event_name == "runtime.error.recorded"
    assert event.service == "worker"
    assert event.environment == "test"
    assert event.correlation_id is record.identity.correlation_id
    assert event.task_id == record.identity.task_id.value
    assert event.run_id == record.identity.run_id.value
    assert event.skill_run_id == "skill-1"
    assert event.node_execution_id == "node-1"
    assert event.attempt_id == "attempt-1"
    assert event.error_id == record.identity.error_id.value
    encoded = encode_runtime_diagnostic_event(event)
    payload = json.loads(encoded)
    assert payload == {
        "occurred_at": "2026-01-01T01:00:00Z",
        "level": "critical",
        "event_name": "runtime.error.recorded",
        "service": "worker",
        "environment": "test",
        "correlation_id": "corr-1",
        "task_id": "task-1",
        "run_id": "run-1",
        "skill_run_id": "skill-1",
        "node_execution_id": "node-1",
        "attempt_id": "attempt-1",
        "error_id": "error-1",
        "error_category": "timeout_error",
        "retryability": "retryable",
        "disposition": "retry",
        "component": "worker",
    }
    for marker in (
        "SECRET-REQ",
        "SECRET-RESP",
        "retry SECRET",
        "The operation timed out.",
        "Provider timeout while running the worker.",
        "critical",
    ):
        assert marker not in encoded or marker == "critical"


@pytest.mark.parametrize("field", ["service", "environment"])
@pytest.mark.parametrize("value", [None, 1, _TextSubclass("x"), " "])
def test_projection_rejects_non_exact_or_blank_destination_values(
    field: str, value: object
) -> None:
    with pytest.raises((TypeError, ValueError)):
        runtime_errors.runtime_error_to_diagnostic_event(
            _record(), **{field: cast(str, value)}
        )


def test_values_are_immutable_and_unknown_payload_fields_are_not_accepted() -> None:
    identity = _identity()
    record = _record(identity=identity)
    with pytest.raises((AttributeError, TypeError)):
        identity.task_id = TaskId("other")  # type: ignore[misc]
    with pytest.raises((AttributeError, TypeError)):
        del record.component  # type: ignore[misc]
    with pytest.raises(TypeError):
        _record(payload="secret")
