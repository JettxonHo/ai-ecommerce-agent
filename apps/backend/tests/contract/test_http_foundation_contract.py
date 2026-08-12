"""Contract tests for the MVP-0 transport foundation.

The authored OpenAPI file remains the public HTTP authority.  This module
only exercises the adapter-owned framework boundary: fixed workspace
injection, same-origin writes, and safe foundation problem projections.
"""

# FastAPI/Starlette's current TestClient has no typed httpx2 dependency in the
# project's accepted runtime tuple; this file deliberately treats that
# framework test helper as an untyped boundary while preserving strict typing
# for production adapter code.
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportPrivateUsage=false, reportUnusedFunction=false, reportCallIssue=false

from __future__ import annotations

import builtins
import inspect
import os
import socket
import warnings
from typing import Annotated, get_type_hints

import pytest
from fastapi import FastAPI, Query
from pytest_socket import SocketBlockedError, _true_socket
from starlette.exceptions import StarletteDeprecationWarning
from starlette.requests import Request

from ai_ecommerce_agent.entrypoints.http import (
    FixedWorkspaceHttpConfig,
    create_http_application,
    fixed_workspace_id,
)

# Starlette 1.x emits a deprecation warning while importing TestClient when
# the optional ``httpx2`` package is unavailable.  The project already pins
# ``httpx`` transitively through the OpenAI SDK; suppress only this known
# adapter-test import warning while retaining the global warnings-as-errors
# policy for all runtime behavior.
warnings.filterwarnings("ignore", category=StarletteDeprecationWarning)
from fastapi.testclient import TestClient  # noqa: E402

pytestmark = pytest.mark.contract

_ORIGIN = "http://127.0.0.1:5173"
_WORKSPACE = "workspace-demo"
_EXPECTED_PROBLEM_KEYS = {"type", "title", "status", "detail", "instance", "action"}


@pytest.fixture(autouse=True)
def _allow_local_testclient_sockets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Permit TestClient's Unix socketpair while continuing to block network."""

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


def _app() -> FastAPI:
    return create_http_application(
        config=FixedWorkspaceHttpConfig(
            workspace_id=_WORKSPACE,
            workbench_origin=_ORIGIN,
        )
    )


