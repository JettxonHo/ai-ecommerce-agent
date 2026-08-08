"""Narrow architecture locks for the Task Management adapter boundary."""

from __future__ import annotations

import pytest

import ai_ecommerce_agent.modules.task_management.infrastructure as infrastructure
from ai_ecommerce_agent.modules.task_management import public
from ai_ecommerce_agent.modules.task_management.infrastructure import (
    TaskManagementPostgresUnitOfWorkFactory,
)

pytestmark = pytest.mark.architecture


def test_public_facade_and_adapter_facade_stay_narrow() -> None:
    assert set(public.__all__) == {
        "DomainVersionReference",
        "RunSnapshot",
        "RunStatus",
        "StageReference",
        "StageSnapshot",
        "StageStatus",
        "TaskSnapshot",
        "TaskStatus",
    }
    assert set(infrastructure.__all__) == {"TaskManagementPostgresUnitOfWorkFactory"}
    assert not hasattr(public, "TaskManagementPostgresUnitOfWorkFactory")
    assert not hasattr(infrastructure, "Session")
    assert not hasattr(infrastructure, "registry")
    assert isinstance(TaskManagementPostgresUnitOfWorkFactory, type)
