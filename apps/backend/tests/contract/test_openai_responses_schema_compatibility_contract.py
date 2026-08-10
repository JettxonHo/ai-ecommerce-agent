"""Contract checks for the private OpenAI schema compatibility boundary."""

from __future__ import annotations

from inspect import Parameter, iscoroutinefunction, signature
from typing import cast, get_type_hints

import pytest

import ai_ecommerce_agent.platform.model_runtime as _runtime_package
from ai_ecommerce_agent import application as application_package
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime import openai_responses
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _schema_compatibility,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

_runtime_package.__dict__.pop("openai_responses", None)

pytestmark = pytest.mark.contract


def _schema(value: object | None = None) -> StructuredContent:
    mapping = (
        value
        if value is not None
        else {
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
            "additionalProperties": False,
        }
    )
    return StructuredContent.from_mapping(cast(dict[str, object], mapping))


def _spec(value: object | None = None) -> StructuredOutputSpec:
    return StructuredOutputSpec("schema", "v1", _schema(value))


class _SpecSubclass(StructuredOutputSpec):
    pass


class _ModelCallIdSubclass(ModelCallId):
    pass


def test_private_facade_and_module_interface_are_exact() -> None:
    facade_exports: object = openai_responses.__dict__["__all__"]
    assert cast(list[str], facade_exports) == []
    assert not hasattr(openai_responses, "ensure_openai_responses_schema_compatible")
    private_exports: object = _schema_compatibility.__dict__["__all__"]
    assert cast(list[str], private_exports) == [
        "ensure_openai_responses_schema_compatible"
    ]
    function = _schema_compatibility.ensure_openai_responses_schema_compatible
    assert list(signature(function).parameters) == [
        "structured_output",
        "model_call_id",
    ]
    assert all(
        parameter.kind is Parameter.KEYWORD_ONLY
        for parameter in signature(function).parameters.values()
    )
    assert get_type_hints(function) == {
        "structured_output": StructuredOutputSpec,
        "model_call_id": ModelCallId,
        "return": type(None),
    }
    assert not iscoroutinefunction(function)
    assert not hasattr(application_package, "ensure_openai_responses_schema_compatible")


def test_exact_input_types_and_safe_error_identity() -> None:
    call_id = ModelCallId("call-1")
    function = _schema_compatibility.ensure_openai_responses_schema_compatible
    with pytest.raises(TypeError):
        function(structured_output={"schema": _spec()}, model_call_id=call_id)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        function(structured_output=None, model_call_id=call_id)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        function(
            structured_output=_SpecSubclass("schema", "v1", _schema()),
            model_call_id=call_id,
        )
    with pytest.raises(TypeError):
        function(structured_output=_spec(), model_call_id="call-1")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        function(
            structured_output=_spec(), model_call_id=_ModelCallIdSubclass("call-1")
        )

    with pytest.raises(ModelRuntimeError) as caught:
        function(
            structured_output=_spec({"type": "string", "secret": "schema-value"}),
            model_call_id=call_id,
        )
    error = caught.value
    assert error.category is ModelRuntimeErrorCategory.INVALID_REQUEST
    assert error.retryability is False
    assert error.model_call_id is call_id
    assert error.provider_metadata is None
    assert error.message == "OpenAI Responses schema is incompatible"
    assert "schema-value" not in repr(error)


def test_compatible_schema_returns_none_without_mutating_supplied_identity() -> None:
    spec = _spec()
    call_id = ModelCallId("call-1")
    before = spec.schema.to_mapping()
    result = _schema_compatibility.ensure_openai_responses_schema_compatible(
        structured_output=spec,
        model_call_id=call_id,
    )
    assert result is None
    assert spec.schema.to_mapping() == before
