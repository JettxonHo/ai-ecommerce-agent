"""Publicly implementable application protocol for Task Management."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_ecommerce_agent.modules.task_management.domain import (
    RunSnapshot,
    StageSnapshot,
    TaskSnapshot,
)

from .commands import CreateDraftTask, PrepareInitialRun
from .queries import GetRun, GetStage, GetTask, ListTasks
from .results import PrepareInitialRunResult


@runtime_checkable
class TaskManagementApplication(Protocol):
    """Narrow use-case surface consumed by future API/orchestration adapters."""

    def create_draft_task(self, command: CreateDraftTask) -> TaskSnapshot:
        """Create one stable draft Task without idempotency semantics."""

        ...

    def create_draft_task_idempotent(
        self, command: CreateDraftTask
    ) -> tuple[TaskSnapshot, bool]:
        """Create or replay a draft Task using durable retry identity."""

        ...

    def get_task(self, query: GetTask) -> TaskSnapshot:
        """Read one immutable Task snapshot."""

        ...

    def list_tasks(self, query: ListTasks) -> tuple[TaskSnapshot, ...]:
        """Read a bounded recent Task summary window."""

        ...

    def get_run(self, query: GetRun) -> RunSnapshot:
        """Read one immutable Run snapshot."""

        ...

    def get_stage(self, query: GetStage) -> StageSnapshot:
        """Read one immutable Stage snapshot."""

        ...

    def prepare_initial_run(
        self, command: PrepareInitialRun
    ) -> PrepareInitialRunResult:
        """Atomically prepare the initial Run/Fact Stage Current Truth.

        Accepted input-gate and durable-dispatch work is coordinated by the
        caller; this primitive does not validate Source input or create a
        WorkIntent/Receipt.
        """

        ...


__all__ = ["TaskManagementApplication"]
