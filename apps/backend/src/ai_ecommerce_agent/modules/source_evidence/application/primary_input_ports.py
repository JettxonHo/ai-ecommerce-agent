"""Framework-neutral persistence ports for Task primary input."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.shared_kernel import Revision, TaskId

from ..domain import TaskPrimaryInput


@runtime_checkable
class PrimaryInputRepositoryPort(Protocol):
    """Load and CAS-save one current primary input per Task."""

    def get(self, task_id: TaskId) -> TaskPrimaryInput | None:
        """Return the current input or ``None``."""

        ...

    def add(self, value: TaskPrimaryInput) -> None:
        """Stage a first input row."""

        ...

    def save(self, value: TaskPrimaryInput, *, expected_revision: Revision) -> None:
        """CAS-save a changed input without owning the transaction."""

        ...


@runtime_checkable
class PrimaryInputUnitOfWork(UnitOfWork, Protocol):
    """One-shot UoW exposing only the primary-input repository."""

    @property
    def primary_inputs(self) -> PrimaryInputRepositoryPort:
        """Task primary-input repository."""

        ...


@runtime_checkable
class PrimaryInputUnitOfWorkFactory(Protocol):
    """Create a fresh primary-input transaction scope."""

    def __call__(self) -> PrimaryInputUnitOfWork:
        """Return a new one-shot UoW."""

        ...


__all__ = [
    "PrimaryInputRepositoryPort",
    "PrimaryInputUnitOfWork",
    "PrimaryInputUnitOfWorkFactory",
]
