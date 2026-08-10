"""Behavior tests for pure Structured Output parsing and validation."""

from __future__ import annotations

import socket
from typing import cast

import pytest

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId,
    ModelCallResult,
    ModelOutputEnvelope,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
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

pytestmark = pytest.mark.unit


def _schema(values: dict[str, object] | None = None) -> StructuredContent:
    schema: dict[str, object] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sku": {"type": "string"},
                        "quantity": {"type": "integer"},
                    },
                    "required": ["sku", "quantity"],
                    "additionalProperties": False,
                },
            },
            "email": {"type": "string", "format": "email"},
            "status": {"enum": ["ready", "pending"]},
        },
        "required": ["title", "items", "email", "status"],
        "additionalProperties": False,
    }
    if values:
        schema.update(values)
    return StructuredContent.from_mapping(schema)


def _spec(
    schema: StructuredContent | None = None,
    *,
    schema_id: str = "schema-1",
    schema_version: str = "v1",
) -> StructuredOutputSpec:
    return StructuredOutputSpec(schema_id, schema_version, schema or _schema())


def _result(
    payload: str = (
        '{"title":"Bag","items":[{"sku":"a","quantity":2},'
        '{"sku":"b","quantity":1}],"email":"a@example.com",'
        '"status":"ready"}'
    ),
    *,
    schema_id: str = "schema-1",
    schema_version: str = "v1",
) -> ModelCallResult:
    model_call_id = ModelCallId("call-1")
    version_tuple = ModelRuntimeVersionTuple(
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
        version_tuple,
        "response-1",
        None,
        ModelTokenUsage(1, 2, 3),
        1,
    )
    return ModelCallResult(ModelOutputEnvelope(payload), metadata)


def _assert_error(
    result: ModelCallResult,
    spec: StructuredOutputSpec,
    category: ModelRuntimeErrorCategory,
    *,
    markers: tuple[str, ...] = (),
) -> ModelRuntimeError:
    with pytest.raises(ModelRuntimeError) as caught:
        parse_and_validate_structured_output(result=result, spec=spec)
    error = caught.value
    assert error.category is category
    assert error.retryability is False
    assert error.model_call_id is result.provider_metadata.model_call_id
    assert error.provider_metadata is result.provider_metadata
    assert error.message
    for marker in markers:
        assert marker not in error.message
    return error


def test_valid_nested_object_and_array_roundtrip_is_immutable_and_deterministic() -> (
    None
):
    result = _result()
    spec = _spec()
    first = parse_and_validate_structured_output(result=result, spec=spec)
    second = parse_and_validate_structured_output(result=result, spec=spec)
    assert first is not second
    first_mapping = first.to_mapping()
    assert first_mapping == {
        "title": "Bag",
        "items": [{"sku": "a", "quantity": 2}, {"sku": "b", "quantity": 1}],
        "email": "a@example.com",
        "status": "ready",
    }
    first_mapping["items"][0]["sku"] = "mutated"  # type: ignore[index]
    assert first.to_mapping()["items"][0]["sku"] == "a"  # type: ignore[index]
    assert first == second
    assert result.output_envelope.payload_text.startswith("{")
    assert spec.schema.to_mapping()["additionalProperties"] is False


@pytest.mark.parametrize(
    "payload",
    [
        "{",
        '{"title":"Bag","title":"Duplicate","items":[],"email":"a@example.com","status":"ready"}',
        '{"title":"Bag","items":[],"email":"a@example.com","status":"ready","n":NaN}',
        '{"title":"Bag","items":[],"email":"a@example.com","status":"ready","n":Infinity}',
        '{"title":"Bag","items":[],"email":"a@example.com","status":"ready","n":-Infinity}',
        "[]",
        "42",
        '"scalar"',
        "null",
    ],
)
def test_malformed_duplicate_nonfinite_and_non_object_candidates_are_invalid(
    payload: str,
) -> None:
    error = _assert_error(
        _result(payload),
        _spec(),
        ModelRuntimeErrorCategory.INVALID_CANDIDATE,
        markers=(payload, "title", "items"),
    )
    assert error.message in {
        "structured output candidate is not valid JSON",
        "structured output candidate must be a JSON object",
    }


