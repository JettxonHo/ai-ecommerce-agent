"""Opt-in real PostgreSQL vertical acceptance for the Task HTTP routes."""

# FastAPI/Starlette's TestClient is an untyped framework boundary in the
# accepted runtime tuple; keep this integration test focused on behavior.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportUnusedFunction=false, reportCallIssue=false

from __future__ import annotations

import os
import socket
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from pytest_socket import SocketBlockedError, _true_socket
from sqlalchemy import Engine, text
from sqlalchemy.engine import URL
from starlette.exceptions import StarletteDeprecationWarning

from ai_ecommerce_agent.bootstrap.deterministic_result_postgres import (
    DeterministicResultPostgresComposition,
    compose_deterministic_result_postgres,
)
from ai_ecommerce_agent.entrypoints.http import (
    FixedWorkspaceHttpConfig,
    create_task_http_application,
)
from ai_ecommerce_agent.modules.source_evidence.application.primary_input_services import (  # noqa: E501
    PrimaryInputApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.primary_input_uow import (  # noqa: E501
    PrimaryInputPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.task_management.application.services import (
    TaskManagementApplicationService,
)
from ai_ecommerce_agent.modules.task_management.infrastructure.uow import (
    TaskManagementPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)

warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)
from fastapi.testclient import TestClient  # noqa: E402

pytestmark = [pytest.mark.integration, pytest.mark.live]

if os.environ.get("MVP0_RUN_TASK_HTTP_POSTGRES") != "1":
    pytest.skip(
        "set MVP0_RUN_TASK_HTTP_POSTGRES=1 for the opt-in Task HTTP PostgreSQL suite",
        allow_module_level=True,
    )

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "mvp0_249_task_http"
URL_ENV = "MVP0_TASK_HTTP_DATABASE_URL"
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
    """Own one schema, migrate it to the current sole head, and clean it."""

    database_url = _database_url()
    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=database_url,
            pool_size=4,
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
        engine.dispose()


@pytest.fixture(autouse=True)
def _allow_local_testclient_socket(monkeypatch: pytest.MonkeyPatch) -> None:
    """Permit TestClient's local Unix socketpair, but no network sockets."""

    true_socket = _true_socket

    class LocalSocket(true_socket):  # type: ignore[misc, valid-type]
        def __new__(
            cls,
            family: socket.AddressFamily | int = -1,
            type: socket.SocketKind | int = -1,
            proto: int = -1,
            fileno: int | None = None,
        ) -> LocalSocket:
            if int(family) == int(socket.AF_UNIX):
                return super().__new__(cls, family, type, proto, fileno)
            raise SocketBlockedError()

    monkeypatch.setattr(socket, "socket", LocalSocket)


def _client(engine: Engine) -> TestClient:
    task_factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        engine, schema=SCHEMA
    )
    input_factory = PrimaryInputPostgresUnitOfWorkFactory.from_engine(
        engine, schema=SCHEMA
    )
    return TestClient(
        create_task_http_application(
            config=FixedWorkspaceHttpConfig(
                workspace_id="workspace-demo",
                workbench_origin="http://127.0.0.1:5173",
            ),
            task_application=TaskManagementApplicationService(task_factory),
            primary_input_application=PrimaryInputApplicationService(input_factory),
        )
    )


def _result_client(
    engine: Engine,
) -> tuple[TestClient, DeterministicResultPostgresComposition]:
    task_factory = TaskManagementPostgresUnitOfWorkFactory.from_engine(
        engine, schema=SCHEMA
    )
    input_factory = PrimaryInputPostgresUnitOfWorkFactory.from_engine(
        engine, schema=SCHEMA
    )
    composition = compose_deterministic_result_postgres(
        PostgresEngineConfig(
            database_url=_database_url(),
            pool_size=2,
            max_overflow=0,
            pool_timeout=5,
        ),
        schema=SCHEMA,
    )
    return (
        TestClient(
            create_task_http_application(
                config=FixedWorkspaceHttpConfig(
                    workspace_id="workspace-demo",
                    workbench_origin="http://127.0.0.1:5173",
                ),
                task_application=TaskManagementApplicationService(task_factory),
                primary_input_application=PrimaryInputApplicationService(input_factory),
                result_application=composition.application,
                pipeline_coordinator=composition.coordinator,
                export_application=composition.export_application,
            )
        ),
        composition,
    )


