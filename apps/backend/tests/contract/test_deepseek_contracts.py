"""Provider-neutral contract checks for the private DeepSeek adapter seam."""

from __future__ import annotations

from inspect import signature

import pytest

import ai_ecommerce_agent.platform.model_runtime as _runtime_package
from ai_ecommerce_agent.application.model_runtime import ModelRuntimePort
from ai_ecommerce_agent.platform.model_runtime.deepseek import (
    _request_preparation,
    _response_mapping,
    _runtime,
)

_runtime_package.__dict__.pop("deepseek", None)

pytestmark = pytest.mark.contract


def test_private_deepseek_package_has_no_public_facade() -> None:
    import ai_ecommerce_agent.platform.model_runtime.deepseek as package

    assert not hasattr(package, "__all__")
    assert package.__doc__ == "Private DeepSeek Chat Completions adapter package."


def test_frozen_provider_identity_and_factory_interfaces_are_exact() -> None:
    assert _runtime.DEEPSEEK_CREDENTIAL_REF == "deepseek_primary"
    assert _runtime.DEEPSEEK_BASE_URL == "https://api.deepseek.com"
    assert _runtime.DEEPSEEK_MODEL == "deepseek-v4-pro"
    assert list(signature(_runtime.create_deepseek_runtime).parameters) == [
        "credential_ref"
    ]
    assert list(signature(_request_preparation.prepare_deepseek_call).parameters) == [
        "request",
        "parameters",
    ]
    assert list(signature(_response_mapping.map_deepseek_response).parameters) == [
        "request",
        "response",
        "provider_attempt_ids",
        "latency_ms",
    ]


def test_runtime_adapter_satisfies_provider_neutral_port_protocol() -> None:
    assert isinstance(_runtime.DeepSeekModelRuntime, ModelRuntimePort)
