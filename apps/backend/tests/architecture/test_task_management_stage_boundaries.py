"""Narrow Stage/ownership boundary checks for #91."""

from dataclasses import fields

import pytest

from ai_ecommerce_agent.modules.task_management import public
from ai_ecommerce_agent.modules.task_management.application import ports
from ai_ecommerce_agent.modules.task_management.domain import Run, Stage, Task

pytestmark = pytest.mark.architecture


def test_stage_is_internal_and_task_remains_a_narrow_navigation_entity() -> None:
    assert "Stage" not in public.__all__
    assert not hasattr(public, "Stage")
    assert "stages" not in {field.name for field in fields(Task)}
    assert {"task_id", "stage", "status", "current_version", "last_valid_version"} <= {
        field.name for field in fields(Stage)
    }
    assert "thread_id" not in {field.name for field in fields(Run)}


def test_task_management_ports_are_module_private_and_framework_neutral() -> None:
    assert set(ports.__all__) == {
        "RunRepositoryPort",
        "StageRepositoryPort",
        "TaskManagementUnitOfWork",
        "TaskManagementUnitOfWorkFactory",
        "TaskRepositoryPort",
    }
    assert not hasattr(ports, "Session")
    assert not hasattr(ports, "AsyncSession")
    assert not hasattr(ports, "registry")
