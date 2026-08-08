"""Immutable results composed only of public Task/Run/Stage snapshots."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.modules.task_management.domain import (
    RunSnapshot,
    StageSnapshot,
    TaskSnapshot,
)


@dataclass(frozen=True, slots=True)
class PrepareInitialRunResult:
    """The atomic initial Task/Run/Stage projection."""

    task: TaskSnapshot
    run: RunSnapshot
    stage: StageSnapshot


__all__ = ["PrepareInitialRunResult"]
