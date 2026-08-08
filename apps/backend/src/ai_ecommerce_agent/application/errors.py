"""Application-owned lifecycle errors.

The errors in this module deliberately depend only on the shared error value.
Infrastructure adapters may preserve the original driver failure while using
these errors for invalid application lifecycle operations.
"""

from __future__ import annotations

from collections.abc import Mapping

from ai_ecommerce_agent.shared_kernel.errors import ProjectError, SafeContext


class UnitOfWorkError(ProjectError):
    """Base project-owned error for Unit of Work lifecycle failures."""

    def __init__(
        self,
        code: str = "uow_error",
        context: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__("application", code, SafeContext.from_mapping(context))


class UnitOfWorkStateError(UnitOfWorkError):
    """An operation was attempted from an invalid Unit of Work state.

    The stable error code and safe ``operation``/``state`` context identify
    the rejected transition without a separate class for every combination.
    """


__all__ = [
    "UnitOfWorkError",
    "UnitOfWorkStateError",
]