@pytest.mark.parametrize(
    "payload",
    [
        '{"title":"Bag","items":[],"email":"a@example.com","status":"ready","extra":1}',
        '{"title":"Bag","items":[{"sku":"a","quantity":1,"extra":true}],"email":"a@example.com","status":"ready"}',
        '{"title":"Bag","items":[],"email":"not-an-email","status":"ready"}',
        '{"title":"Bag","items":[{"sku":"a","quantity":true}],"email":"a@example.com","status":"ready"}',
        '{"title":"Bag","items":[{"sku":"a","quantity":"2"}],"email":"a@example.com","status":"ready"}',
        '{"title":"Bag","items":[],"email":"a@example.com","status":"READY"}',
        '{"title":"Bag","items":[],"email":"a@example.com"}',
    ],
)
def test_schema_violations_unknown_fields_formats_and_coercion_are_invalid(
    payload: str,
) -> None:
    _assert_error(
        _result(payload),
        _spec(),
        ModelRuntimeErrorCategory.INVALID_CANDIDATE,
        markers=("a@example.com", "READY", "quantity"),
    )


def test_schema_id_and_version_mismatch_are_nonretryable_invalid_requests() -> None:
    result = _result(schema_id="runtime-schema", schema_version="runtime-v2")
    spec = _spec(schema_id="project-schema", schema_version="project-v1")
    error = _assert_error(
        result,
        spec,
        ModelRuntimeErrorCategory.INVALID_REQUEST,
        markers=("runtime-schema", "project-schema", "runtime-v2", "project-v1"),
    )
    assert (
        error.message
        == "structured output schema identity does not match the model result"
    )


@pytest.mark.parametrize(
    "schema",
    [
        {"type": "array"},
        {"type": "object", "properties": {}, "required": []},
        {
            "type": "object",
            "properties": {"value": {"$ref": "other.json"}},
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {"value": {"$ref": "https://example.test/schema.json"}},
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {"value": {"format": "unknown-format"}},
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {"value": {"type": "object", "properties": {}}},
            "additionalProperties": False,
        },
        {
            "type": "object",
            "properties": {"value": {"$ref": "#/$defs/missing"}},
            "additionalProperties": False,
        },
    ],
)
def test_project_schema_preflight_errors_are_invalid_requests(
    schema: dict[str, object],
) -> None:
    error = _assert_error(
        _result(),
        _spec(StructuredContent.from_mapping(schema)),
        ModelRuntimeErrorCategory.INVALID_REQUEST,
        markers=("unknown-format", "example.test", "missing"),
    )
    assert error.message.startswith("structured output project schema")


def test_fragment_local_defs_reference_succeeds_without_network() -> None:
    schema = StructuredContent.from_mapping(
        {
            "$defs": {
                "item": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                    "additionalProperties": False,
                }
            },
            "type": "object",
            "properties": {"item": {"$ref": "#/$defs/item"}},
            "required": ["item"],
            "additionalProperties": False,
        }
    )
    result = _result('{"item":{"name":"ok"}}')
    assert parse_and_validate_structured_output(
        result=result, spec=_spec(schema)
    ).to_mapping() == {"item": {"name": "ok"}}


def test_schema_data_objects_and_business_property_names_are_not_walked() -> None:
    schema = StructuredContent.from_mapping(
        {
            "type": "object",
            "properties": {
                "format": {"type": "string"},
                "properties": {"type": "string"},
                "const_value": {"const": {"format": {"properties": "business-data"}}},
            },
            "required": ["format", "properties", "const_value"],
            "additionalProperties": False,
        }
    )
    result = _result(
        '{"format":"known","properties":"named","const_value":'
        '{"format":{"properties":"business-data"}}}'
    )
    assert parse_and_validate_structured_output(
        result=result, spec=_spec(schema)
    ).to_mapping() == {
        "format": "known",
        "properties": "named",
        "const_value": {"format": {"properties": "business-data"}},
    }


