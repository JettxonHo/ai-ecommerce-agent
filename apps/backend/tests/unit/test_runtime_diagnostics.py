"""Behavioral validation for runtime diagnostic values and projection."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, cast

import pytest

from ai_ecommerce_agent.application.runtime_diagnostics import (
    CorrelationId,
    RuntimeDiagnosticEvent,
    RuntimeDiagnosticLevel,
    encode_runtime_diagnostic_event,
)

pytestmark = pytest.mark.unit


class _TextSubclass(str):
    pass


class _DatetimeSubclass(datetime):
    pass


_IDENTITY_FIELDS = (
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
)


def _event(**changes: Any) -> RuntimeDiagnosticEvent:
    values: dict[str, Any] = {
        "occurred_at": datetime(2026, 1, 2, tzinfo=UTC),
        "level": RuntimeDiagnosticLevel.INFO,
        "event_name": "task.started",
        "service": "worker",
        "environment": "test",
        "correlation_id": CorrelationId("corr"),
    }
    values.update(changes)
    return RuntimeDiagnosticEvent(**values)


@pytest.mark.parametrize("value", [None, 1, _TextSubclass("corr"), "   ", ""])
def test_correlation_id_rejects_non_exact_or_blank_values(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        CorrelationId(cast(str, value))


@pytest.mark.parametrize(
    "field",
    ["event_name", "service", "environment"],
)
@pytest.mark.parametrize("value", [None, 1, _TextSubclass("x"), "", " \t "])
def test_required_event_text_rejects_wrong_exact_types_and_blank_values(
    field: str, value: object
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _event(**{field: value})


@pytest.mark.parametrize("field", ["occurred_at", "level", "correlation_id"])
def test_required_event_values_reject_raw_values(field: str) -> None:
    value: object = {
        "occurred_at": datetime(2026, 1, 2),
        "level": "info",
        "correlation_id": "corr",
    }[field]
    with pytest.raises((TypeError, ValueError)):
        _event(**{field: value})


def test_naive_datetime_and_optional_non_exact_identities_are_rejected() -> None:
    with pytest.raises(ValueError):
        _event(occurred_at=datetime(2026, 1, 2))
    with pytest.raises(TypeError):
        _event(occurred_at=_DatetimeSubclass(2026, 1, 2, tzinfo=UTC))
    with pytest.raises(TypeError):
        _event(task_id=_TextSubclass("task"))
    with pytest.raises(TypeError):
        _event(task_id=1)


@pytest.mark.parametrize("field", _IDENTITY_FIELDS)
@pytest.mark.parametrize("value", [1, False, _TextSubclass("id"), "", "  "])
def test_every_optional_identity_rejects_raw_subclass_and_blank_values(
    field: str, value: object
) -> None:
    with pytest.raises((TypeError, ValueError)):
        _event(**{field: value})


def test_all_optional_identities_omit_as_null_and_unknown_payload_is_not_accepted() -> (
    None
):
    encoded = encode_runtime_diagnostic_event(
        _event(
            **dict.fromkeys(
                (
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
                )
            )
        )
    )
    assert all(f'"{field}"' not in encoded for field in _IDENTITY_FIELDS)
    assert set(json.loads(encoded)) == {
        "occurred_at",
        "level",
        "event_name",
        "service",
        "environment",
        "correlation_id",
    }
    for field in (
        "payload",
        "message",
        "headers",
        "url",
        "prompt",
        "source_text",
        "provider_body",
        "exception",
        "stack",
        "locals",
    ):
        with pytest.raises(TypeError):
            RuntimeDiagnosticEvent(
                datetime(2026, 1, 2, tzinfo=UTC),
                RuntimeDiagnosticLevel.INFO,
                "task.started",
                "worker",
                "test",
                CorrelationId("corr"),
                **{field: "secret-marker"},  # type: ignore[call-arg]
            )


def test_opaque_identity_text_is_preserved_without_normalization() -> None:
    encoded = encode_runtime_diagnostic_event(_event(task_id=" opaque-token "))
    assert '"task_id":" opaque-token "' in encoded


def test_event_is_immutable_and_encoder_accepts_only_exact_event_type() -> None:
    event = _event()
    with pytest.raises((AttributeError, TypeError)):
        event.service = "other"  # type: ignore[misc]
    with pytest.raises((AttributeError, TypeError)):
        del event.service  # type: ignore[misc]

    class EventSubclass(RuntimeDiagnosticEvent):
        pass

    with pytest.raises(TypeError):
        encode_runtime_diagnostic_event(
            cast(
                RuntimeDiagnosticEvent,
                EventSubclass(
                    event.occurred_at,
                    event.level,
                    event.event_name,
                    event.service,
                    event.environment,
                    event.correlation_id,
                ),
            )
        )
