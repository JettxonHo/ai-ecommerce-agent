"""Immutable, framework-neutral structured content."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from typing import cast


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
            if not isinstance(key, str):
                raise TypeError("structured content mapping keys must be strings")
            entries.append((key, _freeze(value, active)))
        entries.sort(key=lambda entry: entry[0])
        return tuple(entries)
    finally:
        active.remove(identity)


def _freeze(value: object, active: set[int]) -> tuple[str, object]:
    if value is None:
        return ("none", None)
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError("structured content floats must be finite")
        return ("float", value)
    if isinstance(value, str):
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


@dataclass(frozen=True, slots=True, init=False)
class StructuredContent:
    """A deeply immutable top-level string-keyed structured value."""

    _value: tuple[tuple[str, tuple[str, object]], ...]

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


__all__ = ["StructuredContent"]
