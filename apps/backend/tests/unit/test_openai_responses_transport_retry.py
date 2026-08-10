"""Offline coverage for the bounded OpenAI Responses transport retry."""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from email.utils import format_datetime
from typing import Any, cast

import httpx
import openai
import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelExecutionProfile,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    ProviderAttemptId,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _execution,
    request_preparation,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit

_PROFILE = ModelExecutionProfile("profile-1", "v1")
_CALL_ID = ModelCallId("call-1")
_ATTEMPTS = (ProviderAttemptId("attempt-1"), ProviderAttemptId("attempt-2"))


class _AttemptSubclass(ProviderAttemptId):
    pass


class _TupleSubclass(tuple[ProviderAttemptId, ...]):
    pass


def _request() -> ModelCallRequest:
    return ModelCallRequest(
        ModelCallIdentity(_CALL_ID),
        "instruction-marker",
        StructuredContent.from_mapping({"context": ["value"]}),
        StructuredOutputSpec(
            "schema-1",
            "v1",
            StructuredContent.from_mapping(
                {
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                }
            ),
        ),
        _PROFILE,
        ModelCallContractVersions("prompt-1", "v1", "skill-1", "domain-1", "context-1"),
    )


def _parameters() -> request_preparation.OpenAIResponsesCallParameters:
    return request_preparation.OpenAIResponsesCallParameters(
        _PROFILE, request_preparation.OpenAIReasoningEffort.LOW, 32, 19
    )


def _payload(text: str = "mapped output") -> dict[str, object]:
    return {
        "id": "response-id",
        "created_at": 0.0,
        "model": "gpt-5.6-terra",
        "object": "response",
        "output": [
            {
                "id": "message-1",
                "content": [{"annotations": [], "text": text, "type": "output_text"}],
                "role": "assistant",
                "status": "completed",
                "type": "message",
            }
        ],
        "parallel_tool_calls": False,
        "tool_choice": "none",
        "tools": [],
        "status": "completed",
        "usage": {
            "input_tokens": 3,
            "input_tokens_details": {"cache_write_tokens": 0, "cached_tokens": 1},
            "output_tokens": 5,
            "output_tokens_details": {"reasoning_tokens": 2},
            "total_tokens": 8,
        },
    }


def _client(handler: Any) -> openai.OpenAI:
    return openai.OpenAI(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def _error_response(status: int, request_id: str = "error-request") -> httpx.Response:
    return httpx.Response(
        status,
        headers={"x-request-id": request_id},
        json={"error": {"message": "provider detail must stay private"}},
    )


def _success_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, headers={"x-request-id": "success"}, json=_payload())


def _ticks() -> Iterator[float]:
    return iter((90.0, 90.01, 90.02, 90.03, 90.04, 90.05, 90.06))


def _noop_sleep(delay: float) -> None:
    return None


def _traceback_contains_raw_transport_value(value: object, seen: set[int]) -> bool:
    identity = id(value)
    if identity in seen:
        return False
    seen.add(identity)
    if isinstance(value, (openai.OpenAIError, httpx.Response, httpx.Headers)):
        return True
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        return any(
            _traceback_contains_raw_transport_value(item, seen)
            for item in (*mapping.keys(), *mapping.values())
        )
    if isinstance(value, (list, tuple, set, frozenset)):
        items = cast(tuple[object, ...], tuple(cast(Any, value)))
        return any(
            _traceback_contains_raw_transport_value(item, seen) for item in items
        )
    return False


def _assert_no_raw_transport_references(error: BaseException) -> None:
    traceback = error.__traceback__
    while traceback is not None:
        for name, value in traceback.tb_frame.f_locals.items():
            assert not _traceback_contains_raw_transport_value(value, set()), (
                traceback.tb_frame.f_code.co_name,
                name,
                type(value).__name__,
            )
        traceback = traceback.tb_next


