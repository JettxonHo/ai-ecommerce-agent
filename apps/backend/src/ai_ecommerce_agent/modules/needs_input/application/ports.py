"""Typed repository and transaction ports owned by Needs Input."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Protocol, Self, runtime_checkable

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

from ..domain.snapshots import NeedsInputActionRequestSnapshot


@runtime_checkable
class NeedsInputRequestRepository(Protocol):
    def get(self, action_request_id: str) -> NeedsInputActionRequestSnapshot | None: ...

    def get_current(
        self, task_id: TaskId
    ) -> NeedsInputActionRequestSnapshot | None: ...

    def add(self, request: NeedsInputActionRequestSnapshot) -> None: ...

    def save(
        self,
        request: NeedsInputActionRequestSnapshot,
        *,
        expected_revision: Revision,
    ) -> None: ...


@runtime_checkable
class NeedsInputUnitOfWork(Protocol):
    @property
    def needs_input_requests(self) -> NeedsInputRequestRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


type NeedsInputUnitOfWorkFactory = Callable[[], NeedsInputUnitOfWork]


__all__ = [
    "NeedsInputRequestRepository",
    "NeedsInputUnitOfWork",
    "NeedsInputUnitOfWorkFactory",
]
