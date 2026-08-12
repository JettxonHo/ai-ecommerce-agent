"""Focused unit contracts for the Task Management application slice."""

from __future__ import annotations

from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWorkState
from ai_ecommerce_agent.modules.task_management.application.errors import (
    TaskManagementConstraintError,
    TaskManagementRevisionConflictError,
)
from ai_ecommerce_agent.modules.task_management.application.ports import (
    RunRepositoryPort,
    StageRepositoryPort,
    TaskManagementUnitOfWork,
    TaskRepositoryPort,
)
from ai_ecommerce_agent.modules.task_management.application.services import (
    TaskManagementApplicationService,
)
from ai_ecommerce_agent.modules.task_management.domain import (
    Run,
    Stage,
    StageReference,
    Task,
)
from ai_ecommerce_agent.modules.task_management.public import (
    CreateDraftTask,
    GetTask,
    PrepareInitialRun,
    TaskManagementError,
    TaskManagementResourceKind,
    TaskManagementResourceReference,
)
from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

pytestmark = pytest.mark.unit

NOW = datetime(2026, 8, 9, 1, 0, tzinfo=UTC)
FACT_STAGE = StageReference.PRODUCT_INTAKE_AND_FACT_EXTRACTION


class _TaskRepository:
    def __init__(
        self,
        owner: _FakeUow,
        store: dict[TaskId, Task],
        idempotency: dict[str, TaskId],
    ) -> None:
        self._owner = owner
        self._store = store
        self._idempotency = idempotency

    def get(self, task_id: TaskId) -> Task | None:
        return self._store.get(task_id)

    def list(self, *, limit: int) -> tuple[Task, ...]:
        return tuple(self._store.values())[:limit]

    def add(self, task: Task) -> None:
        if task.task_id in self._store:
            raise TaskManagementConstraintError(constraint_name="task_identity")
        self._store[task.task_id] = task
        self._owner.writes += 1

    def get_by_idempotency_key(self, idempotency_key: str) -> Task | None:
        task_id = self._idempotency.get(idempotency_key)
        return self._store.get(task_id) if task_id is not None else None

    def add_with_idempotency(
        self, task: Task, *, idempotency_key: str
    ) -> tuple[Task, bool]:
        existing = self.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            return existing, True
        self.add(task)
        self._idempotency[idempotency_key] = task.task_id
        return task, False

    def save(self, task: Task, *, expected_revision: Revision) -> None:
        current = self._store.get(task.task_id)
        if current is None or current.revision != expected_revision:
            raise TaskManagementRevisionConflictError(
                resource="task", expected_revision=expected_revision.value
            )
        self._store[task.task_id] = task
        self._owner.writes += 1


class _RunRepository:
    def __init__(self, owner: _FakeUow, store: dict[RunId, Run]) -> None:
        self._owner = owner
        self._store = store

    def get(self, run_id: RunId) -> Run | None:
        return self._store.get(run_id)

    def add(self, run: Run) -> None:
        if run.run_id in self._store:
            raise TaskManagementConstraintError(constraint_name="run_identity")
        self._store[run.run_id] = run
        self._owner.writes += 1

    def save(self, run: Run, *, expected_revision: Revision) -> None:
        current = self._store.get(run.run_id)
        if current is None or current.revision != expected_revision:
            raise TaskManagementRevisionConflictError(
                resource="run", expected_revision=expected_revision.value
            )
        self._store[run.run_id] = run
        self._owner.writes += 1


class _StageRepository:
    def __init__(
        self, owner: _FakeUow, store: dict[tuple[TaskId, StageReference], Stage]
    ) -> None:
        self._owner = owner
        self._store = store

    def get(self, task_id: TaskId, stage: StageReference) -> Stage | None:
        return self._store.get((task_id, stage))

    def add(self, stage: Stage) -> None:
        key = (stage.task_id, stage.stage)
        if key in self._store:
            raise TaskManagementConstraintError(constraint_name="stage_identity")
        self._store[key] = stage
        self._owner.writes += 1

    def save(self, stage: Stage, *, expected_revision: Revision) -> None:
        key = (stage.task_id, stage.stage)
        current = self._store.get(key)
        if current is None or current.revision != expected_revision:
            raise TaskManagementRevisionConflictError(
                resource="stage", expected_revision=expected_revision.value
            )
        self._store[key] = stage
        self._owner.writes += 1