def test_facade_is_exact_and_parent_package_does_not_reexport() -> None:
    """The stable internal facade has the exact names and callable signatures."""

    import ai_ecommerce_agent.entrypoints as entrypoints

    assert {name for name in dir(entrypoints) if not name.startswith("_")} <= {"http"}
    assert {
        name
        for name in dir(
            __import__("ai_ecommerce_agent.entrypoints.http", fromlist=["*"])
        )
        if not name.startswith("_")
    } >= {"FixedWorkspaceHttpConfig", "create_http_application", "fixed_workspace_id"}
    application_signature = inspect.signature(create_http_application)
    assert list(application_signature.parameters) == ["config"]
    assert (
        application_signature.parameters["config"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )
    assert get_type_hints(create_http_application) == {
        "config": FixedWorkspaceHttpConfig,
        "return": FastAPI,
    }
    request_signature = inspect.signature(fixed_workspace_id)
    assert list(request_signature.parameters) == ["request"]
    assert get_type_hints(fixed_workspace_id) == {"request": Request, "return": str}


def test_workspace_is_server_injected_and_client_values_have_no_authority() -> None:
    """A test-only endpoint can observe only the configured server scope."""

    app = _app()

    @app.post("/__contract/workspace")
    def workspace_probe(
        request: Request,
        workspace_id: str | None = None,
    ) -> dict[str, str | None]:
        # The endpoint intentionally accepts a workspace-shaped query value;
        # the adapter's request context remains the only authoritative value.
        return {
            "serverWorkspace": fixed_workspace_id(request),
            "clientWorkspace": workspace_id,
        }

    with TestClient(app) as client:
        response = client.post(
            "/__contract/workspace?workspace_id=attacker-workspace",
            headers={"X-Workspace-Id": "attacker-header", "Origin": _ORIGIN},
            json={"workspace_id": "attacker-body"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "serverWorkspace": _WORKSPACE,
        "clientWorkspace": "attacker-workspace",
    }
    assert "access-control-allow-origin" not in response.headers


def test_app_construction_performs_no_environment_filesystem_or_socket_io(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Factory construction is pure and does not acquire process resources."""

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("unexpected construction-time I/O")

    monkeypatch.setattr(os, "getenv", forbidden)
    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    app = _app()
    assert isinstance(app, FastAPI)


@pytest.mark.parametrize("method", ["get", "head"])
def test_read_methods_do_not_require_origin(method: str) -> None:
    """GET and HEAD stay usable at the accepted local boundary."""

    app = _app()
    route_method = getattr(app, method)

    @route_method("/__contract/read")
    def read_probe() -> dict[str, str]:
        return {"workspace": _WORKSPACE}

    with TestClient(app) as client:
        response = getattr(client, method)("/__contract/read")

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
@pytest.mark.parametrize("origin", [None, _ORIGIN])
def test_state_changing_methods_allow_missing_or_equal_origin(
    method: str, origin: str | None
) -> None:
    """Only an absent Origin or the exact configured origin proceeds."""

    app = _app()
    route_method = getattr(app, method)
    calls: list[str] = []

    @route_method("/__contract/write")
    def write_probe() -> dict[str, str]:
        calls.append(method)
        return {"status": "ok"}

    headers = {} if origin is None else {"Origin": origin}
    with TestClient(app) as client:
        response = getattr(client, method)("/__contract/write", headers=headers)

    assert response.status_code == 200
    assert calls == [method]
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
@pytest.mark.parametrize(
    "headers",
    [
        {"Origin": "http://evil.example"},
        {"Origin": f"{_ORIGIN}, {_ORIGIN}"},
        [("Origin", _ORIGIN), ("Origin", _ORIGIN)],
    ],
)
def test_state_changing_methods_reject_wrong_or_duplicate_origin(
    method: str, headers: dict[str, str] | list[tuple[str, str]]
) -> None:
    """Wrong, malformed, and duplicate Origins fail before the handler."""

    app = _app()
    route_method = getattr(app, method)
    calls: list[str] = []

    @route_method("/__contract/write")
    def write_probe() -> dict[str, str]:
        calls.append(method)
        return {"status": "ok"}

    with TestClient(app) as client:
        response = getattr(client, method)("/__contract/write", headers=headers)

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "urn:ai-ecommerce-agent:problem:malformed-request",
        "title": "Malformed request",
        "status": 400,
        "detail": "The request Origin is not allowed.",
        "instance": "/__contract/write",
        "action": "correct_input",
    }
    assert calls == []


def test_unknown_route_is_safe_problem() -> None:
    """Framework routes and arbitrary unknown paths use the authored envelope."""

    with TestClient(_app()) as client:
        response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "urn:ai-ecommerce-agent:problem:not-found",
        "title": "Not found",
        "status": 404,
        "detail": "The requested resource was not found.",
        "instance": "/does-not-exist",
        "action": "none",
    }


def test_framework_docs_routes_are_not_enabled() -> None:
    """FastAPI docs/OpenAPI endpoints stay outside the runtime surface."""

    with TestClient(_app()) as client:
        responses = [client.get(path) for path in ("/openapi.json", "/docs", "/redoc")]

    assert [response.status_code for response in responses] == [404, 404, 404]
    assert all(
        response.headers["content-type"] == "application/problem+json"
        for response in responses
    )


def test_request_validation_is_safe_and_typed() -> None:
    """Validation exposes location and type code, never rejected data/message."""

    app = _app()

    @app.get("/__contract/validation")
    def validation_probe(
        count: Annotated[int, Query(ge=1)],
    ) -> dict[str, int]:
        return {"count": count}

    with TestClient(app) as client:
        response = client.get("/__contract/validation?count=not-an-int")

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    payload = response.json()
    assert set(payload) == _EXPECTED_PROBLEM_KEYS | {"fieldIssues"}
    assert payload["type"] == "urn:ai-ecommerce-agent:problem:validation-failed"
    assert payload["title"] == "Validation failed"
    assert payload["status"] == 422
    assert payload["action"] == "correct_input"
    assert payload["fieldIssues"] == [
        {"fieldPath": "query.count", "reasonCode": "int_parsing"}
    ]
    assert "not-an-int" not in response.text
    assert "valid integer" not in response.text


def test_unhandled_exception_is_safe_and_does_not_leak_details() -> None:
    """Unhandled endpoint exceptions become a fixed operator-action Problem."""

    app = _app()

    @app.get("/__contract/failure")
    def failure_probe() -> None:
        raise RuntimeError("secret provider payload")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/__contract/failure")

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "urn:ai-ecommerce-agent:problem:internal-error",
        "title": "Internal error",
        "status": 500,
        "detail": "The server could not complete the request.",
        "instance": "/__contract/failure",
        "action": "contact_operator",
    }
    assert "secret provider payload" not in response.text
