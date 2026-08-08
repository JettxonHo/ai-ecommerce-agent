"""Explicit SQLAlchemy RowMapping ↔ domain conversions.

The database schema owns primitive type/nullability checks.  This adapter
performs only value-object conversion and the meaningful paired-version check;
no SQLAlchemy row or ORM object leaves infrastructure.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import cast

from ai_ecommerce_agent.modules.task_management.domain import (
    DomainVersionReference,
    Run,
    RunStatus,
    Stage,
    StageReference,
    StageStatus,
    Task,
    TaskStatus,
)
from ai_ecommerce_agent.shared_kernel import (
    DomainVersionId,
    Revision,
    RunId,
    TaskId,
    VersionNumber,
)


def _text(row: Mapping[str, object], name: str) -> str:
    return cast(str, row[name])


def _nullable_text(row: Mapping[str, object], name: str) -> str | None:
    return cast(str | None, row[name])


def _integer(row: Mapping[str, object], name: str) -> int:
    return cast(int, row[name])


def _nullable_integer(row: Mapping[str, object], name: str) -> int | None:
    return cast(int | None, row[name])


def _timestamp(row: Mapping[str, object], name: str) -> datetime:
    return cast(datetime, row[name])


def _nullable_timestamp(row: Mapping[str, object], name: str) -> datetime | None:
    return cast(datetime | None, row[name])


def _version(
    version_id: str | None, version_number: int | None
) -> DomainVersionReference | None:
    if version_id is None and version_number is None:
        return None
    if version_id is None or version_number is None:
        raise ValueError("database version reference must contain both values")
    return DomainVersionReference(
        DomainVersionId(version_id), VersionNumber(version_number)
    )


def _version_values(
    version: DomainVersionReference | None,
) -> tuple[str | None, int | None]:
    if version is None:
        return None, None
    return str(version.version_id), version.version_number.value


def task_row_to_domain(row: Mapping[str, object]) -> Task:
    """Map one ``task_management_tasks`` RowMapping to ``Task``."""

    current_stage = _nullable_text(row, "current_stage")
    active_run_id = _nullable_text(row, "active_run_id")
    latest_run_id = _nullable_text(row, "latest_run_id")
    return Task(
        task_id=TaskId(_text(row, "task_id")),
        task_name=_text(row, "task_name"),
        product_category=_text(row, "product_category"),
        promotion_goal=_text(row, "promotion_goal"),
        task_status=TaskStatus(_text(row, "task_status")),
        revision=Revision(_integer(row, "revision")),
        current_stage=StageReference(current_stage) if current_stage else None,
        active_run_id=RunId(active_run_id) if active_run_id else None,
        latest_run_id=RunId(latest_run_id) if latest_run_id else None,
        waiting_reason=_nullable_text(row, "waiting_reason"),
        updated_at=_timestamp(row, "updated_at"),
    )


def task_domain_to_row(task: Task) -> dict[str, object]:
    """Map one Task to SQLAlchemy Core insert/update primitives."""

    return {
        "task_id": str(task.task_id),
        "task_name": task.task_name,
        "product_category": task.product_category,
        "promotion_goal": task.promotion_goal,
        "task_status": task.task_status.value,
        "revision": task.revision.value,
        "current_stage": task.current_stage.value if task.current_stage else None,
        "active_run_id": str(task.active_run_id) if task.active_run_id else None,
        "latest_run_id": str(task.latest_run_id) if task.latest_run_id else None,
        "waiting_reason": task.waiting_reason,
        "updated_at": task.updated_at,
    }


def run_row_to_domain(row: Mapping[str, object]) -> Run:
    """Map one ``task_management_runs`` RowMapping to ``Run``."""

    source_run_id = _nullable_text(row, "source_run_id")
    current_stage = _nullable_text(row, "current_stage")
    return Run(
        run_id=RunId(_text(row, "run_id")),
        task_id=TaskId(_text(row, "task_id")),
        source_run_id=RunId(source_run_id) if source_run_id else None,
        status=RunStatus(_text(row, "status")),
        revision=Revision(_integer(row, "revision")),
        current_stage=StageReference(current_stage) if current_stage else None,
        started_at=_nullable_timestamp(row, "started_at"),
        updated_at=_timestamp(row, "updated_at"),
        completed_at=_nullable_timestamp(row, "completed_at"),
        failure_summary=_nullable_text(row, "failure_summary"),
        last_valid_result=_version(
            _nullable_text(row, "last_valid_result_version_id"),
            _nullable_integer(row, "last_valid_result_version_number"),
        ),
    )


def run_domain_to_row(run: Run) -> dict[str, object]:
    """Map one Run to SQLAlchemy Core insert/update primitives."""

    version_id, version_number = _version_values(run.last_valid_result)
    return {
        "run_id": str(run.run_id),
        "task_id": str(run.task_id),
        "source_run_id": str(run.source_run_id) if run.source_run_id else None,
        "status": run.status.value,
        "revision": run.revision.value,
        "current_stage": run.current_stage.value if run.current_stage else None,
        "started_at": run.started_at,
        "updated_at": run.updated_at,
        "completed_at": run.completed_at,
        "failure_summary": run.failure_summary,
        "last_valid_result_version_id": version_id,
        "last_valid_result_version_number": version_number,
    }


def stage_row_to_domain(row: Mapping[str, object]) -> Stage:
    """Map one ``task_management_stages`` RowMapping to ``Stage``."""

    last_run_id = _nullable_text(row, "last_run_id")
    return Stage(
        task_id=TaskId(_text(row, "task_id")),
        stage=StageReference(_text(row, "stage")),
        status=StageStatus(_text(row, "status")),
        revision=Revision(_integer(row, "revision")),
        current_version=_version(
            _nullable_text(row, "current_version_id"),
            _nullable_integer(row, "current_version_number"),
        ),
        last_valid_version=_version(
            _nullable_text(row, "last_valid_version_id"),
            _nullable_integer(row, "last_valid_version_number"),
        ),
        last_run_id=RunId(last_run_id) if last_run_id else None,
        waiting_reason=_nullable_text(row, "waiting_reason"),
        updated_at=_timestamp(row, "updated_at"),
    )


def stage_domain_to_row(stage: Stage) -> dict[str, object]:
    """Map one Stage to SQLAlchemy Core insert/update primitives."""

    current_id, current_number = _version_values(stage.current_version)
    last_id, last_number = _version_values(stage.last_valid_version)
    return {
        "task_id": str(stage.task_id),
        "stage": stage.stage.value,
        "status": stage.status.value,
        "revision": stage.revision.value,
        "current_version_id": current_id,
        "current_version_number": current_number,
        "last_valid_version_id": last_id,
        "last_valid_version_number": last_number,
        "last_run_id": str(stage.last_run_id) if stage.last_run_id else None,
        "waiting_reason": stage.waiting_reason,
        "updated_at": stage.updated_at,
    }


__all__ = [
    "run_domain_to_row",
    "run_row_to_domain",
    "stage_domain_to_row",
    "stage_row_to_domain",
    "task_domain_to_row",
    "task_row_to_domain",
]
