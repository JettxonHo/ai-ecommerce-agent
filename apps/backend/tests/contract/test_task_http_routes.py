"""Representative HTTP behavior for the first Fast Lane Task/input slice."""

# FastAPI/Starlette's current TestClient is an untyped framework test helper;
# keep its boundary untyped while preserving strict typing for production code.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportUnusedFunction=false, reportCallIssue=false

from __future__ import annotations

import socket
import warnings
from dataclasses import dataclass
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
    def __init__(self, task_id: str = "task-1") -> None:
        self.created = _task(task_id)
        self.keys: dict[str, tuple[str, str, str]] = {}
        self.seen_task_ids: list[TaskId] = []

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
        self.seen_task_ids.append(query.task_id)  # type: ignore[attr-defined]
        return self.created

    def list_tasks(self, query: object) -> tuple[TaskSnapshot, ...]:
        del query
        return (self.created,)


class _PrimaryInputs:
    def __init__(self, task_id: str = "task-1") -> None:
        self.task_id = TaskId(task_id)
        self.value: PrimaryInputSnapshot | None = None

    def get_primary_input(self, query: object) -> PrimaryInputSnapshot:
        del query
        if self.value is None:
            from ai_ecommerce_agent.modules.source_evidence.public import (
                PrimaryInputNotFound,
            )

            raise PrimaryInputNotFound(self.task_id)
        return self.value

    def save_primary_input(self, command: object) -> PrimaryInputSnapshot:
        del command
        self.value = PrimaryInputSnapshot(
            task_id=self.task_id,
            input_kind=PrimaryInputKind.PASTED_TEXT,
            file_name=None,
            content="Product details",
            byte_count=len(b"Product details"),
            revision=Revision.initial(),
            updated_at=NOW,
        )
        return self.value


@dataclass(frozen=True)
class _ResultSnapshot:
    task_id: TaskId = TaskId("task-1")
    result_revision: int = 0
    input_revision: int = 0
    status: str = "awaiting_review"
    generated_at: datetime = NOW
    missing_information: tuple[str, ...] = ()
    candidates: dict[str, dict[str, str] | None] | None = None

    def __post_init__(self) -> None:
        if self.candidates is None:
            object.__setattr__(
                self,
                "candidates",
                {
                    "productIntake": {"candidate": "intake"},
                    "customerInsight": {"candidate": "insight"},
                    "productPositioning": {"candidate": "positioning"},
                    "marketingBrief": {"candidate": "marketing"},
                    "xiaohongshuBrief": {"candidate": "xiaohongshu"},
                },
            )


class _Results:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []
        self.snapshot = _ResultSnapshot()

    def generate_result(
        self,
        *,
        task_id: TaskId,
        idempotency_key: str,
        expected_input_revision: int,
        coordinator: object,
    ) -> tuple[_ResultSnapshot, bool]:
        assert coordinator is not None
        self.calls.append((str(task_id), idempotency_key, expected_input_revision))
        replayed = len(self.calls) > 1
        return self.snapshot, replayed

    def get_current_result(self, *, task_id: TaskId) -> _ResultSnapshot:
        assert task_id == self.snapshot.task_id
        return self.snapshot


class _Coordinator:
    def generate(self, *, input_text: str) -> object:
        return input_text


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


def test_primary_input_route_accepts_an_opaque_task_id_with_a_slash() -> None:
    tasks = _Tasks("task/7")
    inputs = _PrimaryInputs("task/7")
    with TestClient(
        create_task_http_application(
            config=FixedWorkspaceHttpConfig(
                workspace_id="workspace-demo",
                workbench_origin="http://127.0.0.1:5173",
            ),
            task_application=tasks,
            primary_input_application=inputs,
        )
    ) as client:
        saved = client.put(
            "/api/v1/tasks/task%2F7/primary-input",
            json={
                "inputKind": "pasted_text",
                "fileName": None,
                "content": "Product details",
            },
        )

    assert saved.status_code == 200
    assert saved.json()["taskId"] == "task/7"
    assert tasks.seen_task_ids == [TaskId("task/7")]


def test_result_routes_require_injected_coordinator_and_preserve_idempotent_replay(  # noqa: E501
) -> None:
    tasks = _Tasks()
    results = _Results()
    application = create_task_http_application(
        config=FixedWorkspaceHttpConfig(
            workspace_id="workspace-demo",
            workbench_origin="http://127.0.0.1:5173",
        ),
        task_application=tasks,
        primary_input_application=_PrimaryInputs(),
        result_application=results,
        pipeline_coordinator=_Coordinator(),
    )
    with TestClient(application) as client:
        first = client.post(
            "/api/v1/tasks/task-1/commands/generate-result",
            headers={"Idempotency-Key": "result-retry-1"},
            json={"expectedInputRevision": 0},
        )
        replay = client.post(
            "/api/v1/tasks/task-1/commands/generate-result",
            headers={"Idempotency-Key": "result-retry-1"},
            json={"expectedInputRevision": 0},
        )
        current = client.get("/api/v1/tasks/task-1/current-result")

    assert first.status_code == 201
    assert first.headers["location"].endswith("/current-result")
    assert replay.status_code == 200
    assert "location" not in replay.headers
    assert current.status_code == 200
    assert current.json()["productIntake"] == {"candidate": "intake"}
    assert results.calls == [
        ("task-1", "result-retry-1", 0),
        ("task-1", "result-retry-1", 0),
    ]


def test_result_routes_fail_closed_without_injected_coordinator() -> None:
    with pytest.raises(ValueError, match="pipeline_coordinator is required"):
        create_task_http_application(
            config=FixedWorkspaceHttpConfig(
                workspace_id="workspace-demo",
                workbench_origin="http://127.0.0.1:5173",
            ),
            task_application=_Tasks(),
            primary_input_application=_PrimaryInputs(),
            result_application=_Results(),
        )
