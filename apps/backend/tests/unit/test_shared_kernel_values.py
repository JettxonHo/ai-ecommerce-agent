"""Focused unit coverage for MVP0-006 shared value objects."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pytest

from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    ProjectError,
    Revision,
    RunId,
    SafeContext,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


def test_identity_types_are_opaque_and_not_interchangeable() -> None:
    task_id = TaskId("task-01")
    same_task_id = TaskId("task-01")
    run_id = RunId("task-01")

    assert task_id == same_task_id
    assert task_id != run_id
    assert str(task_id) == "task-01"
    assert task_id < TaskId("task-02")
    with pytest.raises(TypeError):
        _ = task_id < run_id  # type: ignore[operator]


def test_identity_rejects_empty_values_and_can_generate_application_ids() -> None:
    with pytest.raises(ValueError):
        TaskId("")
    with pytest.raises(ValueError):
        TaskId("   ")
    with pytest.raises(TypeError):
        TaskId(cast(Any, 1))

    generated = TaskId.new()
    assert isinstance(generated, TaskId)
    assert generated.value
    assert generated != TaskId.new()


def test_revision_is_non_negative_and_separate_from_version_number() -> None:
    initial = Revision.initial()
    assert initial.value == 0
    assert initial.next() == Revision(1)
    assert Revision(1) > initial
    assert Revision(1) != VersionNumber(1)

    with pytest.raises(ValueError):
        Revision(-1)
    with pytest.raises(TypeError):
        Revision(cast(Any, True))
    with pytest.raises(TypeError):
        Revision(cast(Any, 1.0))


def test_domain_version_identity_and_positive_number_stay_separate() -> None:
    version_id = DomainVersionId("version-01")
    version_number = VersionNumber.initial()
    assert version_id == DomainVersionId("version-01")
    assert version_number == VersionNumber(1)
    assert VersionNumber(2) > version_number

    with pytest.raises(ValueError):
        VersionNumber(0)
    with pytest.raises(ValueError):
        VersionNumber(-1)
    with pytest.raises(TypeError):
        VersionNumber(cast(Any, False))


def test_safe_context_is_copied_and_read_only() -> None:
    source = {"resourceId": "task-01", "revision": "2"}
    error = ProjectError.from_context("conflict", "revision_conflict", source)
    source["resourceId"] = "changed"

    assert error.category == "conflict"
    assert error.code == "revision_conflict"
    assert error.safe_context == {"resourceId": "task-01", "revision": "2"}
    assert error == ProjectError.from_context(
        "conflict", "revision_conflict", {"resourceId": "task-01", "revision": "2"}
    )
    assert str(error) == "conflict:revision_conflict"
    assert error.args == ("conflict:revision_conflict",)
    assert isinstance(error, Exception)

    context = error.safe_context
    assert isinstance(context, Mapping)
    with pytest.raises(TypeError):
        context["new"] = "value"  # type: ignore[index]

    with pytest.raises(TypeError):
        SafeContext.from_mapping(cast(Any, {"key": 1}))


def test_project_error_rejects_invalid_context() -> None:
    with pytest.raises(TypeError):
        ProjectError(cast(Any, ""), "code")
    with pytest.raises(TypeError):
        ProjectError("category", cast(Any, ""))
    with pytest.raises(ValueError):
        SafeContext((("key", "value"), ("key", "other")))
    with pytest.raises(TypeError):
        SafeContext((("", "value"),))
