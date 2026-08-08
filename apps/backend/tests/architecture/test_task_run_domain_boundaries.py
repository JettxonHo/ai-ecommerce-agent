"""Narrow architecture checks for the A2 Task/Run domain boundary."""

from dataclasses import fields

import pytest

from ai_ecommerce_agent.modules.task_management import public
from ai_ecommerce_agent.modules.task_management.domain import Run, Task

pytestmark = pytest.mark.architecture


def test_a2_entities_are_internal_and_do_not_expand_public_facade() -> None:
    assert "Task" not in public.__all__
    assert "Run" not in public.__all__
    assert not hasattr(public, "Task")
    assert not hasattr(public, "Run")
    assert {field.name for field in fields(Task)} >= {
        "active_run_id",
        "latest_run_id",
        "task_status",
    }
    assert "thread_id" not in {field.name for field in fields(Run)}
    assert "stages" not in {field.name for field in fields(Task)}
