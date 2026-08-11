"""Contract tests for the local runtime diagnostic JSON-line sink."""

from __future__ import annotations

import inspect
from datetime import UTC, datetime, timedelta, timezone
from io import StringIO
from typing import TextIO, get_type_hints

import pytest

from ai_ecommerce_agent.application.runtime_diagnostics import (
    CorrelationId,
    RuntimeDiagnosticEvent,
    RuntimeDiagnosticLevel,
    encode_runtime_diagnostic_event,
)
from ai_ecommerce_agent.platform import runtime_diagnostics

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = ["RuntimeDiagnosticJsonLineSink"]


def _event(
    level: RuntimeDiagnosticLevel = RuntimeDiagnosticLevel.INFO,
    *,
    full: bool = False,
) -> RuntimeDiagnosticEvent:
    identities = (
        {
            "task_id": "task-opaque",
            "run_id": "run-opaque",
            "skill_run_id": "skill-opaque",
            "node_execution_id": "node-opaque",
            "attempt_id": "attempt-opaque",
            "error_id": "error-opaque",
            "model_call_id": "model-opaque",
            "provider_attempt_id": "provider-opaque",
            "retrieval_run_id": "retrieval-opaque",
            "review_id": "review-opaque",
            "source_version_id": "source-opaque",
        }
        if full
        else {}
    )
    return RuntimeDiagnosticEvent(
        datetime(2026, 1, 2, 3, 4, 5, 678900, tzinfo=timezone(timedelta(hours=2))),
        level,
        "run.started",
        "worker",
        "test",
        CorrelationId("corr-opaque"),
        **identities,
    )


def test_sink_facade_and_signatures_are_exact() -> None:
    sink_type = runtime_diagnostics.RuntimeDiagnosticJsonLineSink

    assert runtime_diagnostics.__all__ == _EXPECTED_PUBLIC
    constructor = inspect.signature(sink_type)
    assert list(constructor.parameters) == ["stream"]
    assert constructor.parameters["stream"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_type_hints(sink_type.__init__) == {
        "stream": TextIO,
        "return": type(None),
    }

    emit = inspect.signature(sink_type.emit)
    assert list(emit.parameters) == ["self", "event"]
    assert emit.parameters["event"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert get_type_hints(sink_type.emit) == {
        "event": RuntimeDiagnosticEvent,
        "return": type(None),
    }


def test_minimal_and_full_events_are_exactly_one_canonical_json_line() -> None:
    stream = StringIO()
    sink = runtime_diagnostics.RuntimeDiagnosticJsonLineSink(stream=stream)
    events = (_event(), _event(RuntimeDiagnosticLevel.CRITICAL, full=True))

    for event in events:
        sink.emit(event)

    assert stream.getvalue() == "".join(
        f"{encode_runtime_diagnostic_event(event)}\n" for event in events
    )
    assert stream.getvalue().count("\n") == len(events)
    assert stream.getvalue().splitlines() == [
        encode_runtime_diagnostic_event(event) for event in events
    ]


def test_all_levels_and_unicode_identity_values_emit_without_extra_fields() -> None:
    stream = StringIO()
    sink = runtime_diagnostics.RuntimeDiagnosticJsonLineSink(stream=stream)
    events = tuple(
        RuntimeDiagnosticEvent(
            datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
            level,
            "provider.✓",
            "service",
            "test",
            CorrelationId("秘密-correlation"),
            task_id="task-✓",
        )
        for level in RuntimeDiagnosticLevel
    )

    for event in events:
        sink.emit(event)

    assert stream.getvalue() == "".join(
        f"{encode_runtime_diagnostic_event(event)}\n" for event in events
    )
    assert '"message"' not in stream.getvalue()
    assert '"extra"' not in stream.getvalue()
