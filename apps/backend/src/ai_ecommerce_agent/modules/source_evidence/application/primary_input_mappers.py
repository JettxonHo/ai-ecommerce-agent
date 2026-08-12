"""Map the Task primary-input domain value to its public snapshot."""

from __future__ import annotations

from ..domain import PrimaryInputSnapshot, TaskPrimaryInput


def primary_input_to_snapshot(value: TaskPrimaryInput) -> PrimaryInputSnapshot:
    """Project only stable input identity, content and revision fields."""

    return PrimaryInputSnapshot(
        task_id=value.task_id,
        input_kind=value.input_kind,
        file_name=value.file_name,
        content=value.content,
        byte_count=value.byte_count,
        revision=value.revision,
        updated_at=value.updated_at,
    )


__all__ = ["primary_input_to_snapshot"]
