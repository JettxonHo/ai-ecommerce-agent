"""Public facade and application-port contracts for MVP0-009A."""

from __future__ import annotations

from dataclasses import is_dataclass
from types import TracebackType
from typing import Self

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWorkState
from ai_ecommerce_agent.modules.task_management import public
from ai_ecommerce_agent.modules.task_management.application.ports import (
    RunRepositoryPort,
    StageRepositoryPort,
    TaskManagementUnitOfWork,
    TaskManagementUnitOfWorkFactory,
    TaskRepositoryPort,
)
from ai_ecommerce_agent.modules.task_management.domain import (
    Run,
    Stage,
    StageReference,
    Task,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    RunId,
    TaskId,
)

pytestmark = pytest.mark.contract

_PUBLIC_NAMES = {
    "DomainVersionReference",
    "InvalidTransitionError",
    "OwnershipError",
    "RevisionConflictError",
    "RunNotFoundError",
    "RunSnapshot",
    "RunStatus",
    "StageNotFoundError",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "TaskManagementApplicationError",
    "TaskManagementDomainError",
    "TaskNotFoundError",
    "TaskSnapshot",
    "TaskStatus",
}


def test_task_management_facade_is_the_snapshot_catalog_and_error_boundary() -> None:
    assert set(public.__all__) == _PUBLIC_NAMES
    assert not hasattr(public, "Task")
    assert not hasattr(public, "Run")
    assert not hasattr(public, "Stage")
    assert not hasattr(public, "TaskRepositoryPort")
    assert not hasattr(public, "TaskManagementUnitOfWork")

    for snapshot in (public.TaskSnapshot, public.RunSnapshot, public.StageSnapshot):
        assert is_dataclass(snapshot)
        assert not hasattr(snapshot, "from_domain")

    assert "thread_id" not in public.RunSnapshot.__dataclass_fields__
    assert "last_valid_result" in public.RunSnapshot.__dataclass_fields__

    not_found = public.TaskNotFoundError("task-01")
    assert not_found.category == "task_management.application"
    assert not_found.code == "task_not_found"
    assert not_found.safe_context == {"taskId": "task-01"}


class _TaskRepository:
    def get(self, task_id: TaskId) -> Task | None:
        return None

    def add(self, task: Task) -> None:
        del task

    def save(self, task: Task, *, expected_revision: Revision) -> None:
        del task, expected_revision


class _RunRepository:
    def get(self, run_id: RunId) -> Run | None:
        return None

    def add(self, run: Run) -> None:
        del run

    def save(self, run: Run, *, expected_revision: Revision) -> None:
        del run, expected_revision


class _StageRepository:
    def get(self, task_id: TaskId, stage: StageReference) -> Stage | None:
        return None

    def add(self, stage: Stage) -> None:
        del stage

    def save(self, stage: Stage, *, expected_revision: Revision) -> None:
        del stage, expected_revision


class _UnitOfWork:
    state = UnitOfWorkState.NEW

    @property
    def tasks(self) -> TaskRepositoryPort:
        return _TaskRepository()

    @property
    def runs(self) -> RunRepositoryPort:
        return _RunRepository()

    @property
    def stages(self) -> StageRepositoryPort:
        return _StageRepository()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc_value, traceback

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def close(self) -> None:
        return None


def test_application_ports_are_typed_and_technical_free() -> None:
    assert isinstance(_TaskRepository(), TaskRepositoryPort)
    assert isinstance(_RunRepository(), RunRepositoryPort)
    assert isinstance(_StageRepository(), StageRepositoryPort)
    assert isinstance(_UnitOfWork(), TaskManagementUnitOfWork)
    assert isinstance(lambda: _UnitOfWork(), TaskManagementUnitOfWorkFactory)
    assert "sqlalchemy" not in TaskRepositoryPort.__module__
    assert "Session" not in (TaskRepositoryPort.__doc__ or "")
