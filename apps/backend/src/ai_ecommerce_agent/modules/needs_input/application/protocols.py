"""Narrow application protocol consumed by result and HTTP adapters."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_ecommerce_agent.shared_kernel import TaskId

from ..domain.evidence import InsufficientResultEvidence
from ..domain.snapshots import NeedsInputActionRequestSnapshot
from .commands import ResolveNeedsInput
from .results import ResolveNeedsInputResult


@runtime_checkable
class NeedsInputApplication(Protocol):
    def publish_from_result(
        self, evidence: InsufficientResultEvidence
    ) -> NeedsInputActionRequestSnapshot: ...

    def get_current_request(
        self, task_id: TaskId
    ) -> NeedsInputActionRequestSnapshot | None: ...

    def get_action_request(
        self, action_request_id: str
    ) -> NeedsInputActionRequestSnapshot: ...

    def resolve_needs_input(
        self, command: ResolveNeedsInput
    ) -> ResolveNeedsInputResult: ...


__all__ = ["NeedsInputApplication"]
