"""Framework-neutral application protocol for Durable Dispatch leases."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain.snapshots import WorkIntentSnapshot
from .lease_commands import ClaimNextWorkIntent, HeartbeatWorkIntentLease


@runtime_checkable
class DurableDispatchLeaseApplication(Protocol):
    """Synchronous claim and heartbeat use-case surface."""

    def claim_next_work_intent(
        self, command: ClaimNextWorkIntent
    ) -> WorkIntentSnapshot | None:
        """Claim at most one eligible Work Intent, or return ``None``."""

        ...

    def heartbeat_work_intent_lease(
        self, command: HeartbeatWorkIntentLease
    ) -> WorkIntentSnapshot:
        """Refresh one database-authoritative Lease."""

        ...


__all__ = ["DurableDispatchLeaseApplication"]
