"""Framework-neutral persistence ports owned by Durable Dispatch."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.shared_kernel import Revision

from ..domain.identity import DispatchId
from ..domain.snapshots import WorkIntentSnapshot


@runtime_checkable
class WorkIntentRepositoryPort(Protocol):
    """Load and revision-save Durable Dispatch Work Intent snapshots."""

    def get(self, dispatch_id: DispatchId) -> WorkIntentSnapshot | None:
        """Return the current snapshot for an identity, or ``None``."""

        ...

    def add(self, snapshot: WorkIntentSnapshot) -> None:
        """Stage a new snapshot without owning the transaction."""

        ...

    def save(
        self,
        snapshot: WorkIntentSnapshot,
        *,
        expected_revision: Revision,
    ) -> None:
        """CAS-save a snapshot without owning the transaction."""

        ...


@runtime_checkable
class DurableDispatchUnitOfWork(UnitOfWork, Protocol):
    """One-shot UoW exposing only the typed Work Intent repository."""

    @property
    def work_intents(self) -> WorkIntentRepositoryPort:
        """Repository capability owned by Durable Dispatch."""

        ...


@runtime_checkable
class DurableDispatchUnitOfWorkFactory(Protocol):
    """Create one fresh Durable Dispatch UoW per transactional command."""

    def __call__(self) -> DurableDispatchUnitOfWork:
        """Return a new one-shot UoW with private transaction resources."""

        ...


__all__ = [
    "DurableDispatchUnitOfWork",
    "DurableDispatchUnitOfWorkFactory",
    "WorkIntentRepositoryPort",
]
