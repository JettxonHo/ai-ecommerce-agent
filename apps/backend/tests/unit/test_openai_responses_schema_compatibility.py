"""Behavioral tests for the provider schema compatibility subset."""

from __future__ import annotations

from copy import deepcopy
from typing import cast

import pytest

import ai_ecommerce_agent.platform.model_runtime as _runtime_package
from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId,
    ModelRuntimeError,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.platform.model_runtime.openai_responses import (
    _schema_compatibility,
)
from ai_ecommerce_agent.shared_kernel import StructuredContent

_runtime_package.__dict__.pop("openai_responses", None)

pytestmark = pytest.mark.unit


_CALL_ID = ModelCallId("call-1")
ensure_openai_responses_schema_compatible = (
    _schema_compatibility.ensure_openai_responses_schema_compatible
)


def _base_schema() -> dict[str, object]:
    return {
        "type": "object",
        "properties": {"value": {"type": "string"}},
        "required": ["value"],
        "additionalProperties": False,
    }


def _check(schema: object, *, schema_id: str = "schema") -> None:
    ensure_openai_responses_schema_compatible(
        structured_output=StructuredOutputSpec(
            schema_id,
            "v1",
            StructuredContent.from_mapping(schema),  # type: ignore[arg-type]
        ),
        model_call_id=_CALL_ID,
    )


def _invalid(schema: object) -> None:
    with pytest.raises(ModelRuntimeError) as caught:
        _check(schema)
    error = caught.value
    assert error.message == "OpenAI Responses schema is incompatible"
    assert error.model_call_id is _CALL_ID
    assert error.provider_metadata is None
    assert error.retryability is False
    assert all(marker not in error.message for marker in ("value", "path", "secret"))


def test_valid_subset_keywords_and_nested_local_recursive_refs() -> None:
    schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "name",
                "pattern": "^[a-z]+$",
                "format": "email",
            },
            "choice": {
                "anyOf": [
                    {"type": "string"},
                    {"type": ["string", "null"]},
                ]
            },
            "node": {"$ref": "#/$defs/node"},
            "items": {
                "type": "array",
                "minItems": 0,
                "maxItems": 3,
                "items": {"type": "integer"},
            },
            "amount": {
                "type": "number",
                "multipleOf": 0.5,
                "minimum": 0,
                "maximum": 10,
                "exclusiveMinimum": -1,
                "exclusiveMaximum": 11,
            },
            "flag": {"type": "boolean"},
            "nothing": {"type": "null"},
            "kind": {"type": "string", "enum": ["x", "y"], "const": "x"},
        },
        "required": [
            "name",
            "choice",
            "node",
            "items",
            "amount",
            "flag",
            "nothing",
            "kind",
        ],
        "additionalProperties": False,
        "$defs": {
            "node": {
                "type": "object",
                "properties": {
                    "next": {"anyOf": [{"$ref": "#/$defs/node"}, {"type": "null"}]}
                },
                "required": ["next"],
                "additionalProperties": False,
            }
        },
    }
    before = deepcopy(schema)
    assert _check(schema) is None
    assert schema == before


@pytest.mark.parametrize("schema_id", ["schema.name", "schema/name", "x" * 65])
def test_schema_name_uses_the_provider_identifier_grammar(schema_id: str) -> None:
    with pytest.raises(ModelRuntimeError):
        _check(_base_schema(), schema_id=schema_id)


@pytest.mark.parametrize(
    "keyword",
    [
        "allOf",
        "oneOf",
        "not",
        "dependentRequired",
        "dependentSchemas",
        "if",
        "then",
        "else",
        "prefixItems",
        "contains",
        "unevaluatedItems",
        "unevaluatedProperties",
        "patternProperties",
        "propertyNames",
    ],
)
def test_unsupported_schema_keywords_are_rejected_with_one_mutation(
    keyword: str,
) -> None:
    schema = _base_schema()
    schema[keyword] = [] if keyword in {"allOf", "oneOf", "prefixItems"} else {}
    _invalid(schema)


