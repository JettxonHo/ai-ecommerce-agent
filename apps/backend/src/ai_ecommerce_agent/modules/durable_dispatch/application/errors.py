"""Technology-neutral persistence errors for the private Durable adapter."""

from __future__ import annotations

from collections.abc import Mapping

from ai_ecommerce_agent.shared_kernel import ProjectError, Revision, SafeContext


class DurableDispatchPersistenceError(ProjectError):
    """A non-integrity database failure at the adapter boundary."""

    def __init__(self, context: Mapping[str, str] | None = None) -> None:
        super().__init__(
            "durable_dispatch", "persistence_error", SafeContext.from_mapping(context)
        )


class DurableDispatchRevisionConflictError(ProjectError):
    """A compare-and-swap update that affected no row."""

    def __init__(self, *, dispatch_id: str, expected_revision: Revision) -> None:
        super().__init__(
            "durable_dispatch",
            "revision_conflict",
            SafeContext.from_mapping(
                {
                    "dispatch_id": dispatch_id,
                    "expected_revision": str(expected_revision.value),
                }
            ),
        )


class DurableDispatchConstraintError(ProjectError):
    """An integrity constraint rejected an adapter persistence operation."""

    def __init__(self, *, constraint_name: str | None) -> None:
        super().__init__(
            "durable_dispatch",
            "constraint_violation",
            SafeContext.from_mapping(
                {"constraint": constraint_name} if constraint_name is not None else None
            ),
        )


__all__ = [
    "DurableDispatchConstraintError",
    "DurableDispatchPersistenceError",
    "DurableDispatchRevisionConflictError",
]