def test_create_list_read_save_input_and_replay_survive_new_composition(
    postgres_engine: Engine,
) -> None:
    """Exercise the consumed HTTP path against migrated PostgreSQL Current Truth."""

    body = {
        "taskName": "City launch",
        "productCategory": "Backpack",
        "promotionGoal": "Awareness",
    }
    headers = {"Idempotency-Key": "task-http-replay"}

    with _client(postgres_engine) as client:
        created = client.post("/api/v1/tasks", headers=headers, json=body)
        assert created.status_code == 201, created.text
        task_id = created.json()["taskId"]
        listed = client.get("/api/v1/tasks?limit=20")
        read = client.get(f"/api/v1/tasks/{task_id}")
        saved = client.put(
            f"/api/v1/tasks/{task_id}/primary-input",
            json={
                "inputKind": "pasted_text",
                "fileName": None,
                "content": "Product details\nwith transit context",
            },
        )
        input_read = client.get(f"/api/v1/tasks/{task_id}/primary-input")

    with _client(postgres_engine) as reconstructed_client:
        replayed = reconstructed_client.post(
            "/api/v1/tasks", headers=headers, json=body
        )
        changed = reconstructed_client.post(
            "/api/v1/tasks",
            headers=headers,
            json={**body, "promotionGoal": "Different"},
        )
        same_input_replay = reconstructed_client.put(
            f"/api/v1/tasks/{task_id}/primary-input",
            json={
                "inputKind": "pasted_text",
                "fileName": None,
                "content": "Product details\r\nwith transit context",
            },
        )
        changed_input = reconstructed_client.put(
            f"/api/v1/tasks/{task_id}/primary-input",
            json={
                "inputKind": "pasted_text",
                "fileName": None,
                "content": "Changed details",
            },
        )
        reloaded_input = reconstructed_client.get(
            f"/api/v1/tasks/{task_id}/primary-input"
        )
        oversize = reconstructed_client.put(
            f"/api/v1/tasks/{task_id}/primary-input",
            json={
                "inputKind": "pasted_text",
                "fileName": None,
                "content": "x" * (1_048_576 + 1),
            },
        )

    assert created.status_code == 201
    assert listed.status_code == 200
    assert [item["taskId"] for item in listed.json()["items"]] == [task_id]
    assert read.status_code == 200
    assert read.json()["taskId"] == task_id
    assert saved.status_code == 200
    assert input_read.status_code == 200
    assert input_read.json()["content"] == "Product details\nwith transit context"
    assert input_read.json()["inputRevision"] == 0
    assert replayed.status_code == 200
    assert replayed.json()["taskId"] == task_id
    assert changed.status_code == 409
    assert same_input_replay.status_code == 200
    assert same_input_replay.json() == input_read.json()
    assert changed_input.status_code == 200
    assert changed_input.json()["inputRevision"] == 1
    assert reloaded_input.status_code == 200
    assert reloaded_input.json()["content"] == "Changed details"
    assert reloaded_input.json()["inputRevision"] == 1
    assert oversize.status_code == 413

    with postgres_engine.connect() as connection:
        task_count = connection.scalar(
            text(
                f'SELECT count(*) FROM "{SCHEMA}"."task_management_tasks" '
                "WHERE task_name = :task_name"
            ),
            {"task_name": body["taskName"]},
        )
        key_count = connection.scalar(
            text(
                f'SELECT count(*) FROM "{SCHEMA}"."task_management_create_idempotency" '
                "WHERE idempotency_key = :idempotency_key"
            ),
            {"idempotency_key": headers["Idempotency-Key"]},
        )
    assert task_count == 1
    assert key_count == 1