def test_eligible_failure_retries_once_with_clipped_timeout_and_same_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(
                500,
                headers={"x-request-id": "first-request"},
                json={"error": {"message": "temporary"}},
            )
        return httpx.Response(
            200,
            headers={"x-request-id": "second-request"},
            json=_payload(),
        )

    ticks = iter((90.0, 90.01, 90.02, 90.03, 90.04, 90.05, 90.06))
    sleeps: list[float] = []
    monkeypatch.setattr(_execution, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    monkeypatch.setattr(_execution, "random", lambda: 0.5)
    client = _client(handler)

    result = _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )

    assert len(calls) == 2
    assert json.loads(calls[0].content) == json.loads(calls[1].content)
    assert calls[0].extensions["timeout"] == {
        "connect": 10.0,
        "read": 10.0,
        "write": 10.0,
        "pool": 10.0,
    }
    assert calls[1].extensions["timeout"] == pytest.approx(
        {"connect": 9.96, "read": 9.96, "write": 9.96, "pool": 9.96}
    )
    assert sleeps == [1.0]
    assert cast(Any, result).provider_metadata.provider_attempt_ids == _ATTEMPTS
    assert cast(Any, result).provider_metadata.provider_request_id == "second-request"
    client.close()


def test_first_success_uses_only_first_id_and_preserves_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, headers={"x-request-id": "first"}, json=_payload())

    sleeps: list[float] = []
    clock = _ticks()
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    request = _request()
    parameters = _parameters()
    client = _client(handler)
    result = _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=request,
        parameters=parameters,
        provider_attempt_ids=(_ATTEMPTS[0],),
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )
    assert len(calls) == 1
    assert sleeps == []
    metadata = cast(Any, result).provider_metadata
    assert metadata.provider_attempt_ids == (_ATTEMPTS[0],)
    assert metadata.provider_attempt_ids[0] is _ATTEMPTS[0]
    assert request.execution_profile is _PROFILE
    assert parameters.execution_profile is _PROFILE
    assert client.max_retries == 0
    client.close()


@pytest.mark.parametrize("status", [408, 409, 429, 500, 503])
def test_each_eligible_status_can_retry_once(
    status: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return (
            _error_response(status)
            if len(calls) == 1
            else httpx.Response(
                200, headers={"x-request-id": "success"}, json=_payload()
            )
        )

    clock = _ticks()
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", _noop_sleep)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    client = _client(handler)
    result = _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )
    assert len(calls) == 2
    assert cast(Any, result).provider_metadata.provider_attempt_ids == _ATTEMPTS
    client.close()


