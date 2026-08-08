"""Typed repository and specialized UoW contracts for Task Management #91."""

from __future__ import annotations

from inspect import getattr_static, getmro, signature
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.modules.task_management.application import (
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
from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

pytestmark = pytest.mark.contract


def test_repository_ports_are_typed_and_do_not_own_transactions() -> None:
    for repository in (TaskRepositoryPort, RunRepositoryPort, StageRepositoryPort):
        for method in ("get", "add", "save"):
            assert callable(getattr(repository, method, None))
        assert not any(
            hasattr(repository, method) for method in ("commit", "rollback", "close")
        )
    task_get = get_type_hints(TaskRepositoryPort.get)
    run_get = get_type_hints(RunRepositoryPort.get)
    stage_get = get_type_hints(StageRepositoryPort.get)
    assert task_get == {"task_id": TaskId, "return": Task | None}
    assert run_get == {"run_id": RunId, "return": Run | None}
    assert stage_get == {
        "task_id": TaskId,
        "stage": StageReference,
        "return": Stage | None,
    }
    for repository, entity_name, expected_entity in (
        (TaskRepositoryPort, "task", Task),
        (RunRepositoryPort, "run", Run),
        (StageRepositoryPort, "stage", Stage),
    ):
        hints = get_type_hints(repository.save)
        assert hints[entity_name] is expected_entity
        assert hints["expected_revision"] is Revision
        assert "expected_revision" in signature(repository.save).parameters


def test_specialized_uow_reuses_root_lifecycle_and_exposes_typed_repositories() -> None:
    assert UnitOfWork in getmro(TaskManagementUnitOfWork)
    properties: tuple[tuple[property, type[object]], ...] = (
        (
            cast(property, getattr_static(TaskManagementUnitOfWork, "tasks")),
            TaskRepositoryPort,
        ),
        (
            cast(property, getattr_static(TaskManagementUnitOfWork, "runs")),
            RunRepositoryPort,
        ),
        (
            cast(property, getattr_static(TaskManagementUnitOfWork, "stages")),
            StageRepositoryPort,
        ),
    )
    for property_value, repository in properties:
        assert isinstance(property_value, property)
        assert property_value.fget is not None
        assert get_type_hints(property_value.fget)["return"] is repository
    assert not any(
        hasattr(TaskManagementUnitOfWork, name)
        for name in ("session", "registry", "get_repository")
    )
    factory_hints = get_type_hints(TaskManagementUnitOfWorkFactory.__call__)
    assert factory_hints["return"] is TaskManagementUnitOfWork
