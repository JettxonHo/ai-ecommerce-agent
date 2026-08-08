"""Opt-in PostgreSQL acceptance for the Task Management application slice."""

from __future__ import annotations

import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import Barrier, Event

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.modules.task_management.application.errors import (
    TaskManagementError,
    TaskManagementResourceKind,
    TaskManagementResourceReference,
)
from ai_ecommerce_agent.modules.task_management.application.ports import (
    TaskManagementUnitOfWork,
)
from ai_ecommerce_agent.modules.task_management.application.services import (
    TaskManagementApplicationService,
)
from ai_ecommerce_agent.modules.task_management.domain import (
    Run,
    Stage,
    StageReference,
)
from ai_ecommerce_agent.modules.task_management.infrastructure.uow import (
    TaskManagementPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.task_management.public import (
    CreateDraftTask,
    GetRun,
    GetStage,
    GetTask,
    PrepareInitialRun,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)
from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

pytestmark = [pytest.mark.integration, pytest.mark.live]

if os.environ.get("MVP0_RUN_TASK_MANAGEMENT_APPLICATION") != "1":
    pytest.skip(
        "set MVP0_RUN_TASK_MANAGEMENT_APPLICATION=1 for the opt-in "
        "Task Management application suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_009c_application"
URL_ENV = "MVP0_APPLICATION_DATABASE_URL"
DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)
NOW = datetime(2026, 8, 9, 1, 0, tzinfo=UTC)
FACT_STAGE = StageReference.PRODUCT_INTAKE_AND_FACT_EXTRACTION


def _database_url() -> str:
    return os.environ.get(
        URL_ENV, os.environ.get("MVP0_ADAPTER_DATABASE_URL", DEFAULT_URL)
    ).strip()


def _alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", SCHEMA)
    config.set_main_option("version_table_schema", SCHEMA)
    return config


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    """Own one fixed test schema and prove that teardown removes it."""

    database_url = _database_url()
    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=database_url,
            pool_size=3,
            max_overflow=0,
            pool_timeout=5,
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))
    try:
        command.upgrade(_alembic_config(database_url), "head")
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        with engine.connect() as connection:
            remaining = connection.scalar(
                text("SELECT count(*) FROM pg_namespace WHERE nspname = :schema"),
                {"schema": SCHEMA},
            )
        assert remaining == 0
        engine.dispose()


@pytest.fixture(scope="module")
def application(postgres_engine: Engine) -> TaskManagementApplicationService:
    factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        postgres_engine, schema=SCHEMA
    )
    return TaskManagementApplicationService(factory)


def _create_draft(application: TaskManagementApplicationService, suffix: str) -> TaskId:
    task_id = TaskId(f"task-application-{suffix}")
    application.create_draft_task(
        CreateDraftTask(
            task_id=task_id,
            task_name="City commute pack",
            product_category="backpack",
            promotion_goal="commute positioning",
            updated_at=NOW,
        )
    )
    return task_id


def _count_rows(engine: Engine, table: str, column: str, value: str) -> int:
    with engine.connect() as connection:
        return int(
            connection.scalar(
                text(
                    f'SELECT count(*) FROM "{SCHEMA}"."{table}" '
                    f'WHERE "{column}" = :value'
                ),
                {"value": value},
            )
        )


def test_create_query_and_prepare_initial_run_are_persisted_atomically(
    application: TaskManagementApplicationService,
) -> None:
    task_id = _create_draft(application, "prepare")

    draft = application.get_task(GetTask(task_id))
    assert draft.task_status.value == "draft"
    assert draft.revision == Revision.initial()

    result = application.prepare_initial_run(
        PrepareInitialRun(
            task_id=task_id,
            run_id=RunId("run-application-prepare"),
            expected_revision=Revision.initial(),
            updated_at=NOW,
        )
    )

    assert result.task.task_status.value == "running"
    assert result.task.current_stage is FACT_STAGE
    assert result.task.active_run_id == result.run.run_id
    assert result.task.latest_run_id == result.run.run_id
    assert result.run.status.value == "queued"
    assert result.run.current_stage is FACT_STAGE
    assert result.stage.status.value == "ready"
    assert result.stage.stage is FACT_STAGE

    assert application.get_run(GetRun(result.run.run_id)) == result.run
    assert application.get_stage(GetStage(task_id, FACT_STAGE)) == result.stage