@pytest.mark.parametrize("status", [408, 409, 429, 500])
def test_eligible_second_failure_maps_current_attempt(
    status: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _error_response(status, f"request-{len(calls)}")

    clock = _ticks()
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", _noop_sleep)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=1_000_000_000_000.0,
            fallback_retry_delay_seconds=2.0,
        )
    error = caught.value
    assert len(calls) == 2
    assert error.provider_metadata is not None
    assert error.provider_metadata.provider_attempt_ids == _ATTEMPTS
    assert error.provider_metadata.provider_request_id == "request-2"
    assert "provider detail" not in error.message
    assert error.__cause__ is None
    assert error.__context__ is None
    client.close()


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
def test_noneligible_status_does_not_consume_second_attempt(
    status: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _error_response(status)

    sleeps: list[float] = []
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=1_000_000_000_000.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert calls == 1
    assert sleeps == []
    assert caught.value.retryability is False
    assert caught.value.provider_metadata is not None
    assert caught.value.provider_metadata.provider_attempt_ids == (_ATTEMPTS[0],)
    client.close()


@pytest.mark.parametrize("transport_error", ["connection", "timeout"])
def test_connection_and_timeout_failures_retry(
    transport_error: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            if transport_error == "connection":
                raise httpx.ConnectError("temporary", request=request)
            raise httpx.ReadTimeout("temporary", request=request)
        return httpx.Response(200, headers={"x-request-id": "success"}, json=_payload())

    clock = _ticks()
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", _noop_sleep)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    client = _client(handler)
    result = _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )
    assert calls == 2
    assert cast(Any, result).provider_metadata.provider_attempt_ids == _ATTEMPTS
    client.close()


@pytest.mark.parametrize("transport_error", ["connection", "timeout"])
def test_connection_and_timeout_second_failure_maps_safe_metadata(
    transport_error: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if transport_error == "connection":
            raise httpx.ConnectError(f"temporary-{calls}", request=request)
        raise httpx.ReadTimeout(f"temporary-{calls}", request=request)

    clock = _ticks()
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", _noop_sleep)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=100.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert calls == 2
    assert caught.value.provider_metadata is not None
    assert caught.value.provider_metadata.provider_attempt_ids == _ATTEMPTS
    assert caught.value.provider_metadata.provider_request_id is None
    _assert_no_raw_transport_references(caught.value)
    client.close()


def test_one_supplied_id_never_sleeps_or_consumes_second_attempt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _error_response(500)

    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=(_ATTEMPTS[0],),
            overall_deadline_monotonic=1_000_000_000_000.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert calls == 1
    assert sleeps == []
    _assert_no_raw_transport_references(caught.value)
    client.close()


@pytest.mark.parametrize("header_value", ["true", "false"])
def test_x_should_retry_header_does_not_change_raw_eligibility(
    header_value: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(
                500,
                headers={"x-should-retry": header_value},
                json={"error": {"message": "temporary"}},
            )
        return httpx.Response(200, headers={"x-request-id": "success"}, json=_payload())

    monkeypatch.setattr(_execution, "monotonic", lambda: next(_ticks()))
    monkeypatch.setattr(_execution, "sleep", _noop_sleep)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    client = _client(handler)
    _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )
    assert len(calls) == 2
    client.close()


@pytest.mark.parametrize("outcome", ["refusal", "incomplete", "invalid_candidate"])
def test_mapped_outcomes_never_retry(
    outcome: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0
    payload = _payload()
    if outcome == "refusal":
        payload["output"] = [
            {
                "id": "message-1",
                "content": [
                    {"annotations": [], "refusal": "not allowed", "type": "refusal"}
                ],
                "role": "assistant",
                "status": "completed",
                "type": "message",
            }
        ]
    elif outcome == "incomplete":
        payload["status"] = "incomplete"
        payload["incomplete_details"] = {"reason": "max_output_tokens"}
        payload["output"] = []
    else:
        payload["output"] = [
            {
                "id": "message-1",
                "content": [{"annotations": [], "text": "", "type": "output_text"}],
                "role": "assistant",
                "status": "completed",
                "type": "message",
            }
        ]

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, json=payload)

    def fail_sleep(delay: float) -> None:
        pytest.fail("retry")

    monkeypatch.setattr(_execution, "sleep", fail_sleep)
    client = _client(handler)
    with pytest.raises(ModelRuntimeError):
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=1_000_000_000_000.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert calls == 1
    client.close()


def test_two_attempt_metadata_preserves_tuple_member_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return (
            _error_response(500)
            if len(calls) == 1
            else httpx.Response(
                200, headers={"x-request-id": "success"}, json=_payload()
            )
        )

    monkeypatch.setattr(_execution, "monotonic", lambda: next(_ticks()))
    monkeypatch.setattr(_execution, "sleep", _noop_sleep)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    client = _client(handler)
    result = _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )
    attempts = cast(Any, result).provider_metadata.provider_attempt_ids
    assert attempts[0] is _ATTEMPTS[0]
    assert attempts[1] is _ATTEMPTS[1]
    client.close()


@pytest.mark.parametrize("mode", ["single", "retry_first", "retry_second"])
def test_final_mapped_traceback_has_no_raw_transport_objects(
    mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _error_response(500, f"request-{calls}")

    monkeypatch.setattr(_execution, "sleep", _noop_sleep)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    if mode != "single":
        monkeypatch.setattr(_execution, "monotonic", lambda: next(_ticks()))
    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        if mode == "single":
            _execution.execute_openai_responses_attempt(
                client=client,
                request=_request(),
                parameters=_parameters(),
                provider_attempt_ids=_ATTEMPTS,
            )
        else:
            _execution.execute_openai_responses_with_transport_retry(
                client=client,
                request=_request(),
                parameters=_parameters(),
                provider_attempt_ids=(
                    (_ATTEMPTS[0],) if mode == "retry_first" else _ATTEMPTS
                ),
                overall_deadline_monotonic=1_000_000_000_000.0,
                fallback_retry_delay_seconds=2.0,
            )
    assert calls == (1 if mode == "retry_first" else 2 if mode == "retry_second" else 1)
    _assert_no_raw_transport_references(caught.value)
    client.close()


@pytest.mark.parametrize("error_kind", ["validation", "api", "base"])
def test_generic_openai_errors_are_mapped_but_never_retried(
    error_kind: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = httpx.Request("POST", "https://example.test")
    if error_kind == "validation":
        error: openai.OpenAIError = openai.APIResponseValidationError(
            httpx.Response(200, request=request), {"secret": "body"}
        )
    elif error_kind == "api":
        error = openai.APIError("secret", request, body={"secret": "body"})
    else:
        error = openai.OpenAIError("secret")
    calls = 0

    def raise_error(**kwargs: object) -> object:
        nonlocal calls
        calls += 1
        raise error

    client = _client(_success_handler)
    monkeypatch.setattr(cast(Any, client.responses), "create", raise_error)
    with pytest.raises(ModelRuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=1_000_000_000_000.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert calls == 1
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.retryability is True
    assert caught.value.provider_metadata is not None
    assert caught.value.provider_metadata.provider_attempt_ids == (_ATTEMPTS[0],)
    assert "secret" not in caught.value.message
    client.close()


@pytest.mark.parametrize(
    ("value", "error_type"),
    [
        (None, TypeError),
        (1, TypeError),
        (True, TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (float("-inf"), ValueError),
    ],
)
def test_deadline_type_and_finiteness_boundaries(
    value: object, error_type: type[Exception]
) -> None:
    client = _client(_success_handler)
    with pytest.raises(error_type):
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=cast(float, value),
            fallback_retry_delay_seconds=2.0,
        )
    client.close()


@pytest.mark.parametrize(
    ("value", "error_type"),
    [
        (None, TypeError),
        (1, TypeError),
        (True, TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (0.0, ValueError),
        (-1.0, ValueError),
    ],
)
def test_fallback_delay_type_finiteness_and_positivity_boundaries(
    value: object, error_type: type[Exception]
) -> None:
    client = _client(_success_handler)
    with pytest.raises(error_type):
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=100.0,
            fallback_retry_delay_seconds=cast(float, value),
        )
    client.close()


@pytest.mark.parametrize(
    ("attempts", "error_type"),
    [
        (None, TypeError),
        ([], TypeError),
        (_TupleSubclass(_ATTEMPTS), TypeError),
        ((object(),), TypeError),
        ((_AttemptSubclass("bad"),), TypeError),
        ((), TypeError),
        ((_ATTEMPTS[0], _ATTEMPTS[1], ProviderAttemptId("third")), ValueError),
        ((ProviderAttemptId("same"), ProviderAttemptId("same")), ValueError),
    ],
)
def test_attempt_id_tuple_boundaries(
    attempts: object, error_type: type[Exception]
) -> None:
    client = _client(_success_handler)
    with pytest.raises(error_type):
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=cast(tuple[ProviderAttemptId, ...], attempts),
            overall_deadline_monotonic=100.0,
            fallback_retry_delay_seconds=2.0,
        )
    client.close()


def test_past_finite_deadline_prepares_before_zero_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    original_prepare = request_preparation.prepare_openai_responses_call

    def prepare(*, request: ModelCallRequest, parameters: object) -> object:
        events.append("prepare")
        prepared = original_prepare(request=request, parameters=cast(Any, parameters))

        class _Body:
            def to_mapping(self) -> object:
                events.append("to_mapping")
                return prepared.request_body.to_mapping()

        return type(
            "PreparedProxy",
            (),
            {"request_body": _Body(), "timeout_seconds": prepared.timeout_seconds},
        )()

    monkeypatch.setattr(_execution, "prepare_openai_responses_call", prepare)
    monkeypatch.setattr(
        _execution, "monotonic", lambda: events.append("clock") or 100.0
    )
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _success_handler(request)

    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=99.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert events == ["prepare", "to_mapping", "clock"]
    assert calls == 0
    assert caught.value.category is ModelRuntimeErrorCategory.TRANSIENT_PROVIDER_FAILURE
    assert caught.value.provider_metadata is None
    client.close()


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ({"retry-after-ms": "2500"}, 2.5),
        ({"Retry-After": "3.5"}, 3.5),
        (
            {
                "Retry-After": format_datetime(
                    datetime.fromtimestamp(103.0, tz=UTC), usegmt=True
                )
            },
            3.0,
        ),
        ({"retry-after-ms": "2500", "Retry-After": "8"}, 2.5),
    ],
)
def test_retry_after_precedence_and_http_date(
    headers: dict[str, str], expected: float, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return (
            httpx.Response(500, headers=headers, json={"error": {}})
            if len(calls) == 1
            else httpx.Response(
                200, headers={"x-request-id": "success"}, json=_payload()
            )
        )

    clock = _ticks()
    sleeps: list[float] = []
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    monkeypatch.setattr(_execution, "time", lambda: 100.0)
    client = _client(handler)
    _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=20.0,
    )
    assert sleeps == [expected]
    assert len(calls) == 2
    client.close()


@pytest.mark.parametrize(
    "header",
    ["not-a-date", "0", "-2", "nan", "inf", "Wed, 21 Oct 2015 07:28:00"],
)
def test_malformed_past_nonfinite_and_naive_retry_after_use_jitter(
    header: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return (
            httpx.Response(500, headers={"Retry-After": header}, json={"error": {}})
            if len(calls) == 1
            else httpx.Response(
                200, headers={"x-request-id": "success"}, json=_payload()
            )
        )

    clock = _ticks()
    sleeps: list[float] = []
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    monkeypatch.setattr(_execution, "time", lambda: 100.0)
    client = _client(handler)
    _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )
    assert sleeps == [0.5]
    assert len(calls) == 2
    client.close()


def test_server_delay_beyond_deadline_keeps_first_error_without_sleep(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            500,
            headers={"Retry-After": "5"},
            json={"error": {"message": "temporary"}},
        )

    clock = iter((90.0, 90.01, 90.02, 90.03))
    sleeps: list[float] = []
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    client = _client(handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=92.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert calls == 1
    assert sleeps == []
    assert caught.value.provider_metadata is not None
    assert caught.value.provider_metadata.provider_attempt_ids == (_ATTEMPTS[0],)
    client.close()


@pytest.mark.parametrize(
    ("random_value", "expected_calls", "expected_sleep"),
    [(0.25, 2, [0.5]), (0.75, 1, [])],
)
def test_deadline_compares_actual_jittered_delay(
    random_value: float,
    expected_calls: int,
    expected_sleep: list[float],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return (
            _error_response(500)
            if len(calls) == 1
            else httpx.Response(
                200, headers={"x-request-id": "success"}, json=_payload()
            )
        )

    clock = iter((90.0, 90.01, 90.02, 90.03, 90.04, 90.05, 90.06))
    sleeps: list[float] = []
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    monkeypatch.setattr(_execution, "random", lambda: random_value)
    client = _client(handler)
    if expected_calls == 2:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=91.0,
            fallback_retry_delay_seconds=2.0,
        )
    else:
        with pytest.raises(ModelRuntimeError):
            _execution.execute_openai_responses_with_transport_retry(
                client=client,
                request=_request(),
                parameters=_parameters(),
                provider_attempt_ids=_ATTEMPTS,
                overall_deadline_monotonic=91.0,
                fallback_retry_delay_seconds=2.0,
            )
    assert len(calls) == expected_calls
    assert sleeps == expected_sleep
    client.close()


def test_deadline_exhaustion_after_one_sleep_keeps_first_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return _error_response(500)

    clock = iter((90.0, 90.01, 90.02, 90.03, 91.0))
    sleeps: list[float] = []
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    client = _client(handler)
    with pytest.raises(ModelRuntimeError):
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=91.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert calls == 1
    assert sleeps == [0.5]
    client.close()


def test_preparation_and_materialization_happen_once_before_clock_and_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    original_prepare = request_preparation.prepare_openai_responses_call

    def prepare(*, request: ModelCallRequest, parameters: object) -> object:
        events.append("prepare")
        prepared = original_prepare(request=request, parameters=cast(Any, parameters))

        class _Body:
            def to_mapping(self) -> object:
                events.append("to_mapping")
                return prepared.request_body.to_mapping()

        return type(
            "PreparedProxy",
            (),
            {"request_body": _Body(), "timeout_seconds": prepared.timeout_seconds},
        )()

    monkeypatch.setattr(_execution, "prepare_openai_responses_call", prepare)
    clock = iter((90.0, 90.01, 90.02, 90.03, 90.04, 90.05, 90.06))
    monkeypatch.setattr(
        _execution, "monotonic", lambda: events.append("clock") or next(clock)
    )

    def record_sleep(delay: float) -> None:
        events.append("sleep")

    monkeypatch.setattr(_execution, "sleep", record_sleep)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)

    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        events.append("create")
        return (
            _error_response(500)
            if calls == 1
            else httpx.Response(
                200, headers={"x-request-id": "success"}, json=_payload()
            )
        )

    client = _client(handler)
    _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )
    assert events[:3] == ["prepare", "to_mapping", "clock"]
    assert events.count("prepare") == 1
    assert events.count("to_mapping") == 1
    assert events.count("create") == 2
    assert events.count("sleep") == 1
    client.close()