@pytest.mark.parametrize(
    "mutation",
    [
        "root_type",
        "root_any_of",
        "additional_properties",
        "required_missing",
        "required_unknown",
        "required_duplicate",
        "required_non_string",
        "properties_non_mapping",
        "properties_unknown",
    ],
)
def test_root_and_required_object_invariants_are_mutation_sensitive(
    mutation: str,
) -> None:
    schema = _base_schema()
    if mutation == "root_type":
        schema["type"] = "string"
    elif mutation == "root_any_of":
        schema["anyOf"] = [{"type": "string"}]
    elif mutation == "additional_properties":
        schema["additionalProperties"] = True
    elif mutation == "required_missing":
        schema["required"] = []
    elif mutation == "required_unknown":
        schema["required"] = ["other"]
    elif mutation == "required_duplicate":
        schema["required"] = ["value", "value"]
    elif mutation == "required_non_string":
        schema["required"] = [1]
    elif mutation == "properties_non_mapping":
        schema["properties"] = []
    else:
        schema["properties"] = {
            "value": {"type": "string"},
            "other": {"unknown": True},
        }
    _invalid(schema)


@pytest.mark.parametrize(
    "reference",
    ["https://example.invalid/schema", "relative.json", "#missing", "#/missing"],
)
def test_only_existing_local_pointer_references_are_allowed(reference: str) -> None:
    schema = _base_schema()
    schema["properties"] = {"value": {"$ref": reference}}
    _invalid(schema)


def test_percent_and_pointer_token_references_are_resolved_without_expansion() -> None:
    schema = _base_schema()
    schema["properties"] = {"value": {"$ref": "#/$defs/a%20b/missing"}}
    schema["$defs"] = {
        "a b": {
            "type": "object",
            "properties": {"slash/key": {"type": "string"}},
            "required": ["slash/key"],
            "additionalProperties": False,
        }
    }
    _invalid(schema)
    schema["properties"] = {"value": {"$ref": "#/$defs/a%20b/properties/slash~1key"}}
    assert _check(schema) is None


@pytest.mark.parametrize(
    "reference",
    ["#/$defs/a%20b", "#/$defs/node"],
)
def test_valid_percent_reference_targets(reference: str) -> None:
    schema = _base_schema()
    schema["properties"] = {"value": {"$ref": reference}}
    schema["$defs"] = {
        "a b": {"type": "string"},
        "node": {"type": "string"},
    }
    assert _check(schema) is None


def test_root_recursive_reference_is_checked_but_not_expanded() -> None:
    schema = _base_schema()
    schema["properties"] = {"value": {"$ref": "#"}}
    assert _check(schema) is None


def test_data_values_are_not_walked_as_schema_nodes() -> None:
    schema = _base_schema()
    schema["properties"] = {
        "value": {
            "type": "string",
            "const": {"allOf": [{"not": {}}], "$ref": "remote"},
            "enum": [{"if": {"then": {}}}],
        }
    }
    assert _check(schema) is None


@pytest.mark.parametrize("reference", ["#/$defs", "#/properties"])
def test_reference_containers_are_not_schema_targets_when_keys_collide(
    reference: str,
) -> None:
    schema = _base_schema()
    if reference == "#/$defs":
        schema["properties"] = {"value": {"$ref": reference}}
        schema["$defs"] = {"type": {"type": "string"}}
    else:
        schema["properties"] = {
            "type": {"type": "string"},
            "value": {"$ref": reference},
        }
        schema["required"] = ["type", "value"]
    _invalid(schema)


def test_boolean_schema_nodes_are_rejected() -> None:
    mutations: tuple[dict[str, object], ...] = (
        {"properties": {"value": True}},
        {"properties": {"value": {"anyOf": [True]}}},
        {"properties": {"value": {"type": "array", "items": False}}},
        {
            "properties": {"value": {"$ref": "#/$defs/node"}},
            "$defs": {"node": True},
        },
    )
    for mutation in mutations:
        schema = _base_schema()
        schema.update(mutation)
        _invalid(schema)


def test_explicit_null_enum_is_rejected() -> None:
    schema = _base_schema()
    schema["properties"] = {"value": {"type": "string", "enum": None}}
    _invalid(schema)


def test_nullable_type_arrays_require_one_supported_type_and_one_null() -> None:
    for type_value in (["string", "null"], ["null", "integer"]):
        schema = _base_schema()
        schema["properties"] = {"value": {"type": type_value}}
        assert _check(schema) is None

    for type_value in (
        ["string", "string"],
        ["string", "null", "integer"],
        ["null", "null"],
        ["string", "boolean"],
        ["string"],
    ):
        schema = _base_schema()
        schema["properties"] = {"value": {"type": type_value}}
        _invalid(schema)


