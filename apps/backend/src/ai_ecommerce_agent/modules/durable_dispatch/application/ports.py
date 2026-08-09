"""Framework-neutral persistence ports owned by Durable Dispatch."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.shared_kernel import Revision

from ..domain.identity import DispatchId
from ..domain.snapshots import WorkIntentSnapshot
from .lease_commands import ClaimNextWorkIntent, HeartbeatWorkIntentLease


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
class WorkIntentLeaseRepositoryPort(Protocol):
    """Claim and heartbeat private Durable Dispatch Work Intent leases."""

    def claim_next(self, command: ClaimNextWorkIntent) -> WorkIntentSnapshot | None:
        """Claim at most one eligible Work Intent in the caller transaction."""

        ...

    def heartbeat(self, command: HeartbeatWorkIntentLease) -> WorkIntentSnapshot | None:
        """Extend one still-owned lease, or return ``None`` on mismatch."""

        ...


@runtime_checkable
class DurableDispatchUnitOfWork(UnitOfWork, Protocol):
    """One-shot UoW exposing only typed private Work Intent repositories."""

    @property
    def work_intents(self) -> WorkIntentRepositoryPort:
        """Repository capability owned by Durable Dispatch."""

        ...

    @property
    def work_intent_leases(self) -> WorkIntentLeaseRepositoryPort:
        """Private claim and heartbeat capability on the same transaction."""

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
    "WorkIntentLeaseRepositoryPort",
]
