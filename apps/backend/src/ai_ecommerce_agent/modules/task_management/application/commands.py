"""Immutable application commands for the Task Management vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId


@dataclass(frozen=True, slots=True)
class CreateDraftTask:
    """Create one stable draft Task in the fixed workspace."""

    task_id: TaskId
    task_name: str
    product_category: str
    promotion_goal: str
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class PrepareInitialRun:
    """Prepare the initial queued Run and ready Fact Stage for a draft Task.

    This is deliberately a Current Truth preparation use case.  It does not
    claim or execute a Run; Worker lease/fencing belongs to a later slice.
    Callers/future composites are responsible for the accepted Fact Stage
    input gate and durable-dispatch coordination.  This primitive neither
    validates that Source gate nor creates a WorkIntent or Receipt.
    """

    task_id: TaskId
    run_id: RunId
    expected_revision: Revision
    updated_at: datetime


__all__ = [
    "CreateDraftTask",
    "PrepareInitialRun",
]
