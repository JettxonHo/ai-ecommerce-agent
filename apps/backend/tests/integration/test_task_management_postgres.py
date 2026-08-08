"""Opt-in PostgreSQL acceptance for Task Management adapter #95."""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, event, text
from sqlalchemy.engine import URL

from ai_ecommerce_agent.modules.task_management.application.errors import (
    TaskManagementOwnershipError,
    TaskManagementRevisionConflictError,
)
from ai_ecommerce_agent.modules.task_management.domain import (
    Run,
    Stage,
    StageReference,
    Task,
)
from ai_ecommerce_agent.modules.task_management.infrastructure.uow import (
    TaskManagementPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)
from ai_ecommerce_agent.shared_kernel import Revision, RunId, TaskId

pytestmark = [pytest.mark.integration, pytest.mark.live]

if os.environ.get("MVP0_RUN_POSTGRES_ADAPTER") != "1":
    pytest.skip(
        "set MVP0_RUN_POSTGRES_ADAPTER=1 for the opt-in PostgreSQL adapter suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_009b2_adapter"
URL_ENV = "MVP0_ADAPTER_DATABASE_URL"
DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)


def _database_url() -> str:
    return os.environ.get(URL_ENV, DEFAULT_URL).strip()


def _alembic_config(database_url: str) -> Config:
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.set_main_option("business_schema", SCHEMA)
    config.set_main_option("version_table_schema", SCHEMA)
    return config


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    """Own only the fixed adapter schema and prove cleanup at teardown."""

    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=_database_url(),
            pool_size=2,
            max_overflow=0,
            pool_timeout=2,
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA}" CASCADE'))
        connection.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))
    try:
        command.upgrade(_alembic_config(_database_url()), "head")
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


def _fixtures(suffix: str) -> tuple[Task, Run, Stage]:
    updated_at = datetime(2026, 8, 9, 1, 0, tzinfo=UTC)
    task = Task.create(
        TaskId(f"task-adapter-{suffix}"),
        task_name="City commute pack",
        product_category="backpack",
        promotion_goal="commute positioning",
        updated_at=updated_at,
    )
    run = Run.create(
        RunId(f"run-adapter-{suffix}"), task.task_id, updated_at=updated_at
    )
    stage = Stage.create(
        task.task_id,
        StageReference.PRODUCT_POSITIONING,
        updated_at=updated_at,
    )
    return task, run, stage


def test_task_run_stage_roundtrip_and_commit_visibility(
    postgres_engine: Engine,
) -> None:
    task, run, stage = _fixtures("roundtrip")
    factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        postgres_engine, schema=SCHEMA
    )
    with factory() as uow:
        uow.tasks.add(task)
        uow.runs.add(run)
        uow.stages.add(stage)
        uow.commit()

    with factory() as uow:
        assert uow.tasks.get(task.task_id) == task
        assert uow.runs.get(run.run_id) == run
        assert uow.stages.get(task.task_id, stage.stage) == stage
        uow.commit()


def test_uncommitted_write_rolls_back(postgres_engine: Engine) -> None:
    task, _, _ = _fixtures("rollback")
    task = Task.create(
        TaskId("task-adapter-rollback"),
        task_name=task.task_name,
        product_category=task.product_category,
        promotion_goal=task.promotion_goal,
        updated_at=task.updated_at,
    )
    factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        postgres_engine, schema=SCHEMA
    )
    with factory() as uow:
        uow.tasks.add(task)
    with factory() as uow:
        assert uow.tasks.get(task.task_id) is None
        uow.commit()


def test_compare_and_swap_conflict_is_project_error(postgres_engine: Engine) -> None:
    task, _, stage = _fixtures("cas")
    task = Task.create(
        TaskId("task-adapter-cas"),
        task_name=task.task_name,
        product_category=task.product_category,
        promotion_goal=task.promotion_goal,
        updated_at=task.updated_at,
    )
    factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        postgres_engine, schema=SCHEMA
    )
    with factory() as uow:
        uow.tasks.add(task)
        uow.stages.add(stage)
        uow.commit()
    first = factory()
    second = factory()
    with first as left, second as right:
        left_task = left.tasks.get(task.task_id)
        right_task = right.tasks.get(task.task_id)
        assert left_task is not None and right_task is not None
        changed_left = left_task.move_to_stage(
            StageReference.PRODUCT_POSITIONING,
            expected_revision=Revision(0),
            updated_at=task.updated_at,
        )
        left.tasks.save(changed_left, expected_revision=Revision(0))
        left.commit()
        changed_right = right_task.move_to_stage(
            StageReference.PRODUCT_POSITIONING,
            expected_revision=Revision(0),
            updated_at=task.updated_at,
        )
        with pytest.raises(TaskManagementRevisionConflictError):
            right.tasks.save(changed_right, expected_revision=Revision(0))
        right.rollback()


def test_named_foreign_owner_constraint_translates(postgres_engine: Engine) -> None:
    task, run, stage = _fixtures("owner")
    task_two = Task.create(
        TaskId("task-adapter-owner-2"),
        task_name=task.task_name,
        product_category=task.product_category,
        promotion_goal=task.promotion_goal,
        updated_at=task.updated_at,
    )
    factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        postgres_engine, schema=SCHEMA
    )
    with factory() as uow:
        uow.tasks.add(task)
        uow.runs.add(run)
        uow.tasks.add(task_two)
        uow.commit()
    cross_owned = Stage(
        task_id=task_two.task_id,
        stage=stage.stage,
        status=stage.status,
        revision=stage.revision,
        current_version=stage.current_version,
        last_valid_version=stage.last_valid_version,
        last_run_id=run.run_id,
        waiting_reason=stage.waiting_reason,
        updated_at=stage.updated_at,
    )
    with factory() as uow:
        with pytest.raises(TaskManagementOwnershipError) as raised:
            uow.stages.add(cross_owned)
        assert raised.value.safe_context["constraint"] == (
            "fk_task_management_stages_last_run_owner"
        )
        uow.rollback()


def test_fresh_uow_sessions_return_connections(postgres_engine: Engine) -> None:
    checkins = 0

    def on_checkin(*_: object) -> None:
        nonlocal checkins
        checkins += 1

    event.listen(postgres_engine, "checkin", on_checkin)
    try:
        factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
            postgres_engine, schema=SCHEMA
        )
        first, second = factory(), factory()
        assert first is not second
        with first as uow:
            assert uow.tasks.get(TaskId("task-adapter-not-present")) is None
            uow.commit()
        first_checkins = checkins
        with second as uow:
            assert uow.tasks.get(TaskId("task-adapter-still-not-present")) is None
            uow.commit()
        assert first_checkins >= 1
        assert checkins > first_checkins
    finally:
        event.remove(postgres_engine, "checkin", on_checkin)