class _FakeUow:
    def __init__(
        self,
        tasks: dict[TaskId, Task],
        runs: dict[RunId, Run],
        stages: dict[tuple[TaskId, StageReference], Stage],
        idempotency: dict[str, TaskId],
        *,
        fail_task_save: bool = False,
        fail_task_get: BaseException | None = None,
    ) -> None:
        self._tasks_store = tasks
        self._runs_store = runs
        self._stages_store = stages
        self._idempotency_store = idempotency
        self._fail_task_save = fail_task_save
        self._fail_task_get = fail_task_get
        self._before_tasks: dict[TaskId, Task] = {}
        self._before_runs: dict[RunId, Run] = {}
        self._before_stages: dict[tuple[TaskId, StageReference], Stage] = {}
        self._before_idempotency: dict[str, TaskId] = {}
        self.commits = 0
        self.rollbacks = 0
        self.writes = 0
        self._active = False
        self._state = UnitOfWorkState.NEW
        self.tasks: TaskRepositoryPort = _TaskRepository(self, tasks, idempotency)
        self.runs: RunRepositoryPort = _RunRepository(self, runs)
        self.stages: StageRepositoryPort = _StageRepository(self, stages)

    def __enter__(self) -> Self:
        self._before_tasks = self._tasks_store.copy()
        self._before_runs = self._runs_store.copy()
        self._before_stages = self._stages_store.copy()
        self._before_idempotency = self._idempotency_store.copy()
        self._active = True
        self._state = UnitOfWorkState.ACTIVE
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del traceback
        if self._active:
            self.rollback()
        self.close()

    @property
    def state(self) -> UnitOfWorkState:
        return self._state

    def commit(self) -> None:
        assert self._active
        self.commits += 1
        self._active = False
        self._state = UnitOfWorkState.COMMITTED

    def rollback(self) -> None:
        assert self._active
        self._tasks_store.clear()
        self._tasks_store.update(self._before_tasks)
        self._runs_store.clear()
        self._runs_store.update(self._before_runs)
        self._stages_store.clear()
        self._stages_store.update(self._before_stages)
        self._idempotency_store.clear()
        self._idempotency_store.update(self._before_idempotency)
        self.rollbacks += 1
        self._active = False
        self._state = UnitOfWorkState.ROLLED_BACK

    def close(self) -> None:
        self._active = False
        self._state = UnitOfWorkState.CLOSED


class _FailingTaskRepository(_TaskRepository):
    def save(self, task: Task, *, expected_revision: Revision) -> None:
        del task, expected_revision
        raise TaskManagementConstraintError(constraint_name="forced_failure")


class _FailingTaskUow(_FakeUow):
    def __init__(
        self,
        tasks: dict[TaskId, Task],
        runs: dict[RunId, Run],
        stages: dict[tuple[TaskId, StageReference], Stage],
        idempotency: dict[str, TaskId],
    ) -> None:
        super().__init__(tasks, runs, stages, idempotency)
        self.tasks = _FailingTaskRepository(self, tasks, idempotency)


class _Factory:
    def __init__(self, *, failing_task_save: bool = False) -> None:
        self.tasks: dict[TaskId, Task] = {}
        self.runs: dict[RunId, Run] = {}
        self.stages: dict[tuple[TaskId, StageReference], Stage] = {}
        self.idempotency: dict[str, TaskId] = {}
        self.uows: list[_FakeUow] = []
        self._failing_task_save = failing_task_save

    def __call__(self) -> TaskManagementUnitOfWork:
        if self._failing_task_save:
            uow = _FailingTaskUow(self.tasks, self.runs, self.stages, self.idempotency)
        else:
            uow = _FakeUow(self.tasks, self.runs, self.stages, self.idempotency)
        self.uows.append(uow)
        return uow


def _service(factory: _Factory) -> TaskManagementApplicationService:
    return TaskManagementApplicationService(factory)


def _create(service: TaskManagementApplicationService) -> TaskId:
    task_id = TaskId("task-app")
    service.create_draft_task(
        CreateDraftTask(
            task_id=task_id,
            task_name="City commute pack",
            product_category="backpack",
            promotion_goal="commute positioning",
            updated_at=NOW,
        )
    )
    return task_id


def test_create_and_query_are_immutable_and_query_does_not_commit() -> None:
    factory = _Factory()
    service = _service(factory)
    task_id = _create(service)
    created_uow = factory.uows[-1]
    assert created_uow.commits == 1

    snapshot = service.get_task(GetTask(task_id))
    assert snapshot.task_status.value == "draft"
    assert snapshot.revision == Revision.initial()
    assert snapshot.task_id == task_id
    queried_uow = factory.uows[-1]
    assert queried_uow.commits == 0

    with pytest.raises(AttributeError):
        snapshot.task_status = snapshot.task_status  # type: ignore[misc]


