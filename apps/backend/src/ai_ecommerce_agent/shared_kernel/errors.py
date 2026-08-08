"""Project-owned error values with shallow, safe context.

This module intentionally has no HTTP, ORM, database-driver or framework
dependencies.  Adapters can translate ``ProjectError`` at their boundary,
while core code can preserve stable category/code semantics without leaking
technical exceptions.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast


@dataclass(frozen=True, slots=True)
class SafeContext:
    """An immutable shallow mapping of already-safe string context values.

    This value only copies and exposes primitive string pairs; it is not a
    sanitizer or a recursive redaction framework. Callers are responsible for
    supplying context that is safe to include at the relevant boundary.
    """

    values: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        keys: set[str] = set()
        for key, value in self.values:
            key_object = cast(object, key)
            value_object = cast(object, value)
            if not isinstance(key_object, str) or not key_object.strip():
                raise TypeError("safe context keys must be non-empty strings")
            if key_object in keys:
                raise ValueError(f"safe context contains duplicate key: {key_object!r}")
            keys.add(key_object)
            if not isinstance(value_object, str):
                raise TypeError("safe context values must be strings")

    @classmethod
    def from_mapping(cls, context: Mapping[str, str] | None = None) -> SafeContext:
        """Copy a mapping so callers cannot mutate error context."""

        if context is None:
            return cls()
        return cls(tuple(sorted(context.items())))

    def as_mapping(self) -> Mapping[str, str]:
        """Expose a read-only mapping suitable for boundary translation."""

        return MappingProxyType(dict(self.values))


@dataclass(frozen=True, slots=True)
class ProjectError(Exception):
    """A stable project error category/code with safe diagnostic context."""

    category: str
    code: str
    context: SafeContext = SafeContext()

    def __post_init__(self) -> None:
        category = cast(object, self.category)
        code = cast(object, self.code)
        context = cast(object, self.context)
        if not isinstance(category, str) or not category.strip():
            raise TypeError("error category must be a non-empty string")
        if not isinstance(code, str) or not code.strip():
            raise TypeError("error code must be a non-empty string")
        if not isinstance(context, SafeContext):
            raise TypeError("error context must be SafeContext")
        Exception.__init__(self, f"{self.category}:{self.code}")

    @classmethod
    def from_context(
        cls,
        category: str,
        code: str,
        context: Mapping[str, str] | None = None,
    ) -> ProjectError:
        """Construct an error from a mapping at an adapter/application edge."""

        return cls(category, code, SafeContext.from_mapping(context))

    @property
    def safe_context(self) -> Mapping[str, str]:
        """Return the context as a read-only mapping."""

        return self.context.as_mapping()

    def __str__(self) -> str:
        return f"{self.category}:{self.code}"


__all__ = ["ProjectError", "SafeContext"]
