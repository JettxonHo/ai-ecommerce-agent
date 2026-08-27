"""Tests-first Slice B contract for the frozen Needs Input HTTP surface.

The route module is imported from inside each test so collection succeeds while
the absent HTTP/composition seam remains an executable behavioral RED.
"""

# FastAPI/Starlette's TestClient is an untyped local framework helper.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportUnusedFunction=false, reportCallIssue=false

from __future__ import annotations

import importlib
import socket
import warnings
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest
from starlette.exceptions import StarletteDeprecationWarning

warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)

from fastapi.testclient import TestClient  # noqa: E402
from pytest_socket import SocketBlockedError, _true_socket  # noqa: E402

from ai_ecommerce_agent.modules.task_management.public import (  # noqa: E402
    TaskSnapshot,
    TaskStatus,
)
from ai_ecommerce_agent.shared_kernel import Revision, TaskId  # noqa: E402

pytestmark = pytest.mark.contract

NOW = datetime(2026, 8, 24, 15, 30, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _allow_testclient_socketpair(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow TestClient's local socketpair while blocking network I/O."""

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


def _load_http_contract() -> tuple[Any, Any, Any]:
    """Load public contracts plus the route/composition seam dynamically."""

    public = importlib.import_module("ai_ecommerce_agent.modules.needs_input.public")
    routes = importlib.import_module(
        "ai_ecommerce_agent.entrypoints.http.needs_input_routes"
    )
    http = importlib.import_module("ai_ecommerce_agent.entrypoints.http.app")
    return public, routes, http


def _task(task_id: str = "task-needs-input", *, revision: int = 2) -> TaskSnapshot:
    return TaskSnapshot(
        task_id=TaskId(task_id),
        task_name="Needs Input launch",
        product_category="Backpack",
        promotion_goal="Awareness",
        task_status=TaskStatus.WAITING_FOR_INPUT,
        revision=Revision(revision),
        current_stage=None,
        active_run_id=None,
        latest_run_id=None,
        waiting_reason="verified competitor evidence is missing",
        updated_at=NOW,
    )


@dataclass(frozen=True, slots=True)
class _NeedsInputState:
    request: Any
    current: Any


class _Tasks:
    def __init__(self, task: TaskSnapshot) -> None:
        self.task = task

    def get_task(self, query: object) -> TaskSnapshot:
        assert query.task_id == self.task.task_id  # type: ignore[attr-defined]
        return self.task


class _PrimaryInputs:
    """Only the composition dependency is needed for these route tests."""


class _NeedsInput:
    def __init__(self, public: Any, state: _NeedsInputState) -> None:
        self.public = public
        self.state = state
        self.calls: list[Any] = []
        self.error: Exception | None = None
        self.replay = False
        self.resolved_request: Any | None = None

    def get_action_request(self, action_request_id: str) -> Any:
        for request in (self.state.request, self.state.current):
            if action_request_id == request.action_request_id:
                return request
        raise self.public.NeedsInputApplicationError(
            "not_found", "internal action request detail must not escape"
        )

    def get_needs_input_action_request(self, action_request_id: str) -> Any:
        return self.get_action_request(action_request_id)

    def get_current_request(self, task_id: TaskId) -> Any:
        if task_id != self.state.current.task_id:
            return None
        return self.state.current

    def resolve(self, command: Any) -> Any:
        self.calls.append(command)
        if self.error is not None:
            raise self.error
        if self.replay:
            assert self.resolved_request is not None
            resolved = self.resolved_request
        else:
            resolved = replace(
                self.state.request,
                revision=self.state.request.revision.next(),
                status=self.public.NeedsInputStatus.RESOLVED,
                resolution_idempotency_key=command.idempotency_key,
                resolution_type=command.resolution_type,
                resolution_payload=dict(command.resolution_payload),
                resolved_at=NOW,
                updated_at=NOW,
            )
            self.resolved_request = resolved
        return SimpleNamespace(
            action_request=resolved,
            task_id=self.state.request.task_id,
        )

    def resolve_needs_input(self, command: Any) -> Any:
        return self.resolve(command)


def _request(
    public: Any, *, action_request_id: str = "action-1", revision: int = 2
) -> Any:
    return public.NeedsInputActionRequestSnapshot(
        action_request_id=action_request_id,
        task_id=TaskId("task-needs-input"),
        revision=Revision(revision),
        status=public.NeedsInputStatus.OPEN,
        reason_type="missing_information",
        reason_summary="verified competitor evidence is missing",
        affected_stages=("product_positioning",),
        source_references=(),
        conflict_values=(),
        allowed_resolution_types=("provide_source_reference", "cancel_path"),
        expected_recovery=public.NeedsInputExpectedRecovery.RERUN,
        superseded_by=None,
        created_at=NOW,
        updated_at=NOW,
    )


def _client(public: Any, http: Any, needs: _NeedsInput) -> TestClient:
    return TestClient(
        http.create_task_http_application(
            config=http.FixedWorkspaceHttpConfig(
                workspace_id="workspace-demo",
                workbench_origin="http://127.0.0.1:5173",
            ),
            task_application=_Tasks(_task()),
            primary_input_application=_PrimaryInputs(),
            needs_input_application=needs,
        )
    )


def test_get_request_and_task_overview_preserve_frozen_reference_shapes() -> None:
    public, _routes, http = _load_http_contract()
    request = _request(public)
    needs = _NeedsInput(public, _NeedsInputState(request=request, current=request))

    with _client(public, http, needs) as client:
        resource = client.get("/api/v1/needs-input-requests/action-1")
        overview = client.get("/api/v1/tasks/task-needs-input")

    assert resource.status_code == 200
    assert set(resource.json()) == {
        "actionRequestId",
        "taskId",
        "revision",
        "status",
        "reasonType",
        "reasonSummary",
        "affectedStages",
        "sourceReferences",
        "conflictValues",
        "allowedResolutionTypes",
        "expectedRecovery",
        "supersededBy",
    }
    assert resource.json()["sourceReferences"] == []
    assert resource.json()["conflictValues"] == []
    assert overview.status_code == 200
    assert overview.json()["needsInputRequest"] == {
        "resourceKind": "needs_input",
        "resourceId": "action-1",
        "revision": 2,
    }


def test_resolve_is_revision_bound_and_same_key_replays_canonical_result() -> None:
    public, _routes, http = _load_http_contract()
    request = _request(public)
    needs = _NeedsInput(public, _NeedsInputState(request=request, current=request))

    body = {
        "expectedRevision": 2,
        "resolution": {
            "resolutionType": "provide_source_reference",
            "sourceReferences": [
                {"resourceKind": "source_version", "resourceId": "source-1"}
            ],
            "notes": "bounded evidence reference",
        },
    }
    with _client(public, http, needs) as client:
        first = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "resolve-1",
            },
            json=body,
        )
        needs.replay = True
        replay = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "resolve-1",
            },
            json=body,
        )

    assert first.status_code == 200
    assert replay.status_code == 200
    assert first.json() == replay.json()
    assert first.json()["actionRequest"]["status"] == "resolved"
    assert first.json()["actionRequest"]["revision"] == 3
    assert first.json()["task"] == {"taskId": "task-needs-input"}
    assert len(needs.calls) == 2
    assert needs.calls[0].expected_revision == Revision(2)
    assert needs.calls[0].idempotency_key == "resolve-1"


