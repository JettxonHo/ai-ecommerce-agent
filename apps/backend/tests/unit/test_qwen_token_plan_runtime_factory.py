"""Tests-first contract for the private Qwen Token Plan factory."""

from __future__ import annotations

import openai
import pytest

from ai_ecommerce_agent.platform.model_runtime.qwen_token_plan._runtime import (
    QWEN_TOKEN_PLAN_CREDENTIAL_REF,
    QwenTokenPlanConfigurationError,
    create_qwen_token_plan_runtime,
)

pytestmark = pytest.mark.unit
_SECRET_FAILURE_MARKER = "synthetic-qwen-secret-marker"


def test_missing_or_blank_secret_fails_before_sdk_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("QWEN_TOKEN_PLAN_API_KEY", raising=False)
    constructor_called = False

    def forbidden_constructor(*_args: object, **_kwargs: object) -> None:
        nonlocal constructor_called
        constructor_called = True
        raise AssertionError("SDK constructor must not run for a blank Secret")

    monkeypatch.setattr(openai, "OpenAI", forbidden_constructor)
    with pytest.raises(QwenTokenPlanConfigurationError) as caught:
        create_qwen_token_plan_runtime(
            credential_ref=QWEN_TOKEN_PLAN_CREDENTIAL_REF,
        )
    assert str(caught.value) == "Qwen Token Plan configuration/access failure"
    assert not constructor_called


@pytest.mark.parametrize("secret", ["", " ", "\t\n"])
def test_blank_secret_variants_fail_without_client_or_network(
    monkeypatch: pytest.MonkeyPatch,
    secret: str,
) -> None:
    monkeypatch.setenv("QWEN_TOKEN_PLAN_API_KEY", secret)
    constructor_called = False

    def forbidden_constructor(*_args: object, **_kwargs: object) -> None:
        nonlocal constructor_called
        constructor_called = True
        raise AssertionError("blank Secret must fail before client construction")

    monkeypatch.setattr(openai, "OpenAI", forbidden_constructor)
    with pytest.raises(QwenTokenPlanConfigurationError):
        create_qwen_token_plan_runtime()
    assert not constructor_called


def test_credential_reference_is_exact_and_has_no_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QWEN_TOKEN_PLAN_API_KEY", "test-key")
    with pytest.raises(ValueError, match="qwen_token_plan_supplemental"):
        create_qwen_token_plan_runtime(credential_ref="other")


def test_factory_uses_exact_sync_client_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QWEN_TOKEN_PLAN_API_KEY", "test-key")
    runtime = create_qwen_token_plan_runtime()
    try:
        assert type(runtime).__name__ == "QwenTokenPlanModelRuntime"
        assert runtime.sdk_max_retries == 0
    finally:
        runtime.close()


def test_constructor_failure_traceback_does_not_retain_secret_marker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QWEN_TOKEN_PLAN_API_KEY", _SECRET_FAILURE_MARKER)

    def raising_constructor(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError(_SECRET_FAILURE_MARKER)

    monkeypatch.setattr(openai, "OpenAI", raising_constructor)
    with pytest.raises(QwenTokenPlanConfigurationError) as caught:
        create_qwen_token_plan_runtime()

    traceback = caught.value.__traceback__
    assert traceback is not None
    while traceback is not None:
        assert all(
            not (isinstance(value, str) and _SECRET_FAILURE_MARKER in value)
            for value in traceback.tb_frame.f_locals.values()
        ), traceback.tb_frame.f_code.co_name
        traceback = traceback.tb_next
