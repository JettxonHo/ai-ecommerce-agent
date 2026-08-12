"""Immutable queries for Task-scoped primary input."""

from __future__ import annotations

from dataclasses import dataclass

from ai_ecommerce_agent.shared_kernel import TaskId


@dataclass(frozen=True, slots=True)
class GetPrimaryInput:
    """Read the current primary input for one Task."""

    task_id: TaskId


__all__ = ["GetPrimaryInput"]
