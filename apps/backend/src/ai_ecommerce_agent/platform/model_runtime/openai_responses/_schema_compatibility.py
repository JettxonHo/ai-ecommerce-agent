"""Offline validation of the OpenAI Structured Outputs schema subset."""

from __future__ import annotations

from re import fullmatch as _fullmatch
from typing import cast as _cast
from urllib.parse import unquote as _unquote

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallId as _ModelCallId,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelRuntimeError as _ModelRuntimeError,
)
from ai_ecommerce_agent.application.model_runtime import (
    ModelRuntimeErrorCategory as _ErrorCategory,
)
from ai_ecommerce_agent.application.model_runtime import (
    StructuredOutputSpec as _StructuredOutputSpec,
)

_MESSAGE = "OpenAI Responses schema is incompatible"
_TYPES = ("string", "number", "boolean", "integer", "object", "array", "null")
_FORMATS = (
    "date-time",
    "time",
    "date",
    "duration",
    "email",
    "hostname",
    "ipv4",
    "ipv6",
    "uuid",
)
_KEYWORDS = (
    "$defs",
    "$ref",
    "additionalProperties",
    "anyOf",
    "const",
    "description",
    "enum",
    "exclusiveMaximum",
    "exclusiveMinimum",
    "format",
    "items",
    "maxItems",
    "maximum",
    "minItems",
    "minimum",
    "multipleOf",
    "pattern",
    "properties",
    "required",
    "type",
)
_NUMERIC = (
    "multipleOf",
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
)
_ARRAY_LIMITS = ("minItems", "maxItems")
_OBJECT_HINTS = ("additionalProperties", "properties", "required")


class _SchemaError(ValueError):
    """Internal marker for provider compatibility failures."""


def _error(model_call_id: _ModelCallId) -> _ModelRuntimeError:
    return _ModelRuntimeError(
        _ErrorCategory.INVALID_REQUEST,
        _MESSAGE,
        False,
        model_call_id,
        None,
    )


def _mapping(value: object) -> dict[str, object]:
    if type(value) is not dict:
        raise _SchemaError
    result = _cast(dict[str, object], value)
    if any(type(key) is not str for key in result):
        raise _SchemaError
    return result


def _list(value: object) -> list[object]:
    if type(value) is not list:
        raise _SchemaError
    return _cast(list[object], value)


def _number(value: object, *, positive: bool = False) -> None:
    if type(value) not in (int, float):
        raise _SchemaError
    numeric = _cast(int | float, value)
    if positive and numeric <= 0:
        raise _SchemaError


def _type_value(value: object) -> None:
    if type(value) is str:
        if value not in _TYPES:
            raise _SchemaError
        return
    if type(value) is list:
        values = _cast(list[object], value)
        if not values or any(
            type(item) is not str or item not in _TYPES for item in values
        ):
            raise _SchemaError
        return
    raise _SchemaError


def _required(mapping: dict[str, object], properties: dict[str, object]) -> None:
    required = mapping.get("required")
    if type(required) is not list:
        raise _SchemaError
    values = _cast(list[object], required)
    if any(type(item) is not str for item in values):
        raise _SchemaError
    names = _cast(list[str], values)
    if len(names) != len(set(names)) or set(names) != set(properties):
        raise _SchemaError