def _cas_transaction(
    application: TaskManagementApplicationService,
    task_id: TaskId,
    run_id: RunId,
    stage_reference: StageReference,
    loaded: Barrier,
    left_committed: Event,
    *,
    is_left: bool,
) -> None:
    def operation(uow: TaskManagementUnitOfWork) -> None:
        task = uow.tasks.get(task_id)
        assert task is not None
        moved_task = task.start(
            run_id,
            expected_revision=Revision.initial(),
            updated_at=NOW,
        ).move_to_stage(
            stage_reference,
            expected_revision=Revision(1),
            updated_at=NOW,
        )
        run = Run.create(
            run_id,
            task_id,
            current_stage=stage_reference,
            updated_at=NOW,
        )
        stage = Stage.create(task_id, stage_reference, updated_at=NOW).prepare(
            expected_revision=Revision.initial(),
            updated_at=NOW,
        )
        loaded.wait(timeout=10)
        if not is_left:
            assert left_committed.wait(timeout=10)
        uow.stages.add(stage)
        uow.runs.add(run)
        uow.tasks.save(moved_task, expected_revision=Revision.initial())

    reference = TaskManagementResourceReference(
        kind=TaskManagementResourceKind.TASK,
        task_id=task_id,
    )
    application._write(  # pyright: ignore[reportPrivateUsage]  # CAS coordination test
        reference, operation
    )


def test_two_real_transactions_have_one_cas_winner_and_no_loser_rows(
    application: TaskManagementApplicationService,
    postgres_engine: Engine,
) -> None:
    task_id = _create_draft(application, "cas")
    loaded = Barrier(2)
    left_committed = Event()
    left_run_id = RunId("run-application-cas-left")
    right_run_id = RunId("run-application-cas-right")

    def left_worker() -> None:
        _cas_transaction(
            application,
            task_id,
            left_run_id,
            FACT_STAGE,
            loaded,
            left_committed,
            is_left=True,
        )
        left_committed.set()

    def right_worker() -> None:
        _cas_transaction(
            application,
            task_id,
            right_run_id,
            StageReference.PRODUCT_POSITIONING,
            loaded,
            left_committed,
            is_left=False,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        left_future = executor.submit(left_worker)
        right_future = executor.submit(right_worker)
        left_future.result()
        with pytest.raises(TaskManagementError) as raised:
            right_future.result()

    assert raised.value.error_code == "revision_conflict"
    assert raised.value.retryability is False
    assert raised.value.relevant_reference.task_id == task_id
    assert (
        _count_rows(postgres_engine, "task_management_runs", "run_id", str(left_run_id))
        == 1
    )
    assert (
        _count_rows(
            postgres_engine, "task_management_runs", "run_id", str(right_run_id)
        )
        == 0
    )
    assert (
        _count_rows(postgres_engine, "task_management_stages", "task_id", str(task_id))
        == 1
    )
    assert application.get_task(GetTask(task_id)).active_run_id == left_run_id


def test_pointer_ownership_failure_rolls_back_the_whole_application_transaction(
    application: TaskManagementApplicationService,
    postgres_engine: Engine,
) -> None:
    task_id = _create_draft(application, "owner")
    other_task_id = _create_draft(application, "owner-other")
    bad_run_id = RunId("run-application-owner-bad")

    def operation(uow: TaskManagementUnitOfWork) -> None:
        task = uow.tasks.get(task_id)
        assert task is not None
        uow.stages.add(Stage.create(task_id, FACT_STAGE, updated_at=NOW))
        uow.runs.add(Run.create(bad_run_id, other_task_id, updated_at=NOW))
        bad_task = task.start(
            bad_run_id,
            expected_revision=Revision.initial(),
            updated_at=NOW,
        ).move_to_stage(
            FACT_STAGE,
            expected_revision=Revision(1),
            updated_at=NOW,
        )
        uow.tasks.save(bad_task, expected_revision=Revision.initial())

    reference = TaskManagementResourceReference(
        kind=TaskManagementResourceKind.TASK,
        task_id=task_id,
    )
    with pytest.raises(TaskManagementError) as raised:
        application._write(  # pyright: ignore[reportPrivateUsage]  # ownership rollback test
            reference, operation
        )

    assert raised.value.error_code == "ownership_conflict"
    assert raised.value.relevant_reference.task_id == task_id
    assert application.get_task(GetTask(task_id)).task_status.value == "draft"
    with pytest.raises(TaskManagementError) as missing_run:
        application.get_run(GetRun(bad_run_id))
    assert missing_run.value.error_code == "not_found"
    with pytest.raises(TaskManagementError) as missing_stage:
        application.get_stage(GetStage(task_id, FACT_STAGE))
    assert missing_stage.value.error_code == "not_found"
    assert (
        _count_rows(postgres_engine, "task_management_runs", "run_id", str(bad_run_id))
        == 0
    )
    assert (
        _count_rows(postgres_engine, "task_management_stages", "task_id", str(task_id))
        == 0
    )
