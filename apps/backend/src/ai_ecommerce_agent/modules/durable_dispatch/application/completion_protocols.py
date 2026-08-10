"""Framework-neutral participant protocol for final completion coordination."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .completion_commands import CompleteOwnedWorkIntent
from .completion_results import WorkIntentCompletionResult


@runtime_checkable
class DurableDispatchCommitFenceParticipant(Protocol):
    """Transaction-neutral completion participant bound by a future outer UoW."""

    def complete_owned_work_intent(
        self, command: CompleteOwnedWorkIntent
    ) -> WorkIntentCompletionResult: ...


__all__ = ["DurableDispatchCommitFenceParticipant"]
