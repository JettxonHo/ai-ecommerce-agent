"""Unit coverage for the shared immutable structured-content value."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any, cast

import pytest

from ai_ecommerce_agent.shared_kernel import StructuredContent

pytestmark = pytest.mark.unit


def test_nested_values_are_copied_and_round_trip_as_plain_data() -> None:
    values: dict[str, object] = {
        "name": "commuter pack",
        "details": {
            "capacity_litres": 18,
            "features": ["laptop sleeve", {"waterproof": True}],
        },
    }

    content = StructuredContent.from_mapping(values)
    values["name"] = "changed"
    details = cast(dict[str, object], values["details"])
    details["capacity_litres"] = 99
    features = cast(list[object], details["features"])
    features.append("new feature")

    assert content.to_mapping() == {
        "name": "commuter pack",
        "details": {
            "capacity_litres": 18,
            "features": ["laptop sleeve", {"waterproof": True}],
        },
    }


def test_to_mapping_returns_a_deep_detached_copy() -> None:
    content = StructuredContent.from_mapping(
        {"nested": {"items": [{"label": "first"}]}}
    )

    detached = content.to_mapping()
    nested = cast(dict[str, object], detached["nested"])
    items = cast(list[object], nested["items"])
    items.append({"label": "second"})
    cast(dict[str, object], items[0])["label"] = "changed"

    assert content.to_mapping() == {"nested": {"items": [{"label": "first"}]}}
    assert isinstance(detached, Mapping)


def test_mapping_order_does_not_affect_equality_but_array_order_does() -> None:
    first = StructuredContent.from_mapping(
        {"outer": {"a": 1, "b": 2}, "items": ["a", "b"]}
    )
    reordered_object = StructuredContent.from_mapping(
        {"items": ["a", "b"], "outer": {"b": 2, "a": 1}}
    )
    reordered_array = StructuredContent.from_mapping(
        {"outer": {"a": 1, "b": 2}, "items": ["b", "a"]}
    )

    assert first == reordered_object
    assert first != reordered_array


def test_bool_and_int_are_distinct_and_scalar_types_are_preserved() -> None:
    boolean = StructuredContent.from_mapping({"value": True})
    integer = StructuredContent.from_mapping({"value": 1})
    finite = StructuredContent.from_mapping({"integer": 3, "float": 3.5})

    assert boolean != integer
    boolean_value = boolean.to_mapping()["value"]
    integer_value = integer.to_mapping()["value"]
    assert type(boolean_value) is bool
    assert type(integer_value) is int
    assert finite.to_mapping() == {"integer": 3, "float": 3.5}


def test_tuple_arrays_are_accepted_and_order_is_preserved() -> None:
    content = StructuredContent.from_mapping({"items": ("first", "second")})

    assert content.to_mapping() == {"items": ["first", "second"]}


@pytest.mark.parametrize(
    "values",
    [
        {1: "non-string key"},
        {"nested": {1: "non-string key"}},
        {"value": b"bytes"},
        {"value": {"set-value"}},
        {"value": object()},
        {"value": math.nan},
        {"value": math.inf},
        {"value": -math.inf},
    ],
)
def test_unsupported_values_are_rejected(values: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        StructuredContent.from_mapping(cast(Any, values))


def test_non_mapping_top_level_value_is_rejected() -> None:
    with pytest.raises(TypeError):
        StructuredContent.from_mapping(cast(Any, ["not", "a", "mapping"]))


def test_recursive_input_is_rejected() -> None:
    values: dict[str, object] = {}
    values["self"] = values

    with pytest.raises(ValueError):
        StructuredContent.from_mapping(values)
