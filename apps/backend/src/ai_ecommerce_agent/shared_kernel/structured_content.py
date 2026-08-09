"""Immutable, framework-neutral structured content."""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from typing import NoReturn, cast


def _freeze_mapping(
    values: Mapping[object, object], active: set[int]
) -> tuple[tuple[str, tuple[str, object]], ...]:
    identity = id(values)
    if identity in active:
        raise ValueError("structured content cannot contain cycles")
    active.add(identity)
    try:
        entries: list[tuple[str, tuple[str, object]]] = []
        for key, value in values.items():
            if type(key) is not str:
                raise TypeError("structured content mapping keys must be strings")
            entries.append((key, _freeze(value, active)))
        entries.sort(key=lambda entry: entry[0])
        return tuple(entries)
    finally:
        active.remove(identity)


def _freeze(value: object, active: set[int]) -> tuple[str, object]:
    if value is None:
        return ("none", None)
    if type(value) is bool:
        return ("bool", value)
    if type(value) is int:
        return ("int", value)
    if type(value) is float:
        if not isfinite(value):
            raise ValueError("structured content floats must be finite")
        return ("float", value)
    if type(value) is str:
        return ("str", value)
    if isinstance(value, Mapping):
        return (
            "mapping",
            _freeze_mapping(cast(Mapping[object, object], value), active),
        )
    if isinstance(value, (list, tuple)):
        array = cast(list[object] | tuple[object, ...], value)
        identity = id(array)
        if identity in active:
            raise ValueError("structured content cannot contain cycles")
        active.add(identity)
        try:
            frozen_items = tuple(_freeze(item, active) for item in array)
        finally:
            active.remove(identity)
        return ("array", frozen_items)
    raise TypeError(f"unsupported structured content value: {type(value).__name__}")


def _thaw(value: tuple[str, object]) -> object:
    kind, payload = value
    if kind in {"none", "bool", "int", "float", "str"}:
        return payload
    if kind == "mapping":
        entries = cast(tuple[tuple[str, tuple[str, object]], ...], payload)
        return {key: _thaw(item) for key, item in entries}
    if kind == "array":
        items = cast(tuple[tuple[str, object], ...], payload)
        return [_thaw(item) for item in items]
    raise AssertionError(f"unknown structured content kind: {kind!r}")


class StructuredContent:
    """A deeply immutable top-level string-keyed structured value."""

    __slots__ = ("_value",)

    _value: tuple[tuple[str, tuple[str, object]], ...]

    def __init__(self, *args: object, **kwargs: object) -> None:
        raise TypeError("StructuredContent must be created with from_mapping")

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> StructuredContent:
        """Copy and freeze a string-keyed mapping of JSON-like values."""

        candidate = cast(object, values)
        if not isinstance(candidate, Mapping):
            raise TypeError("structured content must be created from a mapping")
        instance = object.__new__(cls)
        frozen = _freeze_mapping(cast(Mapping[object, object], candidate), set())
        object.__setattr__(instance, "_value", frozen)
        return instance

    def to_mapping(self) -> Mapping[str, object]:
        """Return a new, mutable plain mapping detached from this value."""

        return {key: _thaw(value) for key, value in self._value}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StructuredContent):
            return False
        return self._value == other._value

    def __repr__(self) -> str:
        return "StructuredContent(...)"

    def __setattr__(self, name: str, value: object) -> NoReturn:
        raise TypeError("StructuredContent is immutable")

    def __delattr__(self, name: str) -> NoReturn:
        raise TypeError("StructuredContent is immutable")

    def __hash__(self) -> NoReturn:
        raise TypeError("StructuredContent instances are not hashable")


__all__ = ["StructuredContent"]
