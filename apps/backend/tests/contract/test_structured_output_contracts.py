"""Public contract tests for the Structured Output Gate."""

from __future__ import annotations

from inspect import Parameter, iscoroutinefunction, signature
from typing import get_type_hints

import pytest

from ai_ecommerce_agent import application as application_package
from ai_ecommerce_agent.application import model_runtime
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallContractVersions,
    ModelCallId,
    ModelCallIdentity,
    ModelCallRequest,
    ModelCallResult,
    ModelExecutionProfile,
    ModelOutputEnvelope,
    ModelRecoveryKind,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    ModelRuntimePort,
    ModelRuntimeVersionTuple,
    ModelTokenUsage,
    ProviderAttemptId,
    ProviderCallMetadata,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.application.structured_output import (
    parse_and_validate_structured_output,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.contract


_MODEL_RUNTIME_PUBLIC = [
    "ModelCallContractVersions",
    "ModelCallId",
    "ModelCallIdentity",
    "ModelCallRequest",
    "ModelCallResult",
    "ModelExecutionProfile",
    "ModelOutputEnvelope",
    "ModelRecoveryKind",
    "ModelRuntimeError",
    "ModelRuntimeErrorCategory",
    "ModelRuntimePort",
    "ModelRuntimeVersionTuple",
    "ModelTokenUsage",
    "ProviderAttemptId",
    "ProviderCallMetadata",
    "StructuredOutputSpec",
]


class _ResultSubclass(ModelCallResult):
    pass


class _SpecSubclass(StructuredOutputSpec):
    pass


def _schema_content() -> StructuredContent:
    return StructuredContent.from_mapping(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {"value": {"type": "string"}},
            "required": ["value"],
            "additionalProperties": False,
        }
    )


def _result(
    *, schema_id: str = "schema-1", schema_version: str = "v1"
) -> ModelCallResult:
    model_call_id = ModelCallId("call-1")
    versions = ModelRuntimeVersionTuple(
        "provider",
        "responses",
        "sdk",
        "configured",
        None,
        "prompt",
        "v1",
        schema_id,
        schema_version,
        "skill",
        "domain",
        "profile",
        "v1",
        "context",
    )
    metadata = ProviderCallMetadata(
        model_call_id,
        (ProviderAttemptId("attempt-1"),),
        versions,
        "response-1",
        None,
        ModelTokenUsage(1, 2, 3),
        1,
    )
    return ModelCallResult(ModelOutputEnvelope('{"value":"ok"}'), metadata)


def _spec(
    *, schema_id: str = "schema-1", schema_version: str = "v1"
) -> StructuredOutputSpec:
    return StructuredOutputSpec(schema_id, schema_version, _schema_content())


def test_structured_output_facade_has_exact_symbol_and_identity() -> None:
    from ai_ecommerce_agent.application import structured_output

    assert structured_output.__all__ == ["parse_and_validate_structured_output"]
    assert structured_output.__all__.count("parse_and_validate_structured_output") == 1
    assert (
        structured_output.parse_and_validate_structured_output
        is parse_and_validate_structured_output
    )
    public_names = {
        name
        for name in structured_output.__dict__
        if not name.startswith("_") and name != "annotations"
    }
    assert public_names == {"parse_and_validate_structured_output"}
    assert not hasattr(application_package, "parse_and_validate_structured_output")


def test_signature_is_exact_keyword_only_synchronous_and_typed() -> None:
    function_signature = signature(parse_and_validate_structured_output)
    assert list(function_signature.parameters) == ["result", "spec"]
    assert all(
        parameter.kind is Parameter.KEYWORD_ONLY
        for parameter in function_signature.parameters.values()
    )
    assert get_type_hints(parse_and_validate_structured_output) == {
        "result": ModelCallResult,
        "spec": StructuredOutputSpec,
        "return": StructuredContent,
    }
    assert not iscoroutinefunction(parse_and_validate_structured_output)


def test_existing_model_runtime_facade_is_unchanged() -> None:
    assert model_runtime.__all__ == _MODEL_RUNTIME_PUBLIC
    assert [getattr(model_runtime, name) for name in _MODEL_RUNTIME_PUBLIC] == [
        ModelCallContractVersions,
        ModelCallId,
        ModelCallIdentity,
        ModelCallRequest,
        ModelCallResult,
        ModelExecutionProfile,
        ModelOutputEnvelope,
        ModelRecoveryKind,
        ModelRuntimeError,
        ModelRuntimeErrorCategory,
        ModelRuntimePort,
        ModelRuntimeVersionTuple,
        ModelTokenUsage,
        ProviderAttemptId,
        ProviderCallMetadata,
        StructuredOutputSpec,
    ]
    assert all(not hasattr(application_package, name) for name in _MODEL_RUNTIME_PUBLIC)


def test_result_and_spec_require_exact_runtime_types() -> None:
    result = _result()
    spec = _spec()
    with pytest.raises(TypeError):
        parse_and_validate_structured_output(result={"result": result}, spec=spec)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        parse_and_validate_structured_output(result=None, spec=spec)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        parse_and_validate_structured_output(
            result=_ResultSubclass(result.output_envelope, result.provider_metadata),
            spec=spec,
        )
    with pytest.raises(TypeError):
        parse_and_validate_structured_output(result=result, spec={"spec": spec})  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        parse_and_validate_structured_output(result=result, spec=None)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        parse_and_validate_structured_output(
            result=result,
            spec=_SpecSubclass(
                spec.output_schema_id, spec.output_schema_version, spec.schema
            ),
        )
