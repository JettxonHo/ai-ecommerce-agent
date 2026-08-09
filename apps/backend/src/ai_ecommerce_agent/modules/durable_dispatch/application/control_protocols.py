"""Framework-neutral application protocol for Durable Dispatch controls."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain.snapshots import WorkIntentSnapshot
from .control_commands import (
    AcknowledgeWorkIntentStop,
    RequestWorkIntentCancellation,
    SupersedeWorkIntent,
)
from .control_queries import CheckOwnedWorkIntentControl
from .control_results import OwnedWorkIntentControlCheck, WorkIntentSupersessionResult


@runtime_checkable
class DurableDispatchControlApplication(Protocol):
    """Synchronous seam for persisted cancellation and supersession controls."""

    def check_owned_work_intent_control(
        self, query: CheckOwnedWorkIntentControl
    ) -> OwnedWorkIntentControlCheck: ...

    def request_work_intent_cancellation(
        self, command: RequestWorkIntentCancellation
    ) -> WorkIntentSnapshot: ...

    def supersede_work_intent(
        self, command: SupersedeWorkIntent
    ) -> WorkIntentSupersessionResult: ...

    def acknowledge_work_intent_stop(
        self, command: AcknowledgeWorkIntentStop
    ) -> WorkIntentSnapshot: ...


__all__ = ["DurableDispatchControlApplication"]