def test_create_idempotency_replays_same_task_and_rejects_changed_input() -> None:
    factory = _Factory()
    service = _service(factory)
    first, replayed = service.create_draft_task_idempotent(
        CreateDraftTask(
            task_id=TaskId("task-idempotent-first"),
            task_name="City commute pack",
            product_category="backpack",
            promotion_goal="commute positioning",
            updated_at=NOW,
            idempotency_key="create-key",
        )
    )
    replay, was_replayed = service.create_draft_task_idempotent(
        CreateDraftTask(
            task_id=TaskId("task-idempotent-retry"),
            task_name="City commute pack",
            product_category="backpack",
            promotion_goal="commute positioning",
            updated_at=NOW,
            idempotency_key="create-key",
        )
    )

    assert replayed is False
    assert was_replayed is True
    assert replay.task_id == first.task_id
    assert len(factory.tasks) == 1
    with pytest.raises(TaskManagementError) as raised:
        service.create_draft_task_idempotent(
            CreateDraftTask(
                task_id=TaskId("task-idempotent-conflict"),
                task_name="Different task",
                product_category="backpack",
                promotion_goal="commute positioning",
                updated_at=NOW,
                idempotency_key="create-key",
            )
        )
    assert raised.value.error_code == "idempotency_conflict"
    assert len(factory.tasks) == 1


def test_prepare_initial_run_sets_draft_running_and_initial_fact_state_atomically() -> (
    None
):
    factory = _Factory()
    service = _service(factory)
    task_id = _create(service)

    result = service.prepare_initial_run(
        PrepareInitialRun(
            task_id=task_id,
            run_id=RunId("run-app"),
            expected_revision=Revision.initial(),
            updated_at=NOW,
        )
    )

    assert result.task.task_status.value == "running"
    assert result.task.current_stage is FACT_STAGE
    assert result.task.active_run_id == RunId("run-app")
    assert result.task.latest_run_id == RunId("run-app")
    assert result.task.revision == Revision(2)
    assert result.run.status.value == "queued"
    assert result.run.current_stage is FACT_STAGE
    assert result.stage.stage is FACT_STAGE
    assert result.stage.status.value == "ready"
    assert result.stage.revision == Revision(1)
    assert factory.uows[-1].commits == 1


def test_stale_prepare_returns_typed_conflict_and_writes_nothing() -> None:
    factory = _Factory()
    service = _service(factory)
    task_id = _create(service)

    with pytest.raises(TaskManagementError) as raised:
        service.prepare_initial_run(
            PrepareInitialRun(
                task_id=task_id,
                run_id=RunId("run-stale"),
                expected_revision=Revision(1),
                updated_at=NOW,
            )
        )

    assert raised.value.error_code == "revision_conflict"
    assert raised.value.retryability is False
    assert raised.value.relevant_reference is not None
    assert raised.value.relevant_reference.task_id == task_id
    assert factory.runs == {}
    assert factory.stages == {}
    assert factory.uows[-1].commits == 0


def test_prepare_failure_rolls_back_run_stage_and_task_pointer_changes() -> None:
    factory = _Factory(failing_task_save=True)
    service = _service(factory)
    task_id = _create(service)
    # Keep the seeded Task while replacing only the next UoW's task port.
    with pytest.raises(TaskManagementError) as raised:
        service.prepare_initial_run(
            PrepareInitialRun(
                task_id=task_id,
                run_id=RunId("run-rollback"),
                expected_revision=Revision.initial(),
                updated_at=NOW,
            )
        )

    assert raised.value.error_code == "constraint_violation"
    assert factory.runs == {}
    assert factory.stages == {}
    assert factory.tasks[task_id].task_status.value == "draft"
    assert factory.uows[-1].commits == 0
    assert factory.uows[-1].rollbacks == 1


def test_unknown_programming_exception_is_not_hidden_as_persistence_error() -> None:
    task_id = TaskId("task-unknown")

    class _BrokenFactory(_Factory):
        def __call__(self) -> TaskManagementUnitOfWork:
            uow = _FakeUow(self.tasks, self.runs, self.stages, self.idempotency)
            uow.tasks = _TaskRepository(uow, self.tasks, self.idempotency)

            def broken_get(value: TaskId) -> Task | None:
                del value
                raise RuntimeError("programming bug")

            # Protocol methods are intentionally replaced only in this test.
            uow.tasks.get = broken_get  # type: ignore[method-assign]
            self.uows.append(uow)
            return uow

    broken_service = _service(_BrokenFactory())
    with pytest.raises(RuntimeError, match="programming bug"):
        broken_service.get_task(GetTask(task_id))


def test_public_application_error_can_cross_a_standard_exception_boundary() -> None:
    reference = TaskManagementResourceReference(
        kind=TaskManagementResourceKind.TASK,
        task_id=TaskId("task-error"),
    )
    error = TaskManagementError(
        error_code="revision_conflict",
        category="task_management",
        message="refresh",
        retryability=False,
        relevant_reference=reference,
    )
    with pytest.raises(TaskManagementError) as raised:
        raise error
    assert raised.value.relevant_reference == reference
