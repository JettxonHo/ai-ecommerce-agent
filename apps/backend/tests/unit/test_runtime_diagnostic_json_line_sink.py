"""Behavioral tests for the local runtime diagnostic JSON-line sink."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from io import StringIO
from typing import cast

import pytest

from ai_ecommerce_agent.application import runtime_errors
from ai_ecommerce_agent.application.runtime_diagnostics import (
    CorrelationId,
    RuntimeDiagnosticEvent,
    RuntimeDiagnosticLevel,
    encode_runtime_diagnostic_event,
)
from ai_ecommerce_agent.platform.runtime_diagnostics import (
    RuntimeDiagnosticJsonLineSink,
)
from ai_ecommerce_agent.shared_kernel import ResourceReference, RunId, TaskId

pytestmark = pytest.mark.unit


class CountingStringIO(StringIO):
    """Real text stream that records writes without mocking the stream API."""

    def __init__(self) -> None:
        super().__init__()
        self.write_calls = 0
        self.writes: list[str] = []

    def write(self, data: str) -> int:
        self.write_calls += 1
        self.writes.append(data)
        return super().write(data)


def _event(
    name: str = "task.started",
    *,
    level: RuntimeDiagnosticLevel = RuntimeDiagnosticLevel.INFO,
) -> RuntimeDiagnosticEvent:
    return RuntimeDiagnosticEvent(
        datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        level,
        name,
        "worker",
        "test",
        CorrelationId("corr"),
        task_id=f"{name}-task",
    )


def test_sequential_events_are_independent_and_stream_remains_caller_owned() -> None:
    stream = StringIO()
    sink = RuntimeDiagnosticJsonLineSink(stream=stream)
    first = _event("first", level=RuntimeDiagnosticLevel.WARNING)
    second = _event("second", level=RuntimeDiagnosticLevel.ERROR)

    sink.emit(first)
    sink.emit(second)

    assert not stream.closed
    assert stream.getvalue() == (
        f"{encode_runtime_diagnostic_event(first)}\n"
        f"{encode_runtime_diagnostic_event(second)}\n"
    )
    assert "first-task" in stream.getvalue()
    assert "second-task" in stream.getvalue()


def test_successful_emit_writes_exactly_once_with_one_newline() -> None:
    stream = CountingStringIO()
    sink = RuntimeDiagnosticJsonLineSink(stream=stream)
    events = (_event("first"), _event("second", level=RuntimeDiagnosticLevel.ERROR))

    for event in events:
        before = stream.write_calls
        sink.emit(event)
        assert stream.write_calls == before + 1
        assert stream.writes[-1] == f"{encode_runtime_diagnostic_event(event)}\n"
        assert stream.writes[-1].count("\n") == 1

    assert stream.write_calls == len(events)


def test_runtime_error_event_sink_preserves_the_appended_detail_quartet() -> None:
    stream = CountingStringIO()
    sink = RuntimeDiagnosticJsonLineSink(stream=stream)
    base = _event("runtime.error.recorded", level=RuntimeDiagnosticLevel.ERROR)
    event = RuntimeDiagnosticEvent(
        base.occurred_at,
        base.level,
        base.event_name,
        base.service,
        base.environment,
        base.correlation_id,
        base.task_id,
        error_category="timeout_error",
        retryability="retryable",
        disposition="retry",
        component="worker",
    )
    sink.emit(event)
    assert stream.write_calls == 1
    assert stream.writes == [f"{encode_runtime_diagnostic_event(event)}\n"]


def test_runtime_error_record_reaches_real_sink_without_sensitive_fields() -> None:
    stream = CountingStringIO()
    sink = RuntimeDiagnosticJsonLineSink(stream=stream)
    occurred_at = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    record = runtime_errors.RuntimeErrorRecord(
        identity=runtime_errors.RuntimeErrorIdentity(
            error_id=runtime_errors.ErrorId("error-1"),
            correlation_id=CorrelationId("corr"),
            task_id=TaskId("task-1"),
            run_id=RunId("run-1"),
        ),
        error_category=runtime_errors.RuntimeErrorCategory.TIMEOUT_ERROR,
        severity=RuntimeDiagnosticLevel.ERROR,
        retryability=runtime_errors.RuntimeErrorRetryability.RETRYABLE,
        disposition=runtime_errors.RuntimeErrorDisposition.RETRY,
        component="worker",
        user_safe_message="safe-user-marker",
        operator_summary="operator-summary-marker",
        provider_request_reference=ResourceReference(
            "provider_request", "provider-request-marker"
        ),
        provider_response_reference=ResourceReference(
            "provider_response", "provider-response-marker"
        ),
        first_occurred_at=occurred_at,
        last_occurred_at=occurred_at,
        remediation_options=("remediation-marker",),
    )

    event = runtime_errors.runtime_error_to_diagnostic_event(
        record, service="worker", environment="test"
    )
    sink.emit(event)

    payload = json.loads(stream.getvalue())
    assert set(payload) == {
        "occurred_at",
        "level",
        "event_name",
        "service",
        "environment",
        "correlation_id",
        "task_id",
        "run_id",
        "error_id",
        "error_category",
        "retryability",
        "disposition",
        "component",
    }
    assert payload["error_category"] == "timeout_error"
    assert payload["retryability"] == "retryable"
    assert payload["disposition"] == "retry"
    assert payload["component"] == "worker"
    for marker in (
        "safe-user-marker",
        "operator-summary-marker",
        "provider-request-marker",
        "provider-response-marker",
        "remediation-marker",
    ):
        assert marker not in stream.getvalue()


@pytest.mark.parametrize("invalid", [None, {}, {"event_name": "raw"}, "message"])
def test_invalid_event_writes_nothing(invalid: object) -> None:
    stream = CountingStringIO()
    sink = RuntimeDiagnosticJsonLineSink(stream=stream)

    with pytest.raises(TypeError):
        sink.emit(cast(RuntimeDiagnosticEvent, invalid))

    assert stream.getvalue() == ""
    assert stream.write_calls == 0


def test_event_subclass_is_rejected_without_a_write() -> None:
    event = _event()

    class EventSubclass(RuntimeDiagnosticEvent):
        pass

    subclass = EventSubclass(
        event.occurred_at,
        event.level,
        event.event_name,
        event.service,
        event.environment,
        event.correlation_id,
        event.task_id,
    )
    stream = StringIO()
    sink = RuntimeDiagnosticJsonLineSink(stream=stream)

    with pytest.raises(TypeError):
        sink.emit(cast(RuntimeDiagnosticEvent, subclass))

    assert stream.getvalue() == ""


def test_constructor_is_keyword_only_without_payload_escape_hatch() -> None:
    with pytest.raises(TypeError):
        RuntimeDiagnosticJsonLineSink(StringIO())  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        RuntimeDiagnosticJsonLineSink(stream=None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        RuntimeDiagnosticJsonLineSink(stream=StringIO(), message="raw")  # type: ignore[call-arg]

    stream = StringIO()
    sink = RuntimeDiagnosticJsonLineSink(stream=stream)
    with pytest.raises(TypeError):
        sink.emit(cast(RuntimeDiagnosticEvent, object()))
    assert stream.getvalue() == ""
