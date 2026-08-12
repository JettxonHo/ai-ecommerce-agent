"""Contract tests for the provider-neutral runtime error value seam."""

from __future__ import annotations

import inspect
from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from typing import Any, get_type_hints

import pytest

from ai_ecommerce_agent.application import runtime_errors
from ai_ecommerce_agent.application.runtime_diagnostics import (
    CorrelationId,
    RuntimeDiagnosticEvent,
    RuntimeDiagnosticLevel,
)
from ai_ecommerce_agent.shared_kernel import ResourceReference, RunId, TaskId

pytestmark = pytest.mark.contract


def test_facade_and_catalogs_are_exact() -> None:
    assert runtime_errors.__all__ == [
        "ErrorId",
        "RuntimeErrorCategory",
        "RuntimeErrorRetryability",
        "RuntimeErrorDisposition",
        "RuntimeErrorIdentity",
        "RuntimeErrorRecord",
        "runtime_error_to_diagnostic_event",
    ]
    assert list(runtime_errors.RuntimeErrorCategory) == [
        runtime_errors.RuntimeErrorCategory.TRANSIENT_INFRASTRUCTURE_ERROR,
        runtime_errors.RuntimeErrorCategory.RATE_LIMIT_ERROR,
        runtime_errors.RuntimeErrorCategory.TIMEOUT_ERROR,
        runtime_errors.RuntimeErrorCategory.STRUCTURED_OUTPUT_ERROR,
        runtime_errors.RuntimeErrorCategory.VALIDATION_ERROR,
        runtime_errors.RuntimeErrorCategory.PERMISSION_OR_AUTHENTICATION_ERROR,
        runtime_errors.RuntimeErrorCategory.DATA_INTEGRITY_ERROR,
        runtime_errors.RuntimeErrorCategory.DEPENDENCY_CONFIGURATION_ERROR,
        runtime_errors.RuntimeErrorCategory.PROVIDER_CONTENT_REJECTION,
        runtime_errors.RuntimeErrorCategory.CANCELLATION,
    ]
    assert [member.value for member in runtime_errors.RuntimeErrorCategory] == [
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
    ]
    assert [member.value for member in runtime_errors.RuntimeErrorRetryability] == [
        "retryable",
        "conditionally_retryable",
        "non_retryable",
        "unknown",
    ]
    assert [member.value for member in runtime_errors.RuntimeErrorDisposition] == [
        "retry",
        "fallback",
        "wait",
        "pause",
        "fail",
        "cancel",
        "manual_recovery",
    ]


@pytest.mark.parametrize(
    "value_type",
    [
        runtime_errors.ErrorId,
        runtime_errors.RuntimeErrorIdentity,
        runtime_errors.RuntimeErrorRecord,
    ],
)
def test_value_types_are_frozen_slotted_and_exactly_ordered(
    value_type: type[Any],
) -> None:
    assert is_dataclass(value_type)
    params = value_type.__dataclass_params__  # type: ignore[attr-defined]
    slots = value_type.__slots__  # type: ignore[attr-defined]
    assert params.frozen is True  # type: ignore[attr-defined]
    assert slots
    assert "__dict__" not in slots

    fields_by_type = {
        runtime_errors.ErrorId: ["value"],
        runtime_errors.RuntimeErrorIdentity: [
            "error_id",
            "correlation_id",
            "task_id",
            "run_id",
            "skill_run_id",
            "node_execution_id",
            "attempt_id",
        ],
        runtime_errors.RuntimeErrorRecord: [
            "identity",
            "error_category",
            "severity",
            "retryability",
            "disposition",
            "component",
            "user_safe_message",
            "operator_summary",
            "provider_request_reference",
            "provider_response_reference",
            "first_occurred_at",
            "last_occurred_at",
            "remediation_options",
        ],
    }
    expected_fields = next(
        expected
        for known_type, expected in fields_by_type.items()
        if value_type is known_type
    )
    assert [field.name for field in fields(value_type)] == expected_fields


def test_exact_annotations_signatures_and_projection_annotation() -> None:
    assert get_type_hints(runtime_errors.ErrorId) == {"value": str}
    assert get_type_hints(runtime_errors.RuntimeErrorIdentity) == {
        "error_id": runtime_errors.ErrorId,
        "correlation_id": CorrelationId,
        "task_id": TaskId,
        "run_id": RunId,
        "skill_run_id": str | None,
        "node_execution_id": str | None,
        "attempt_id": str | None,
    }
    assert get_type_hints(runtime_errors.RuntimeErrorRecord) == {
        "identity": runtime_errors.RuntimeErrorIdentity,
        "error_category": runtime_errors.RuntimeErrorCategory,
        "severity": RuntimeDiagnosticLevel,
        "retryability": runtime_errors.RuntimeErrorRetryability,
        "disposition": runtime_errors.RuntimeErrorDisposition,
        "component": str,
        "user_safe_message": str,
        "operator_summary": str,
        "provider_request_reference": ResourceReference | None,
        "provider_response_reference": ResourceReference | None,
        "first_occurred_at": datetime,
        "last_occurred_at": datetime,
        "remediation_options": tuple[str, ...],
    }
    projection = inspect.signature(runtime_errors.runtime_error_to_diagnostic_event)
    assert list(projection.parameters) == ["record", "service", "environment"]
    assert projection.parameters["service"].kind is inspect.Parameter.KEYWORD_ONLY
    assert projection.parameters["environment"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_type_hints(runtime_errors.runtime_error_to_diagnostic_event) == {
        "record": runtime_errors.RuntimeErrorRecord,
        "service": str,
        "environment": str,
        "return": RuntimeDiagnosticEvent,
    }


def test_identity_creation_is_application_owned_and_projection_is_directly_typed() -> (
    None
):
    generated = runtime_errors.ErrorId.new()
    assert type(generated) is runtime_errors.ErrorId
    assert generated.value
    assert generated != runtime_errors.ErrorId.new()

    identity = runtime_errors.RuntimeErrorIdentity(
        generated,
        CorrelationId("corr"),
        TaskId("task"),
        RunId("run"),
    )
    record = runtime_errors.RuntimeErrorRecord(
        identity,
        runtime_errors.RuntimeErrorCategory.TIMEOUT_ERROR,
        RuntimeDiagnosticLevel.ERROR,
        runtime_errors.RuntimeErrorRetryability.RETRYABLE,
        runtime_errors.RuntimeErrorDisposition.RETRY,
        "worker",
        "safe",
        "operator",
        None,
        None,
        datetime(2026, 1, 1, tzinfo=UTC),
        datetime(2026, 1, 1, 1, tzinfo=UTC),
    )
    event = runtime_errors.runtime_error_to_diagnostic_event(
        record, service="svc", environment="prod"
    )
    assert type(event) is RuntimeDiagnosticEvent