_SCHEMA_BEARING_CASES = cast(
    tuple[tuple[str, object], ...],
    (
        (
            "allOf",
            [{"type": "object", "properties": {}}],
        ),
        (
            "anyOf",
            [{"type": "object", "properties": {}}],
        ),
        (
            "oneOf",
            [{"type": "object", "properties": {}}],
        ),
        ("not", {"type": "object", "properties": {}}),
        ("if", {"type": "object", "properties": {}}),
        ("then", {"type": "object", "properties": {}}),
        ("else", {"type": "object", "properties": {}}),
        ("items", {"type": "object", "properties": {}}),
        (
            "prefixItems",
            [{"type": "object", "properties": {}}],
        ),
        ("contains", {"type": "object", "properties": {}}),
        ("contentSchema", {"type": "object", "properties": {}}),
        ("propertyNames", {"type": "object", "properties": {}}),
        ("additionalProperties", {"type": "object", "properties": {}}),
        ("unevaluatedItems", {"type": "object", "properties": {}}),
        ("unevaluatedProperties", {"type": "object", "properties": {}}),
        (
            "dependentSchemas",
            {"branch": {"type": "object", "properties": {}}},
        ),
        (
            "patternProperties",
            {"^branch$": {"type": "object", "properties": {}}},
        ),
        ("properties", {"branch": {"type": "object", "properties": {}}}),
        ("$defs", {"branch": {"type": "object", "properties": {}}}),
    ),
)


@pytest.mark.parametrize("keyword, value", _SCHEMA_BEARING_CASES)
def test_schema_bearing_containers_and_combinators_are_preflighted(
    keyword: str, value: object
) -> None:
    schema = {"type": "object", "additionalProperties": False, keyword: value}
    error = _assert_error(
        _result("{}"),
        _spec(StructuredContent.from_mapping(schema)),
        ModelRuntimeErrorCategory.INVALID_REQUEST,
    )
    assert error.message == "structured output project schema is invalid"


def test_remote_reference_never_opens_a_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_socket(*args: object, **kwargs: object) -> socket.socket:
        raise AssertionError("remote schema retrieval attempted")

    monkeypatch.setattr(socket, "socket", fail_socket)
    schema = StructuredContent.from_mapping(
        {
            "type": "object",
            "properties": {"value": {"$ref": "https://example.test/schema.json"}},
            "additionalProperties": False,
        }
    )
    _assert_error(
        _result('{"value":"ok"}'),
        _spec(schema),
        ModelRuntimeErrorCategory.INVALID_REQUEST,
    )


def test_fragment_local_dynamic_reference_succeeds_without_network() -> None:
    schema = StructuredContent.from_mapping(
        {
            "$defs": {
                "item": {
                    "$dynamicAnchor": "item",
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                    "additionalProperties": False,
                }
            },
            "type": "object",
            "properties": {"item": {"$dynamicRef": "#item"}},
            "required": ["item"],
            "additionalProperties": False,
        }
    )
    result = _result('{"item":{"name":"ok"}}')
    assert parse_and_validate_structured_output(
        result=result, spec=_spec(schema)
    ).to_mapping() == {"item": {"name": "ok"}}


def test_diagnostics_are_fixed_and_safe() -> None:
    result = _result(
        '{"title":"payload-secret","items":[],"email":"a@example.com","status":"ready"}'
    )
    schema = StructuredContent.from_mapping(
        {
            "type": "object",
            "properties": {"secret": {"type": "string"}},
            "required": ["secret"],
            "additionalProperties": False,
        }
    )
    error = _assert_error(
        result,
        _spec(schema),
        ModelRuntimeErrorCategory.INVALID_CANDIDATE,
        markers=("payload-secret", "secret", "type", "required"),
    )
    assert error.message in {
        "structured output candidate is not valid",
        "structured output candidate violates the project schema",
        "structured output candidate is not a JSON object",
    }


def test_inputs_remain_unchanged_after_failure_and_success() -> None:
    result = _result()
    spec = _spec()
    payload_before = result.output_envelope.payload_text
    schema_before = spec.schema.to_mapping()
    parse_and_validate_structured_output(result=result, spec=spec)
    assert result.output_envelope.payload_text == payload_before
    assert spec.schema.to_mapping() == schema_before
    _assert_error(
        _result('{"title":"Bag","items":[],"email":"bad","status":"ready"}'),
        spec,
        ModelRuntimeErrorCategory.INVALID_CANDIDATE,
    )
    assert spec.schema.to_mapping() == schema_before