def test_generate_result_is_durable_atomic_and_revision_fenced(
    postgres_engine: Engine,
) -> None:
    task_body = {
        "taskName": "Anchor result launch",
        "productCategory": "Backpack",
        "promotionGoal": "Awareness",
    }
    anchor_input = (
        "fixture-sufficient-v1 fictional synthetic non-regulated\n"
        "anchor-city-commuter-backpack CBP-SYN-001 城市通勤双肩包\n"
        "工作日城市通勤时携带电脑、文件和日常随身物品，约 18 升，"
        "可放入 14 英寸级别笔记本电脑。\n"
        "表面有防泼水处理。source-sufficient-product-v1 product.json direct_source。"
    )
    client, composition = _result_client(postgres_engine)
    try:
        with client:
            created = client.post(
                "/api/v1/tasks",
                headers={"Idempotency-Key": "result-task-create"},
                json=task_body,
            )
            task_id = created.json()["taskId"]
            saved = client.put(
                f"/api/v1/tasks/{task_id}/primary-input",
                json={
                    "inputKind": "pasted_text",
                    "fileName": None,
                    "content": anchor_input,
                },
            )
            generated = client.post(
                f"/api/v1/tasks/{task_id}/commands/generate-result",
                headers={"Idempotency-Key": "result-key-1"},
                json={"expectedInputRevision": 0},
            )
            current = client.get(f"/api/v1/tasks/{task_id}/current-result")
        assert created.status_code == 201, created.text
        assert saved.status_code == 200, saved.text
        assert generated.status_code == 201, generated.text
        assert generated.json()["status"] == "awaiting_review"
        assert all(
            generated.json()[name] is not None
            for name in (
                "productIntake",
                "customerInsight",
                "productPositioning",
                "marketingBrief",
                "xiaohongshuBrief",
            )
        )
        with client:
            assert current.status_code == 200, current.text
            assert current.json() == generated.json()

            confirmed = client.post(
                f"/api/v1/tasks/{task_id}/commands/confirm-current-result",
                headers={"Idempotency-Key": "confirm-key-1"},
                json={
                    "expectedResultRevision": 0,
                    "marketingCoreMessage": "Confirmed commuter storage message",
                    "xiaohongshuTitleDirection": "Confirmed commuter title direction",
                },
            )
            confirmed_replay = client.post(
                f"/api/v1/tasks/{task_id}/commands/confirm-current-result",
                headers={"Idempotency-Key": "confirm-key-1"},
                json={
                    "expectedResultRevision": 0,
                    "marketingCoreMessage": "Confirmed commuter storage message",
                    "xiaohongshuTitleDirection": "Confirmed commuter title direction",
                },
            )
            assert confirmed.status_code == 201, confirmed.text
            assert confirmed.json()["status"] == "confirmed"
            assert (
                confirmed.json()["confirmation"]["marketingBriefVersion"][
                    "versionNumber"
                ]
                == 1
            )
            assert (
                confirmed.json()["marketingBrief"]["brief_candidate"][
                    "message_architecture"
                ]["core_message"]
                == "Confirmed commuter storage message"
            )
            assert confirmed_replay.status_code == 200, confirmed_replay.text
            assert confirmed_replay.json() == confirmed.json()

            preview = client.post(
                f"/api/v1/tasks/{task_id}/export-previews",
                json={"briefKind": "marketing"},
            )
            assert preview.status_code == 200, preview.text
            basis = preview.json()["basis"]
            snapshot = client.post(
                "/api/v1/export-snapshots",
                headers={"Idempotency-Key": "export-key-1"},
                json={"basis": basis},
            )
            snapshot_replay = client.post(
                "/api/v1/export-snapshots",
                headers={"Idempotency-Key": "export-key-1"},
                json={"basis": basis},
            )
            assert snapshot.status_code == 201, snapshot.text
            assert snapshot.json()["briefKind"] == "marketing"
            assert snapshot_replay.status_code == 200, snapshot_replay.text
            assert snapshot_replay.json() == snapshot.json()
            downloaded = client.get(snapshot.json()["contentLocation"])
            assert downloaded.status_code == 200, downloaded.text
            assert downloaded.headers["content-type"] == "text/markdown; charset=utf-8"
            assert "Confirmed commuter storage message" in downloaded.text
            assert downloaded.text.endswith("\n")

            xhs_preview = client.post(
                f"/api/v1/tasks/{task_id}/export-previews",
                json={"briefKind": "xiaohongshu"},
            )
            assert xhs_preview.status_code == 200, xhs_preview.text
            xhs_snapshot = client.post(
                "/api/v1/export-snapshots",
                headers={"Idempotency-Key": "export-key-xhs"},
                json={"basis": xhs_preview.json()["basis"]},
            )
            assert xhs_snapshot.status_code == 201, xhs_snapshot.text
            xhs_download = client.get(xhs_snapshot.json()["contentLocation"])
            assert xhs_download.status_code == 200, xhs_download.text
            assert xhs_download.text.startswith("# Xiaohongshu Brief\n")

        replay_client, replay_composition = _result_client(postgres_engine)
        try:
            with replay_client:
                replay = replay_client.post(
                    f"/api/v1/tasks/{task_id}/commands/generate-result",
                    headers={"Idempotency-Key": "result-key-1"},
                    json={"expectedInputRevision": 0},
                )
            assert replay.status_code == 200, replay.text
            assert replay.json() == confirmed.json()
        finally:
            replay_composition.close()

        with client:
            changed = client.put(
                f"/api/v1/tasks/{task_id}/primary-input",
                json={
                    "inputKind": "pasted_text",
                    "fileName": None,
                    "content": "Changed input with no Anchor SKU evidence.",
                },
            )
            assert changed.status_code == 200, changed.text
            fenced = client.post(
                f"/api/v1/tasks/{task_id}/commands/generate-result",
                headers={"Idempotency-Key": "result-key-2"},
                json={"expectedInputRevision": 0},
            )
            assert fenced.status_code == 409, fenced.text

        stale_client, stale_composition = _result_client(postgres_engine)
        try:
            with stale_client:
                stale_replay = stale_client.post(
                    f"/api/v1/tasks/{task_id}/commands/generate-result",
                    headers={"Idempotency-Key": "result-key-1"},
                    json={"expectedInputRevision": 0},
                )
            assert stale_replay.status_code == 409, stale_replay.text
        finally:
            stale_composition.close()
    finally:
        composition.close()
