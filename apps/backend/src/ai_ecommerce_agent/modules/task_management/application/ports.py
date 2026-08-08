"""Typed, module-owned repository and Unit of Work ports.

These interfaces are intentionally private to the Task Management
application layer.  Infrastructure will implement them in a later slice;
cross-module callers use only ``modules.task_management.public``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

from ..domain import Run, Stage, StageReference, Task


@runtime_checkable
class TaskRepositoryPort(Protocol):
    """Load and persist Task navigation/current Run pointers."""

    def get(self, task_id: TaskId) -> Task | None:
        """Return the owned Task entity, or ``None`` if absent."""

        ...

    def add(self, task: Task) -> None:
        """Stage a newly-created Task for the current application commit."""

        ...

    def save(self, task: Task, *, expected_revision: Revision) -> None:
        """CAS-save a changed Task entity without owning the transaction."""

        ...


@runtime_checkable
class RunRepositoryPort(Protocol):
    """Load and persist Task-scoped Run monitor snapshots."""

    def get(self, run_id: RunId) -> Run | None:
        """Return the owned Run entity, or ``None`` if absent."""

        ...

    def add(self, run: Run) -> None:
        """Stage a newly-created Run for the current application commit."""

        ...

    def save(self, run: Run, *, expected_revision: Revision) -> None:
        """CAS-save a changed Run entity without owning the transaction."""

        ...


@runtime_checkable
class StageRepositoryPort(Protocol):
    """Load and persist one Task-scoped Stage Current Truth record."""

    def get(self, task_id: TaskId, stage: StageReference) -> Stage | None:
        """Return the owned Task/Stage pair, or ``None`` if absent."""

        ...

    def add(self, stage: Stage) -> None:
        """Stage a new Task/Stage record for the current application commit."""

        ...

    def save(self, stage: Stage, *, expected_revision: Revision) -> None:
        """CAS-save a changed Stage without owning the transaction."""

        ...


@runtime_checkable
class TaskManagementUnitOfWork(UnitOfWork, Protocol):
    """Specialized UoW exposing only typed Task Management repositories."""

    @property
    def tasks(self) -> TaskRepositoryPort:
        """Task navigation repository owned by this module."""

        ...

    @property
    def runs(self) -> RunRepositoryPort:
        """Run monitor repository owned by this module."""

        ...

    @property
    def stages(self) -> StageRepositoryPort:
        """Stage Current Truth repository owned by this module."""

        ...


@runtime_checkable
class TaskManagementUnitOfWorkFactory(Protocol):
    """Create one fresh specialized UoW per transactional command."""

    def __call__(self) -> TaskManagementUnitOfWork:
        """Return a new one-shot UoW; implementations own its lifecycle."""

        ...


__all__ = [
    "RunRepositoryPort",
    "StageRepositoryPort",
    "TaskManagementUnitOfWork",
    "TaskManagementUnitOfWorkFactory",
    "TaskRepositoryPort",
]
