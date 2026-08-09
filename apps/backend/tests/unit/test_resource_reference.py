"""Focused unit coverage for the shared immutable resource reference."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from typing import Any, cast, get_type_hints

import pytest

import ai_ecommerce_agent.shared_kernel as shared_kernel
from ai_ecommerce_agent.shared_kernel import ResourceReference

pytestmark = pytest.mark.unit


class _PlainStringSubclass(str):
    """A normal subclass still rejected by the primitive-string boundary."""


class _StripOverrideString(str):
    def strip(self, chars: str | None = None) -> str:
        del chars
        return ""


class _MutableString(str):
    state: list[object]

    def __new__(cls, value: str) -> _MutableString:
        instance = super().__new__(cls, value)
        instance.state = []
        return instance


def test_resource_reference_is_an_exact_frozen_slotted_shared_value() -> None:
    assert is_dataclass(ResourceReference)
    assert cast(Any, ResourceReference).__dataclass_params__.frozen
    assert tuple(field.name for field in fields(ResourceReference)) == (
        "resource_kind",
        "resource_id",
    )
    assert ResourceReference.__slots__ == ("resource_kind", "resource_id")
    assert get_type_hints(ResourceReference) == {
        "resource_kind": str,
        "resource_id": str,
    }
    assert shared_kernel.ResourceReference is ResourceReference
    assert shared_kernel.__all__.count("ResourceReference") == 1


def test_resource_reference_preserves_exact_values_and_is_immutable() -> None:
    reference = ResourceReference("source_fragment", "fragment-1")

    assert reference.resource_kind == "source_fragment"
    assert reference.resource_id == "fragment-1"
    with pytest.raises(FrozenInstanceError):
        reference.resource_id = "fragment-2"  # type: ignore[misc]


@pytest.mark.parametrize("field_name", ["resource_kind", "resource_id"])
@pytest.mark.parametrize("value", ["", " ", "\t", "\n"])
def test_resource_reference_rejects_empty_or_whitespace_strings(
    field_name: str, value: str
) -> None:
    values: dict[str, object] = {
        "resource_kind": "source_fragment",
        "resource_id": "fragment-1",
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        ResourceReference(**cast(Any, values))


@pytest.mark.parametrize("field_name", ["resource_kind", "resource_id"])
@pytest.mark.parametrize("value", [None, 1, True, object()])
def test_resource_reference_rejects_non_string_values(
    field_name: str, value: object
) -> None:
    values: dict[str, object] = {
        "resource_kind": "source_fragment",
        "resource_id": "fragment-1",
    }
    values[field_name] = value

    with pytest.raises(TypeError):
        ResourceReference(**cast(Any, values))


@pytest.mark.parametrize("field_name", ["resource_kind", "resource_id"])
@pytest.mark.parametrize(
    "value",
    [
        _PlainStringSubclass("source_fragment"),
        _StripOverrideString("source_fragment"),
        _MutableString("source_fragment"),
    ],
)
def test_resource_reference_rejects_string_subclasses(
    field_name: str, value: str
) -> None:
    values: dict[str, object] = {
        "resource_kind": "source_fragment",
        "resource_id": "fragment-1",
    }
    values[field_name] = value

    with pytest.raises(TypeError):
        ResourceReference(**cast(Any, values))


def test_resource_reference_keeps_plain_string_values_unchanged() -> None:
    kind = " source_fragment "
    identifier = " fragment-1 "

    reference = ResourceReference(kind, identifier)

    assert reference.resource_kind == kind
    assert reference.resource_id == identifier
