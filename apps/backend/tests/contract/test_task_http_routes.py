"""Representative HTTP behavior for the first Fast Lane Task/input slice."""

# FastAPI/Starlette's current TestClient is an untyped framework test helper;
# keep its boundary untyped while preserving strict typing for production code.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportUnusedFunction=false, reportCallIssue=false

from __future__ import annotations

import socket
import warnings
from datetime import UTC, datetime

import pytest
from starlette.exceptions import StarletteDeprecationWarning

warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)

from fastapi.testclient import TestClient  # noqa: E402
from pytest_socket import SocketBlockedError, _true_socket  # noqa: E402

from ai_ecommerce_agent.entrypoints.http import (  # noqa: E402
    FixedWorkspaceHttpConfig,
    create_task_http_application,
)
from ai_ecommerce_agent.modules.source_evidence.public import (  # noqa: E402
    PrimaryInputKind,
    PrimaryInputSnapshot,
)
from ai_ecommerce_agent.modules.task_management.public import (  # noqa: E402
    CreateDraftTask,
    TaskSnapshot,
    TaskStatus,
)
from ai_ecommerce_agent.shared_kernel import Revision, TaskId  # noqa: E402

pytestmark = pytest.mark.contract


@pytest.fixture(autouse=True)
def _allow_testclient_socketpair(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow TestClient's local Unix socketpair while blocking network I/O."""

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


NOW = datetime(2026, 8, 12, 0, 0, tzinfo=UTC)


def _task(task_id: str = "task-1") -> TaskSnapshot:
    return TaskSnapshot(
        task_id=TaskId(task_id),
        task_name="City launch",
        product_category="Backpack",
        promotion_goal="Awareness",
        task_status=TaskStatus.DRAFT,
        revision=Revision.initial(),
        current_stage=None,
        active_run_id=None,
        latest_run_id=None,
        waiting_reason=None,
        updated_at=NOW,
    )


class _Tasks:
    def __init__(self) -> None:
        self.created = _task()
        self.keys: dict[str, tuple[str, str, str]] = {}

    def create_draft_task(self, command: object) -> TaskSnapshot:
        del command
        return self.created

    def create_draft_task_idempotent(
        self, command: CreateDraftTask
    ) -> tuple[TaskSnapshot, bool]:
        key = str(command.idempotency_key)
        values = (
            str(command.task_name),
            str(command.product_category),
            str(command.promotion_goal),
        )
        previous = self.keys.get(key)
        if previous is not None and previous != values:
            from ai_ecommerce_agent.modules.task_management.public import (
                TaskManagementError,
                TaskManagementResourceKind,
                TaskManagementResourceReference,
            )

            raise TaskManagementError(
                error_code="idempotency_conflict",
                category="task_management",
                message="retry key conflict",
                retryability=False,
                relevant_reference=TaskManagementResourceReference(
                    kind=TaskManagementResourceKind.TASK,
                    task_id=self.created.task_id,
                ),
            )
        if previous is not None:
            return self.created, True
        self.keys[key] = values
        return self.created, False

    def get_task(self, query: object) -> TaskSnapshot:
        del query
        return self.created

    def list_tasks(self, query: object) -> tuple[TaskSnapshot, ...]:
        del query
        return (self.created,)


class _PrimaryInputs:
    def __init__(self) -> None:
        self.value: PrimaryInputSnapshot | None = None

    def get_primary_input(self, query: object) -> PrimaryInputSnapshot:
        del query
        if self.value is None:
            from ai_ecommerce_agent.modules.source_evidence.public import (
                PrimaryInputNotFound,
            )

            raise PrimaryInputNotFound(TaskId("task-1"))
        return self.value

    def save_primary_input(self, command: object) -> PrimaryInputSnapshot:
        del command
        self.value = PrimaryInputSnapshot(
            task_id=TaskId("task-1"),
            input_kind=PrimaryInputKind.PASTED_TEXT,
            file_name=None,
            content="Product details",
            byte_count=len(b"Product details"),
            revision=Revision.initial(),
            updated_at=NOW,
        )
        return self.value


def _client() -> TestClient:
    return TestClient(
        create_task_http_application(
            config=FixedWorkspaceHttpConfig(
                workspace_id="workspace-demo",
                workbench_origin="http://127.0.0.1:5173",
            ),
            task_application=_Tasks(),
            primary_input_application=_PrimaryInputs(),
        )
    )


def test_task_and_primary_input_routes_expose_the_real_vertical_behavior() -> None:
    with _client() as client:
        created = client.post(
            "/api/v1/tasks",
            headers={"Idempotency-Key": "create-1"},
            json={
                "taskName": "City launch",
                "productCategory": "Backpack",
                "promotionGoal": "Awareness",
            },
        )
        listed = client.get("/api/v1/tasks?limit=20")
        read = client.get("/api/v1/tasks/task-1")
        saved = client.put(
            "/api/v1/tasks/task-1/primary-input",
            json={
                "inputKind": "pasted_text",
                "fileName": None,
                "content": "Product details",
            },
        )
        input_read = client.get("/api/v1/tasks/task-1/primary-input")

    assert created.status_code == 201
    assert listed.status_code == 200
    assert read.status_code == 200
    assert saved.status_code == 200
    assert input_read.status_code == 200
    assert input_read.json()["content"] == "Product details"


def test_task_create_replay_uses_application_idempotency_boundary() -> None:
    tasks = _Tasks()
    with TestClient(
        create_task_http_application(
            config=FixedWorkspaceHttpConfig(
                workspace_id="workspace-demo",
                workbench_origin="http://127.0.0.1:5173",
            ),
            task_application=tasks,
            primary_input_application=_PrimaryInputs(),
        )
    ) as client:
        body = {
            "taskName": "City launch",
            "productCategory": "Backpack",
            "promotionGoal": "Awareness",
        }
        first = client.post(
            "/api/v1/tasks", headers={"Idempotency-Key": "durable-key"}, json=body
        )
        replay = client.post(
            "/api/v1/tasks", headers={"Idempotency-Key": "durable-key"}, json=body
        )
        conflict = client.post(
            "/api/v1/tasks",
            headers={"Idempotency-Key": "durable-key"},
            json={**body, "promotionGoal": "Different"},
        )

    assert first.status_code == 201
    assert replay.status_code == 200
    assert replay.json()["taskId"] == first.json()["taskId"]
    assert conflict.status_code == 409
