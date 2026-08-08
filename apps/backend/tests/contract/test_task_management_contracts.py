"""A1 public facade and immutable snapshot contract tests."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from typing import get_type_hints

import pytest

from ai_ecommerce_agent.modules.task_management import public

pytestmark = pytest.mark.contract

_PUBLIC_NAMES = {
    "DomainVersionReference",
    "RunSnapshot",
    "RunStatus",
    "StageReference",
    "StageSnapshot",
    "StageStatus",
    "TaskSnapshot",
    "TaskStatus",
}

_UPDATED_AT = datetime(2026, 8, 8, 0, 0, tzinfo=UTC)


def test_task_management_facade_exports_only_a1_contracts() -> None:
    assert set(public.__all__) == _PUBLIC_NAMES
    assert not hasattr(public, "Task")
    assert not hasattr(public, "Run")
    assert not hasattr(public, "Stage")
    assert not hasattr(public, "TaskManagementApplicationError")
    assert not hasattr(public, "TaskManagementDomainError")
    assert not hasattr(public, "TaskNotFoundError")

    for snapshot in (public.TaskSnapshot, public.RunSnapshot, public.StageSnapshot):
        assert is_dataclass(snapshot)
        assert not hasattr(snapshot, "from_domain")
        assert not any(
            callable(getattr(snapshot, field.name, None)) for field in fields(snapshot)
        )

    task_fields = {field.name for field in fields(public.TaskSnapshot)}
    assert "task_status" in task_fields
    assert "status" not in task_fields
    assert "active_run_id" in task_fields
    assert "current_run_id" not in task_fields
    assert get_type_hints(public.TaskSnapshot)["updated_at"] is datetime

    for snapshot in (public.RunSnapshot, public.StageSnapshot):
        assert get_type_hints(snapshot)["updated_at"] is datetime
    assert "thread_id" not in public.RunSnapshot.__dataclass_fields__
    assert "last_valid_result" in public.RunSnapshot.__dataclass_fields__
    assert _UPDATED_AT.tzinfo is UTC