def test_retry_after_timestamp_oserror_uses_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return (
            httpx.Response(
                500,
                headers={"Retry-After": "Thu, 01 Jan 1970 00:01:43 GMT"},
                json={"error": {}},
            )
            if len(calls) == 1
            else httpx.Response(
                200, headers={"x-request-id": "success"}, json=_payload()
            )
        )

    clock = _ticks()
    sleeps: list[float] = []
    monkeypatch.setattr(_execution, "monotonic", lambda: next(clock))
    monkeypatch.setattr(_execution, "sleep", sleeps.append)
    monkeypatch.setattr(_execution, "random", lambda: 0.25)
    monkeypatch.setattr(_execution, "time", lambda: 100.0)

    def fail_parse(value: str) -> datetime:
        raise OSError("timestamp unavailable")

    monkeypatch.setattr(_execution, "parsedate_to_datetime", fail_parse)
    client = _client(handler)
    _execution.execute_openai_responses_with_transport_retry(
        client=client,
        request=_request(),
        parameters=_parameters(),
        provider_attempt_ids=_ATTEMPTS,
        overall_deadline_monotonic=100.0,
        fallback_retry_delay_seconds=2.0,
    )
    assert sleeps == [0.5]
    assert len(calls) == 2
    client.close()


def test_unknown_transport_and_preparation_errors_propagate_by_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    marker = RuntimeError("transport marker")
    client = _client(_success_handler)

    def raise_marker(**kwargs: object) -> object:
        raise marker

    monkeypatch.setattr(cast(Any, client.responses), "create", raise_marker)
    with pytest.raises(RuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=1_000_000_000_000.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert caught.value is marker
    client.close()

    prepare_marker = ModelRuntimeError(
        ModelRuntimeErrorCategory.INVALID_REQUEST, "prepare marker", False, _CALL_ID
    )

    def fail_prepare(*, request: ModelCallRequest, parameters: object) -> object:
        raise prepare_marker

    monkeypatch.setattr(_execution, "prepare_openai_responses_call", fail_prepare)
    client = _client(_success_handler)
    with pytest.raises(ModelRuntimeError) as caught:
        _execution.execute_openai_responses_with_transport_retry(
            client=client,
            request=_request(),
            parameters=_parameters(),
            provider_attempt_ids=_ATTEMPTS,
            overall_deadline_monotonic=1_000_000_000_000.0,
            fallback_retry_delay_seconds=2.0,
        )
    assert caught.value is prepare_marker
    client.close()