def test_resolve_rejects_stale_terminal_and_wrong_owner_safely() -> None:
    public, _routes, http = _load_http_contract()
    request = _request(public)
    needs = _NeedsInput(public, _NeedsInputState(request=request, current=request))
    body = {
        "expectedRevision": 2,
        "resolution": {
            "resolutionType": "cancel_path",
            "notes": "cancel this path",
        },
    }

    with _client(public, http, needs) as client:
        needs.error = public.NeedsInputApplicationError(
            "revision_conflict", "secret database detail must not escape"
        )
        stale = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "resolve-stale",
            },
            json=body,
        )
        needs.error = public.NeedsInputApplicationError(
            "capability_conflict", "secret database detail must not escape"
        )
        terminal = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "resolve-terminal",
            },
            json=body,
        )
        needs.error = public.NeedsInputApplicationError(
            "ownership_conflict", "secret database detail must not escape"
        )
        wrong_owner = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "resolve-owner",
            },
            json=body,
        )

    assert stale.status_code == 409
    assert terminal.status_code == 409
    assert wrong_owner.status_code == 409
    for response in (stale, terminal, wrong_owner):
        assert "secret database detail" not in response.text
        assert response.headers["content-type"].startswith("application/problem+json")


def test_resolve_rejects_wrong_origin_and_unbounded_or_unknown_resolution() -> None:
    public, _routes, http = _load_http_contract()
    request = _request(public)
    needs = _NeedsInput(public, _NeedsInputState(request=request, current=request))

    with _client(public, http, needs) as client:
        wrong_origin = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "https://attacker.invalid",
                "Idempotency-Key": "resolve-origin",
            },
            json={
                "expectedRevision": 2,
                "resolution": {"resolutionType": "cancel_path"},
            },
        )
        unknown = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "resolve-unknown",
            },
            json={
                "expectedRevision": 2,
                "resolution": {"resolutionType": "invented_action"},
            },
        )
        oversized = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "resolve-large",
            },
            json={
                "expectedRevision": 2,
                "resolution": {
                    "resolutionType": "cancel_path",
                    "notes": "x" * 4097,
                },
            },
        )

    assert wrong_origin.status_code == 400
    assert unknown.status_code == 422
    assert oversized.status_code == 422
    assert needs.calls == []