@pytest.mark.parametrize(
    "reference",
    [
        "#/$defs/choices/anyOf/00",
        "#/$defs/choices/anyOf/01",
        "#/$defs/choices/anyOf/" + "9" * 10_000,
        "#/$defs/choices~2",
        "#/required/0",
        "#/const",
        "#/enum/0",
    ],
)
def test_local_references_require_canonical_indexes_and_schema_targets(
    reference: str,
) -> None:
    schema = _base_schema()
    schema["properties"] = {"value": {"$ref": reference}}
    schema["$defs"] = {
        "choices": {"anyOf": [{"type": "string"}, {"type": "number"}]},
    }
    schema["const"] = "instance data"
    schema["enum"] = ["instance data"]
    _invalid(schema)


@pytest.mark.parametrize(
    ("format_name",),
    [
        ("date-time",),
        ("time",),
        ("date",),
        ("duration",),
        ("email",),
        ("hostname",),
        ("ipv4",),
        ("ipv6",),
        ("uuid",),
    ],
)
def test_supported_formats_are_accepted(format_name: str) -> None:
    schema = _base_schema()
    schema["properties"] = {"value": {"type": "string", "format": format_name}}
    assert _check(schema) is None


def test_unsupported_format_and_unknown_keyword_are_rejected() -> None:
    mutations: tuple[dict[str, object], ...] = (
        {"format": "regex"},
        {"unknown": True},
        {"default": {"allOf": []}},
        {"examples": [{"not": {}}]},
    )
    for mutation in mutations:
        schema = _base_schema()
        properties = schema["properties"]
        assert isinstance(properties, dict)
        value_schema = cast(dict[str, object], properties["value"])
        value_schema.update(mutation)
        _invalid(schema)


@pytest.mark.parametrize("keyword", ["allOf", "oneOf", "not", "if", "then", "else"])
def test_unsupported_keyword_in_nested_schema_is_rejected(keyword: str) -> None:
    schema = _base_schema()
    schema["properties"] = {"value": {"type": "string", keyword: {}}}
    _invalid(schema)


@pytest.mark.parametrize(
    ("keyword", "value"),
    [
        ("minimum", "low"),
        ("maximum", True),
        ("exclusiveMinimum", None),
        ("multipleOf", 0),
        ("minItems", -1),
        ("maxItems", True),
    ],
)
def test_numeric_and_array_constraints_are_exactly_typed(
    keyword: str, value: object
) -> None:
    schema = _base_schema()
    schema["properties"] = {
        "value": {"type": "array", "items": {"type": "string"}, keyword: value}
    }
    _invalid(schema)


def test_limits_reject_only_limit_plus_one() -> None:
    schema = _base_schema()
    schema["properties"] = {f"k{i}": {"type": "string"} for i in range(5000)}
    schema["required"] = list(schema["properties"])
    assert _check(schema) is None
    properties = schema["properties"]
    required = schema["required"]
    assert isinstance(properties, dict)
    assert isinstance(required, list)
    properties["overflow"] = {"type": "string"}
    required.append("overflow")
    _invalid(schema)

    schema = _base_schema()
    properties = schema["properties"]
    assert isinstance(properties, dict)
    properties["value"] = {
        "type": "string",
        "enum": [str(i) for i in range(1000)],
    }
    assert _check(schema) is None
    value_schema = properties["value"]
    assert isinstance(value_schema, dict)
    enum = value_schema["enum"]
    assert isinstance(enum, list)
    enum.append("1000")
    _invalid(schema)

    schema = _base_schema()
    properties = schema["properties"]
    assert isinstance(properties, dict)
    properties["value"] = {
        "type": "string",
        "enum": ["x" * 60 for _ in range(250)],
    }
    assert _check(schema) is None
    value_schema = properties["value"]
    assert isinstance(value_schema, dict)
    enum = value_schema["enum"]
    assert isinstance(enum, list)
    enum.append("x")
    _invalid(schema)


def test_depth_and_total_string_limits_reject_only_limit_plus_one() -> None:
    nested: dict[str, object] = {"type": "string"}
    for _ in range(8):
        nested = {
            "type": "object",
            "properties": {"child": nested},
            "required": ["child"],
            "additionalProperties": False,
        }
    schema = _base_schema()
    schema["properties"] = {"value": nested}
    assert _check(schema) is None
    nested = {
        "type": "object",
        "properties": {"child": nested},
        "required": ["child"],
        "additionalProperties": False,
    }
    schema["properties"] = {"value": nested}
    _invalid(schema)

    schema = _base_schema()
    properties = schema["properties"]
    assert isinstance(properties, dict)
    properties["value"] = {"type": "string", "const": "x" * 119995}
    assert _check(schema) is None
    properties["value"] = {"type": "string", "const": "x" * 119996}
    _invalid(schema)
