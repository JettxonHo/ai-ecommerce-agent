"""Contract tests for the provider-neutral runtime diagnostic seam."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError, fields, is_dataclass
from datetime import UTC, datetime, timedelta, timezone
from inspect import signature
from typing import get_type_hints

import pytest

import ai_ecommerce_agent.application as application_package
from ai_ecommerce_agent.application import runtime_diagnostics

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = [
    "CorrelationId",
    "RuntimeDiagnosticLevel",
    "RuntimeDiagnosticEvent",
    "encode_runtime_diagnostic_event",
]
_IDENTITY_FIELDS = [
    "task_id",
    "run_id",
    "skill_run_id",
    "node_execution_id",
    "attempt_id",
    "error_id",
    "model_call_id",
    "provider_attempt_id",
    "retrieval_run_id",
    "review_id",
    "source_version_id",
]
_ERROR_DETAIL_FIELDS = [
    "error_category",
    "retryability",
    "disposition",
    "component",
]


def _minimal_event() -> runtime_diagnostics.RuntimeDiagnosticEvent:
    return runtime_diagnostics.RuntimeDiagnosticEvent(
        datetime(2026, 1, 2, 3, 4, 5, 678900, tzinfo=UTC),
        runtime_diagnostics.RuntimeDiagnosticLevel.INFO,
        "run.started",
        "worker",
        "test",
        runtime_diagnostics.CorrelationId("corr-1"),
    )


def test_direct_facade_has_exact_ordered_symbols_and_no_application_reexport() -> None:
    assert runtime_diagnostics.__all__ == _EXPECTED_PUBLIC
    assert all(not hasattr(application_package, name) for name in _EXPECTED_PUBLIC)


def test_level_catalog_and_correlation_identity_contract() -> None:
    assert list(runtime_diagnostics.RuntimeDiagnosticLevel) == [
        runtime_diagnostics.RuntimeDiagnosticLevel.INFO,
        runtime_diagnostics.RuntimeDiagnosticLevel.WARNING,
        runtime_diagnostics.RuntimeDiagnosticLevel.ERROR,
        runtime_diagnostics.RuntimeDiagnosticLevel.CRITICAL,
    ]
    assert [level.value for level in runtime_diagnostics.RuntimeDiagnosticLevel] == [
        "info",
        "warning",
        "error",
        "critical",
    ]
    generated = runtime_diagnostics.CorrelationId.new()
    assert type(generated.value) is str
    assert len(generated.value) == 36
    assert generated != runtime_diagnostics.CorrelationId.new()


def test_correlation_id_is_frozen_slotted_ordered_and_exactly_typed() -> None:
    value = "corr-ordered"
    correlation_id = runtime_diagnostics.CorrelationId(value)

    assert is_dataclass(runtime_diagnostics.CorrelationId)
    assert fields(runtime_diagnostics.CorrelationId)[0].name == "value"
    assert runtime_diagnostics.CorrelationId.__slots__ == ("value",)
    assert get_type_hints(runtime_diagnostics.CorrelationId) == {"value": str}
    assert correlation_id.value is value
    assert not hasattr(correlation_id, "__dict__")
    assert runtime_diagnostics.CorrelationId("a") < runtime_diagnostics.CorrelationId(
        "b"
    )

    with pytest.raises(FrozenInstanceError):
        correlation_id.value = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del correlation_id.value  # type: ignore[misc]


def test_event_is_frozen_slotted_and_has_exact_annotations_and_order() -> None:
    event_type = runtime_diagnostics.RuntimeDiagnosticEvent
    assert is_dataclass(event_type)
    assert event_type.__slots__ == (
        "occurred_at",
        "level",
        "event_name",
        "service",
        "environment",
        "correlation_id",
        *_IDENTITY_FIELDS,
        *_ERROR_DETAIL_FIELDS,
    )
    assert [field.name for field in fields(event_type)] == list(event_type.__slots__)
    assert not hasattr(_minimal_event(), "__dict__")
    assert get_type_hints(event_type) == {
        "occurred_at": datetime,
        "level": runtime_diagnostics.RuntimeDiagnosticLevel,
        "event_name": str,
        "service": str,
        "environment": str,
        "correlation_id": runtime_diagnostics.CorrelationId,
        **dict.fromkeys(_IDENTITY_FIELDS, str | None),
        **dict.fromkeys(_ERROR_DETAIL_FIELDS, str | None),
    }
    assert list(
        signature(runtime_diagnostics.encode_runtime_diagnostic_event).parameters
    ) == ["event"]
    assert get_type_hints(runtime_diagnostics.encode_runtime_diagnostic_event) == {
        "event": event_type,
        "return": str,
    }


def test_minimal_event_encoding_is_compact_ordered_and_omits_absent_ids() -> None:
    encoded = runtime_diagnostics.encode_runtime_diagnostic_event(_minimal_event())
    assert encoded == (
        '{"occurred_at":"2026-01-02T03:04:05.678900Z",'
        '"level":"info","event_name":"run.started","service":"worker",'
        '"environment":"test","correlation_id":"corr-1"}'
    )
    assert "\n" not in encoded
    assert list(json.loads(encoded)) == [
        "occurred_at",
        "level",
        "event_name",
        "service",
        "environment",
        "correlation_id",
    ]


def test_present_error_detail_quartet_has_exact_order_and_encoding() -> None:
    event = runtime_diagnostics.RuntimeDiagnosticEvent(
        datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        runtime_diagnostics.RuntimeDiagnosticLevel.ERROR,
        "runtime.error.recorded",
        "worker",
        "test",
        runtime_diagnostics.CorrelationId("corr-1"),
        source_version_id="source-1",
        error_category="timeout_error",
        retryability="retryable",
        disposition="retry",
        component="dispatch-worker",
    )
    assert runtime_diagnostics.encode_runtime_diagnostic_event(event) == (
        '{"occurred_at":"2026-01-02T03:04:05Z",'
        '"level":"error","event_name":"runtime.error.recorded",'
        '"service":"worker","environment":"test",'
        '"correlation_id":"corr-1","source_version_id":"source-1",'
        '"error_category":"timeout_error","retryability":"retryable",'
        '"disposition":"retry","component":"dispatch-worker"}'
    )


def test_full_identity_event_normalizes_timezone_and_preserves_opaque_values() -> None:
    event = runtime_diagnostics.RuntimeDiagnosticEvent(
        datetime(2026, 1, 2, 5, 4, 5, tzinfo=timezone(timedelta(hours=2))),
        runtime_diagnostics.RuntimeDiagnosticLevel.CRITICAL,
        "provider.failed",
        "api",
        "prod",
        runtime_diagnostics.CorrelationId("root-corr"),
        *[f"{name}-opaque" for name in _IDENTITY_FIELDS],
    )
    assert runtime_diagnostics.encode_runtime_diagnostic_event(event) == (
        '{"occurred_at":"2026-01-02T03:04:05Z","level":"critical",'
        '"event_name":"provider.failed","service":"api","environment":"prod",'
        '"correlation_id":"root-corr","task_id":"task_id-opaque",'
        '"run_id":"run_id-opaque","skill_run_id":"skill_run_id-opaque",'
        '"node_execution_id":"node_execution_id-opaque",'
        '"attempt_id":"attempt_id-opaque","error_id":"error_id-opaque",'
        '"model_call_id":"model_call_id-opaque",'
        '"provider_attempt_id":"provider_attempt_id-opaque",'
        '"retrieval_run_id":"retrieval_run_id-opaque",'
        '"review_id":"review_id-opaque",'
        '"source_version_id":"source_version_id-opaque"}'
    )
