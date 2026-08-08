"""Mutable-resource compare-and-swap revision value."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True, slots=True, order=True)
class Revision:
    """A non-negative revision for one mutable resource.

    Revision is the optimistic-concurrency value for mutable current truth;
    it is intentionally not a domain version number.  A newly-created
    mutable resource starts at ``Revision(0)`` and each successful transition
    may advance it by one or more values under its owning transaction.
    """

    value: int

    def __post_init__(self) -> None:
        value = cast(object, self.value)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("revision value must be an integer")
        if value < 0:
            raise ValueError("revision value must be non-negative")

    @classmethod
    def initial(cls) -> Revision:
        """Return the initial revision for a newly-created resource."""

        return cls(0)

    def next(self) -> Revision:
        """Return the next revision without mutating this value."""

        return type(self)(self.value + 1)


__all__ = ["Revision"]
