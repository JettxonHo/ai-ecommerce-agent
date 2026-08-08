"""Contract checks for the private Task Management PostgreSQL adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from inspect import getattr_static, getmro
from typing import get_type_hints

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
from ai_ecommerce_agent.modules.task_management.infrastructure.repositories import (
    TaskManagementPostgresRunRepository,
    TaskManagementPostgresStageRepository,
    TaskManagementPostgresTaskRepository,
)
from ai_ecommerce_agent.modules.task_management.infrastructure.tables import (
    RUNS_TABLE,
    STAGES_TABLE,
    TASK_MANAGEMENT_SCHEMA_TOKEN,
    TASKS_TABLE,
)
from ai_ecommerce_agent.modules.task_management.infrastructure.uow import (
    TaskManagementPostgresUnitOfWork,
    TaskManagementPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.shared_kernel import RunId, TaskId

pytestmark = pytest.mark.contract


def test_concrete_repositories_satisfy_typed_ports_without_lifecycle_methods() -> None:
    assert isinstance(TaskManagementPostgresTaskRepository, type)
    assert isinstance(TaskManagementPostgresRunRepository, type)
    assert isinstance(TaskManagementPostgresStageRepository, type)
    for port, methods in (
        (TaskRepositoryPort, ("get", "add", "save")),
        (RunRepositoryPort, ("get", "add", "save")),
        (StageRepositoryPort, ("get", "add", "save")),
    ):
        assert all(callable(getattr(port, method, None)) for method in methods)
        assert not any(
            hasattr(port, method) for method in ("commit", "rollback", "close")
        )


def test_specialized_uow_reuses_root_port_and_hides_session_registry() -> None:
    assert isinstance(TaskManagementPostgresUnitOfWork, type)
    assert UnitOfWork in getmro(TaskManagementUnitOfWork)
    for name in ("tasks", "runs", "stages"):
        property_value = getattr_static(TaskManagementUnitOfWork, name)
        assert isinstance(property_value, property)
    assert not any(
        hasattr(TaskManagementPostgresUnitOfWork, name)
        for name in ("session", "registry", "get_repository")
    )
    assert (
        get_type_hints(TaskManagementUnitOfWorkFactory.__call__)["return"]
        is TaskManagementUnitOfWork
    )
    assert isinstance(TaskManagementPostgresUnitOfWorkFactory, type)


def test_metadata_matches_merged_migration_columns_and_schema_token() -> None:
    assert all(
        table.schema == TASK_MANAGEMENT_SCHEMA_TOKEN
        for table in (TASKS_TABLE, RUNS_TABLE, STAGES_TABLE)
    )
    assert [column.name for column in TASKS_TABLE.columns] == [
        "task_id",
        "task_name",
        "product_category",
        "promotion_goal",
        "task_status",
        "revision",
        "current_stage",
        "active_run_id",
        "latest_run_id",
        "waiting_reason",
        "updated_at",
    ]
    assert [column.name for column in RUNS_TABLE.columns] == [
        "run_id",
        "task_id",
        "source_run_id",
        "status",
        "revision",
        "current_stage",
        "started_at",
        "updated_at",
        "completed_at",
        "failure_summary",
        "last_valid_result_version_id",
        "last_valid_result_version_number",
    ]
    assert [column.name for column in STAGES_TABLE.columns] == [
        "task_id",
        "stage",
        "status",
        "revision",
        "current_version_id",
        "current_version_number",
        "last_valid_version_id",
        "last_valid_version_number",
        "last_run_id",
        "waiting_reason",
        "updated_at",
    ]
    constraint_names = {
        constraint.name
        for table in (TASKS_TABLE, RUNS_TABLE, STAGES_TABLE)
        for constraint in table.constraints
    }
    assert {
        "fk_task_management_runs_current_stage_owner",
        "fk_task_management_tasks_active_run_owner",
        "fk_task_management_tasks_latest_run_owner",
        "fk_task_management_tasks_current_stage_owner",
    } <= constraint_names


def test_domain_mapping_is_explicit_and_roundtrips() -> None:
    from ai_ecommerce_agent.modules.task_management.infrastructure.mappings import (
        run_domain_to_row,
        run_row_to_domain,
        stage_domain_to_row,
        stage_row_to_domain,
        task_domain_to_row,
        task_row_to_domain,
    )

    now = datetime(2026, 8, 9, tzinfo=UTC)
    task = Task.create(
        TaskId("contract-task"),
        task_name="Name",
        product_category="Category",
        promotion_goal="Goal",
        updated_at=now,
    )
    run = Run.create(RunId("contract-run"), task.task_id, updated_at=now)
    stage = Stage.create(task.task_id, StageReference.HUMAN_REVIEW, updated_at=now)
    assert task_row_to_domain(task_domain_to_row(task)) == task
    assert run_row_to_domain(run_domain_to_row(run)) == run
    assert stage_row_to_domain(stage_domain_to_row(stage)) == stage
