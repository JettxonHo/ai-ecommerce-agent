"""Pure JSON parsing and Draft 2020-12 Structured Output validation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, NoReturn, cast

from jsonschema import Draft202012Validator
from referencing import Registry

from ai_ecommerce_agent.application.model_runtime import (
    ModelCallResult,
    ModelRuntimeError,
    ModelRuntimeErrorCategory,
    StructuredOutputSpec,
)
from ai_ecommerce_agent.shared_kernel.structured_content import StructuredContent

_SCHEMA_IDENTITY_MESSAGE = (
    "structured output schema identity does not match the model result"
)
_PROJECT_SCHEMA_MESSAGE = "structured output project schema is invalid"
_CANDIDATE_JSON_MESSAGE = "structured output candidate is not valid JSON"
_CANDIDATE_OBJECT_MESSAGE = "structured output candidate must be a JSON object"
_CANDIDATE_SCHEMA_MESSAGE = "structured output candidate is not valid"

_OBJECT_KEYWORDS = (
    "additionalProperties",
    "dependentRequired",
    "dependentSchemas",
    "patternProperties",
    "properties",
    "propertyNames",
    "required",
    "unevaluatedProperties",
)


class _ProjectSchemaError(ValueError):
    """Internal marker for schema preflight failures."""


def _runtime_error(
    result: ModelCallResult,
    category: ModelRuntimeErrorCategory,
    message: str,
) -> ModelRuntimeError:
    metadata = result.provider_metadata
    return ModelRuntimeError(
        category,
        message,
        False,
        metadata.model_call_id,
        metadata,
    )


def _is_object_schema(schema: Mapping[str, object]) -> bool:
    schema_type = schema.get("type")
    if schema_type == "object":
        return True
    if type(schema_type) is list and "object" in schema_type:
        return True
    return any(keyword in schema for keyword in _OBJECT_KEYWORDS)


def _anchor_exists(schema: object, anchor: str) -> bool:
    if isinstance(schema, Mapping):
        mapping = cast(Mapping[str, object], schema)
        if mapping.get("$anchor") == anchor or mapping.get("$dynamicAnchor") == anchor:
            return True
        return any(_anchor_exists(value, anchor) for value in mapping.values())
    if type(schema) is list:
        values = cast(list[object], schema)
        return any(_anchor_exists(value, anchor) for value in values)
    return False


def _resolve_local_reference(schema: Mapping[str, object], reference: str) -> None:
    if reference == "#":
        return
    if not reference.startswith("#"):
        raise _ProjectSchemaError
    fragment = reference[1:]
    if not fragment.startswith("/"):
        if _anchor_exists(schema, fragment):
            return
        raise _ProjectSchemaError
    current: object = schema
    for raw_token in fragment[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            mapping = cast(Mapping[str, object], current)  # pyright: ignore[reportUnnecessaryCast]
        else:
            mapping = None
        if mapping is not None and token in mapping:
            current = mapping[token]
            continue
        if isinstance(current, list):
            values = cast(list[object], current)
        else:
            values = None
        if values is not None and token.isdigit() and int(token) < len(values):
            current = values[int(token)]
            continue
        raise _ProjectSchemaError


def _walk_schema(value: object, root: Mapping[str, object]) -> None:
    if isinstance(value, Mapping):
        mapping = cast(Mapping[str, object], value)
        for reference_key in ("$ref", "$dynamicRef"):
            if reference_key in mapping:
                reference = mapping[reference_key]
                if type(reference) is not str or not reference.startswith("#"):
                    raise _ProjectSchemaError
                _resolve_local_reference(root, reference)
        if "format" in mapping:
            format_name = mapping["format"]
            if (
                type(format_name) is not str
                or format_name not in Draft202012Validator.FORMAT_CHECKER.checkers
            ):
                raise _ProjectSchemaError
        if (
            _is_object_schema(mapping)
            and mapping.get("additionalProperties") is not False
        ):
            raise _ProjectSchemaError
        for child in mapping.values():
            _walk_schema(child, root)
    elif type(value) is list:
        values = cast(list[object], value)
        for child in values:
            _walk_schema(child, root)


def _preflight_schema(schema: object) -> dict[str, object]:
    if type(schema) is not dict:
        raise _ProjectSchemaError
    schema_mapping = cast(dict[str, object], schema)
    schema_type = schema_mapping.get("type")
    if schema_type != "object" and not (
        type(schema_type) is list and "object" in schema_type
    ):
        raise _ProjectSchemaError
    _walk_schema(schema_mapping, schema_mapping)
    try:
        Draft202012Validator.check_schema(schema_mapping)
    except Exception as error:
        raise _ProjectSchemaError from error
    return schema_mapping


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> NoReturn:
    raise ValueError(value)


def _parse_candidate(payload: str) -> object:
    return json.loads(
        payload,
        object_pairs_hook=_reject_duplicate_pairs,
        parse_constant=_reject_nonfinite,
    )


def parse_and_validate_structured_output(
    *,
    result: ModelCallResult,
    spec: StructuredOutputSpec,
) -> StructuredContent:
    """Parse a model payload and return its validated immutable projection."""

    if type(result) is not ModelCallResult:
        raise TypeError("result must be a ModelCallResult")
    if type(spec) is not StructuredOutputSpec:
        raise TypeError("spec must be a StructuredOutputSpec")
    version_tuple = result.provider_metadata.version_tuple
    if (
        version_tuple.output_schema_id != spec.output_schema_id
        or version_tuple.output_schema_version != spec.output_schema_version
    ):
        raise _runtime_error(
            result,
            ModelRuntimeErrorCategory.INVALID_REQUEST,
            _SCHEMA_IDENTITY_MESSAGE,
        )
    try:
        schema = _preflight_schema(spec.schema.to_mapping())
    except Exception as error:
        if isinstance(error, _ProjectSchemaError):
            raise _runtime_error(
                result,
                ModelRuntimeErrorCategory.INVALID_REQUEST,
                _PROJECT_SCHEMA_MESSAGE,
            ) from None
        raise _runtime_error(
            result,
            ModelRuntimeErrorCategory.INVALID_REQUEST,
            _PROJECT_SCHEMA_MESSAGE,
        ) from None
    try:
        candidate = _parse_candidate(result.output_envelope.payload_text)
    except Exception:
        raise _runtime_error(
            result,
            ModelRuntimeErrorCategory.INVALID_CANDIDATE,
            _CANDIDATE_JSON_MESSAGE,
        ) from None
    if type(candidate) is not dict:
        raise _runtime_error(
            result,
            ModelRuntimeErrorCategory.INVALID_CANDIDATE,
            _CANDIDATE_OBJECT_MESSAGE,
        )
    candidate_mapping = cast(dict[str, object], candidate)
    try:
        validator = Draft202012Validator(
            schema,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
            registry=Registry(),
        )
        errors = list(cast(Any, validator).iter_errors(candidate_mapping))
    except Exception:
        raise _runtime_error(
            result,
            ModelRuntimeErrorCategory.INVALID_REQUEST,
            _PROJECT_SCHEMA_MESSAGE,
        ) from None
    if errors:
        raise _runtime_error(
            result,
            ModelRuntimeErrorCategory.INVALID_CANDIDATE,
            _CANDIDATE_SCHEMA_MESSAGE,
        )
    return StructuredContent.from_mapping(candidate_mapping)


__all__ = ["parse_and_validate_structured_output"]
