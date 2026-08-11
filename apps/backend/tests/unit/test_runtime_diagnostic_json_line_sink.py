"""Behavioral tests for the local runtime diagnostic JSON-line sink."""

from __future__ import annotations

from datetime import UTC, datetime
from io import StringIO
from typing import cast

import pytest

from ai_ecommerce_agent.application.runtime_diagnostics import (
    CorrelationId,
    RuntimeDiagnosticEvent,
    RuntimeDiagnosticLevel,
    encode_runtime_diagnostic_event,
)
from ai_ecommerce_agent.platform.runtime_diagnostics import (
    RuntimeDiagnosticJsonLineSink,
)

pytestmark = pytest.mark.unit


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


@pytest.mark.parametrize("invalid", [None, {}, {"event_name": "raw"}, "message"])
def test_invalid_event_writes_nothing(invalid: object) -> None:
    stream = StringIO()
    sink = RuntimeDiagnosticJsonLineSink(stream=stream)

    with pytest.raises(TypeError):
        sink.emit(cast(RuntimeDiagnosticEvent, invalid))

    assert stream.getvalue() == ""


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
