"""Immutable domain-version identity and version-number values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from .identity import DomainVersionId


@dataclass(frozen=True, slots=True, order=True)
class VersionNumber:
    """A positive, monotonically allocated number within one logical object."""

    value: int

    def __post_init__(self) -> None:
        value = cast(object, self.value)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("version number must be an integer")
        if value < 1:
            raise ValueError("version number must be positive")

    @classmethod
    def initial(cls) -> VersionNumber:
        """Return the first version number for a logical object."""

        return cls(1)

    def next(self) -> VersionNumber:
        """Return the next version number without mutating this value."""

        return type(self)(self.value + 1)


__all__ = ["DomainVersionId", "VersionNumber"]
