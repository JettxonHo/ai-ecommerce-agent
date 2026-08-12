"""Immutable commands for Task-scoped primary input."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.shared_kernel import TaskId

from ..domain import PrimaryInputKind


@dataclass(frozen=True, slots=True)
class SavePrimaryInput:
    """Replace or replay one Task's current primary input."""

    task_id: TaskId
    input_kind: PrimaryInputKind
    file_name: str | None
    content: str
    updated_at: datetime


__all__ = ["SavePrimaryInput"]
