"""Opaque identities and fencing values for Durable Dispatch contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, cast
from uuid import uuid4

_IdentityT = TypeVar("_IdentityT", bound="_OpaqueDispatchIdentity")


@dataclass(frozen=True, slots=True, order=True)
class _OpaqueDispatchIdentity:
    """Immutable non-empty identity owned by the Durable Dispatch module."""

    value: str

    def __post_init__(self) -> None:
        value = cast(object, self.value)
        if type(value) is not str:
            raise TypeError("dispatch identity value must be a string")
        if not value.strip():
            raise ValueError("dispatch identity value must not be empty")

    @classmethod
    def new(cls: type[_IdentityT]) -> _IdentityT:
        """Create a new opaque identity for a dispatch-owned value."""

        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class DispatchId(_OpaqueDispatchIdentity):
    """Stable logical Work Intent identity across delivery retries."""


@dataclass(frozen=True, slots=True, order=True)
class DeliveryAttemptId(_OpaqueDispatchIdentity):
    """Identity of one successful claim and execution attempt."""


@dataclass(frozen=True, slots=True, order=True)
class FencingToken:
    """Monotonic non-negative token used by later ownership contracts."""

    value: int

    def __post_init__(self) -> None:
        value = cast(object, self.value)
        if type(value) is not int:
            raise TypeError("fencing token value must be an integer")
        if value < 0:
            raise ValueError("fencing token value must be non-negative")

    @classmethod
    def initial(cls) -> FencingToken:
        """Return the initial token value."""

        return cls(0)

    def next(self) -> FencingToken:
        """Return the next token without mutating this value."""

        return type(self)(self.value + 1)
