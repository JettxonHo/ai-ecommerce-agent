"""Contract checks for the private Task Management PostgreSQL adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from inspect import getattr_static, getmro
from typing import NoReturn, cast, get_type_hints

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.modules.task_management.application import (
    RunRepositoryPort,
    StageRepositoryPort,
    TaskManagementOwnershipError,
    TaskManagementPersistenceError,
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


class _ExecuteFailureSession:
    def __init__(self, error: BaseException) -> None:
        self._error = error

    def execute(self, statement: object) -> NoReturn:
        del statement
        raise self._error


class _Diagnostic:
    def __init__(self, constraint_name: str) -> None:
        self.constraint_name = constraint_name


class _DriverIntegrityError(Exception):
    def __init__(self, constraint_name: str) -> None:
        super().__init__("integrity failure")
        self.diag = _Diagnostic(constraint_name)


class _LifecycleSession:
    def __init__(
        self,
        *,
        begin_error: BaseException | None = None,
        commit_error: BaseException | None = None,
    ) -> None:
        self.begin_error = begin_error
        self.commit_error = commit_error
        self.begin_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    def begin(self) -> None:
        self.begin_calls += 1
        if self.begin_error is not None:
            raise self.begin_error

    def commit(self) -> None:
        self.commit_calls += 1
        if self.commit_error is not None:
            raise self.commit_error

    def rollback(self) -> None:
        self.rollback_calls += 1

    def close(self) -> None:
        self.close_calls += 1


def _error_boundary_task() -> Task:
    return Task.create(
        TaskId("error-boundary-task"),
        task_name="Error boundary task",
        product_category="backpack",
        promotion_goal="error boundary",
        updated_at=datetime(2026, 8, 9, tzinfo=UTC),
    )


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


def test_repository_read_sqlalchemy_error_is_stable() -> None:
    error = SQLAlchemyError("read failed")
    session = _ExecuteFailureSession(error)
    repository = TaskManagementPostgresTaskRepository(cast(Session, session))

    with pytest.raises(TaskManagementPersistenceError) as raised:
        repository.get(TaskId("read-failure"))

    assert raised.value.__cause__ is error


def test_repository_integrity_mapping_precedes_generic_sqlalchemy_mapping() -> None:
    error = IntegrityError(
        "INSERT",
        {},
        _DriverIntegrityError("fk_task_management_runs_task_owner"),
    )
    session = _ExecuteFailureSession(error)
    repository = TaskManagementPostgresTaskRepository(cast(Session, session))

    with pytest.raises(TaskManagementOwnershipError) as raised:
        repository.add(_error_boundary_task())

    assert raised.value.safe_context["constraint"] == (
        "fk_task_management_runs_task_owner"
    )


def test_repository_programming_error_is_not_swallowed() -> None:
    session = _ExecuteFailureSession(RuntimeError("programming failure"))
    repository = TaskManagementPostgresTaskRepository(cast(Session, session))

    with pytest.raises(RuntimeError, match="programming failure"):
        repository.get(TaskId("programming-failure"))


def test_uow_begin_sqlalchemy_error_is_stable_and_closes() -> None:
    error = SQLAlchemyError("begin failed")
    session = _LifecycleSession(begin_error=error)
    uow = TaskManagementPostgresUnitOfWork(lambda: cast(Session, session))

    with pytest.raises(TaskManagementPersistenceError) as raised:
        uow.__enter__()

    assert raised.value.__cause__ is error
    assert session.begin_calls == 1
    assert session.close_calls == 1


def test_uow_commit_sqlalchemy_error_is_stable_after_rollback_and_close() -> None:
    error = SQLAlchemyError("commit failed")
    session = _LifecycleSession(commit_error=error)
    uow = TaskManagementPostgresUnitOfWork(lambda: cast(Session, session))

    with pytest.raises(TaskManagementPersistenceError) as raised:
        with uow:
            uow.commit()

    assert raised.value.__cause__ is error
    assert session.commit_calls == 1
    assert session.rollback_calls == 1
    assert session.close_calls == 1


def test_uow_programming_error_is_not_swallowed() -> None:
    session = _LifecycleSession(commit_error=RuntimeError("programming failure"))
    uow = TaskManagementPostgresUnitOfWork(lambda: cast(Session, session))

    with pytest.raises(RuntimeError, match="programming failure"):
        with uow:
            uow.commit()