def test_resolution_notes_use_utf8_bytes_before_application_call() -> None:
    """Notes are bounded by UTF-8 bytes, while a valid near-limit value passes."""

    public, _routes, http = _load_http_contract()
    request = _request(public)
    oversized_needs = _NeedsInput(
        public, _NeedsInputState(request=request, current=request)
    )
    oversized_notes = "界" * 2048
    oversized_resolution = {
        "resolutionType": "provide_source_reference",
        "sourceReferences": [
            {"resourceKind": "source_version", "resourceId": "source-1"}
        ],
        "notes": oversized_notes,
    }
    oversized_body = {"expectedRevision": 2, "resolution": oversized_resolution}
    with _client(public, http, oversized_needs) as client:
        oversized = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "fixture-a",
            },
            json=oversized_body,
        )

    assert len(oversized_notes.encode("utf-8")) > 4096
    assert len(oversized_notes) <= 4096
    assert oversized.status_code == 422
    assert oversized_needs.calls == []

    accepted_needs = _NeedsInput(
        public, _NeedsInputState(request=request, current=request)
    )
    accepted_notes = "界" * 1365
    accepted_body = {
        "expectedRevision": 2,
        "resolution": {**oversized_resolution, "notes": accepted_notes},
    }
    with _client(public, http, accepted_needs) as client:
        accepted = client.post(
            "/api/v1/needs-input-requests/action-1/commands/resolve",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Idempotency-Key": "fixture-b",
            },
            json=accepted_body,
        )

    assert len(accepted_notes.encode("utf-8")) <= 4096
    assert accepted.status_code == 200
    assert len(accepted_needs.calls) == 1


def test_task_overview_drops_obsolete_reference_after_newer_generation() -> None:
    public, _routes, http = _load_http_contract()
    old = replace(
        _request(public, action_request_id="action-old", revision=2),
        revision=Revision(3),
        status=public.NeedsInputStatus.SUPERSEDED,
        superseded_by="action-new",
    )
    newer = _request(public, action_request_id="action-new", revision=0)
    needs = _NeedsInput(public, _NeedsInputState(request=old, current=newer))

    with _client(public, http, needs) as client:
        overview = client.get("/api/v1/tasks/task-needs-input")
        old_read = client.get("/api/v1/needs-input-requests/action-old")

    assert overview.status_code == 200
    assert overview.json()["needsInputRequest"] == {
        "resourceKind": "needs_input",
        "resourceId": "action-new",
        "revision": 0,
    }
    assert old_read.status_code == 200
    assert old_read.json()["status"] == "superseded"
    assert old_read.json()["supersededBy"] == {
        "resourceKind": "needs_input",
        "resourceId": "action-new",
        "revision": 0,
    }
