"""A1 public facade and immutable snapshot contract tests."""

from __future__ import annotations

from dataclasses import fields, is_dataclass

import pytest

from ai_ecommerce_agent.modules.task_management import public

pytestmark = pytest.mark.contract

_PUBLIC_NAMES = {
    "DomainVersionReference",
    "InvalidTransitionError",
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


def test_task_management_facade_exports_only_a1_contracts() -> None:
    assert set(public.__all__) == _PUBLIC_NAMES
    assert not hasattr(public, "Task")
    assert not hasattr(public, "Run")
    assert not hasattr(public, "Stage")
    assert not hasattr(public, "TaskRepositoryPort")
    assert not hasattr(public, "TaskManagementUnitOfWork")

    for snapshot in (public.TaskSnapshot, public.RunSnapshot, public.StageSnapshot):
        assert is_dataclass(snapshot)
        assert not hasattr(snapshot, "from_domain")
        assert not any(
            callable(getattr(snapshot, field.name, None)) for field in fields(snapshot)
        )

    assert "thread_id" not in public.RunSnapshot.__dataclass_fields__
    assert "last_valid_result" in public.RunSnapshot.__dataclass_fields__


def test_application_not_found_and_domain_conflict_errors_are_stable() -> None:
    not_found = public.TaskNotFoundError("task-01")
    assert not_found.category == "task_management.application"
    assert not_found.code == "task_not_found"
    assert not_found.safe_context == {"taskId": "task-01"}

    conflict = public.RevisionConflictError({"resource": "task"})
    assert conflict.category == "task_management.domain"
    assert conflict.code == "revision_conflict"
    assert conflict.safe_context == {"resource": "task"}
