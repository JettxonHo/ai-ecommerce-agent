"""Synchronous, framework-neutral persistence ports.

Only lifecycle and transaction operations belong on the shared Unit of Work
port.  Business modules add typed repository ports of their own; this module
does not provide a generic repository registry or a raw session escape hatch.
"""

from __future__ import annotations

from enum import StrEnum
from types import TracebackType
from typing import Protocol, Self, runtime_checkable


class UnitOfWorkState(StrEnum):
    """One-shot Unit of Work lifecycle states."""

    NEW = "NEW"
    ACTIVE = "ACTIVE"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"
    CLOSED = "CLOSED"


@runtime_checkable
class UnitOfWork(Protocol):
    """Application-owned synchronous disposable Unit of Work capability."""

    @property
    def state(self) -> UnitOfWorkState:
        """Return the current lifecycle state."""

        ...

    def __enter__(self) -> Self:
        """Enter the short transaction and return this Unit of Work."""

        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Rollback on an uncommitted exit and always close resources."""

        ...

    def commit(self) -> None:
        """Explicitly perform the single final business commit."""

        ...

    def rollback(self) -> None:
        """Explicitly roll back the active transaction."""

        ...

    def close(self) -> None:
        """Close and release the short-lived transaction resources."""

        ...


@runtime_checkable
class UnitOfWorkFactory(Protocol):
    """Factory for a fresh Unit of Work per transactional command."""

    def __call__(self) -> UnitOfWork:
        """Create a new one-shot Unit of Work."""

        ...


__all__ = [
    "UnitOfWork",
    "UnitOfWorkFactory",
    "UnitOfWorkState",
]