def _reference(root: dict[str, object], reference: object) -> None:
    if type(reference) is not str or not reference.startswith("#"):
        raise _SchemaError
    fragment = _unquote(reference[1:])
    if fragment == "":
        return
    if not fragment.startswith("/"):
        raise _SchemaError
    current: object = root
    for raw_token in fragment[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        candidate = _cast(object, current)
        if type(candidate) is dict:
            mapping = _cast(dict[str, object], candidate)
            if token in mapping:
                current = mapping[token]
                continue
        if isinstance(candidate, list):
            values = _list(_cast(object, candidate))
            if token.isdigit() and int(token) < len(values):
                current = values[int(token)]
                continue
        raise _SchemaError


def _object_schema(mapping: dict[str, object]) -> bool:
    schema_type = mapping.get("type")
    return (
        schema_type == "object"
        or (type(schema_type) is list and "object" in schema_type)
        or any(keyword in mapping for keyword in _OBJECT_HINTS)
    )


def _enum(mapping: dict[str, object], stats: dict[str, int]) -> None:
    values = mapping.get("enum")
    if values is None:
        return
    if type(values) is not list or not values:
        raise _SchemaError
    enum_values = _cast(list[object], values)
    stats["enum"] += len(enum_values)
    strings = [value for value in enum_values if type(value) is str]
    stats["strings"] += sum(len(value) for value in strings)
    if len(enum_values) > 250 and len(strings) == len(enum_values):
        if sum(len(value) for value in strings) > 15_000:
            raise _SchemaError


def _walk(
    value: object, root: dict[str, object], depth: int, stats: dict[str, int]
) -> None:
    if type(value) is bool:
        return
    mapping = _mapping(value)
    if depth > 10 or any(key not in _KEYWORDS for key in mapping):
        raise _SchemaError
    if "$ref" in mapping:
        _reference(root, mapping["$ref"])
    if "type" in mapping:
        _type_value(mapping["type"])
    if "description" in mapping and type(mapping["description"]) is not str:
        raise _SchemaError
    if "pattern" in mapping and type(mapping["pattern"]) is not str:
        raise _SchemaError
    if "format" in mapping and (
        type(mapping["format"]) is not str or mapping["format"] not in _FORMATS
    ):
        raise _SchemaError
    _enum(mapping, stats)
    if "const" in mapping and type(mapping["const"]) is str:
        stats["strings"] += len(mapping["const"])
    for keyword in _NUMERIC:
        if keyword in mapping:
            _number(mapping[keyword], positive=keyword == "multipleOf")
    for keyword in _ARRAY_LIMITS:
        if keyword in mapping:
            value = mapping[keyword]
            if type(value) is not int or value < 0:
                raise _SchemaError
    if _object_schema(mapping):
        if mapping.get("additionalProperties") is not False:
            raise _SchemaError
        properties = mapping.get("properties", {})
        properties_mapping = _mapping(properties)
        stats["properties"] += len(properties_mapping)
        stats["strings"] += sum(len(name) for name in properties_mapping)
        _required(mapping, properties_mapping)
        for child in properties_mapping.values():
            _walk(child, root, depth + 1, stats)
    if "$defs" in mapping:
        definitions = _mapping(mapping["$defs"])
        stats["strings"] += sum(len(name) for name in definitions)
        for child in definitions.values():
            _walk(child, root, depth + 1, stats)
    if "items" in mapping:
        _walk(mapping["items"], root, depth + 1, stats)
    if "anyOf" in mapping:
        choices = mapping["anyOf"]
        if type(choices) is not list or not choices:
            raise _SchemaError
        for child in _cast(list[object], choices):
            _walk(child, root, depth + 1, stats)
    if (
        stats["properties"] > 5_000
        or stats["enum"] > 1_000
        or stats["strings"] > 120_000
    ):
        raise _SchemaError


def _validate(structured_output: _StructuredOutputSpec) -> None:
    if _fullmatch(r"[A-Za-z0-9_-]{1,64}", structured_output.output_schema_id) is None:
        raise _SchemaError
    schema = _mapping(structured_output.schema.to_mapping())
    if schema.get("type") != "object" or "anyOf" in schema:
        raise _SchemaError
    stats = {"properties": 0, "enum": 0, "strings": 0}
    _walk(schema, schema, 1, stats)


def ensure_openai_responses_schema_compatible(
    *,
    structured_output: _StructuredOutputSpec,
    model_call_id: _ModelCallId,
) -> None:
    """Validate one Structured Output spec against the OpenAI subset."""

    if type(structured_output) is not _StructuredOutputSpec:
        raise TypeError("structured_output must be a StructuredOutputSpec")
    if type(model_call_id) is not _ModelCallId:
        raise TypeError("model_call_id must be a ModelCallId")
    try:
        _validate(structured_output)
    except _SchemaError:
        raise _error(model_call_id) from None


__all__ = ["ensure_openai_responses_schema_compatible"]
