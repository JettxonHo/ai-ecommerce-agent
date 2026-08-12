"""Focused unit tests for fixed-workspace HTTP adapter values and guards."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from ai_ecommerce_agent.entrypoints.http import FixedWorkspaceHttpConfig

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("workspace_id", "origin"),
    [
        ("workspace-demo", "http://127.0.0.1:5173"),
        ("workspace-demo", "http://localhost:5173"),
        ("workspace-demo", "http://[::1]:5173"),
        ("workspace-demo", "http://127.0.0.1"),
    ],
)
def test_config_accepts_exact_workspace_and_loopback_origin(
    workspace_id: str, origin: str
) -> None:
    config = FixedWorkspaceHttpConfig(workspace_id, origin)
    assert config.workspace_id == workspace_id
    assert config.workbench_origin == origin
    with pytest.raises(FrozenInstanceError):
        config.workspace_id = "other"  # type: ignore[misc]


@pytest.mark.parametrize(
    "workspace_id",
    [None, "", "   ", 1, True, object(), type("WorkspaceId", (str,), {})("x")],
)
def test_config_rejects_non_exact_or_blank_workspace_id(workspace_id: object) -> None:
    with pytest.raises((TypeError, ValueError), match="workspace_id"):
        FixedWorkspaceHttpConfig(workspace_id, "http://127.0.0.1:5173")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "origin",
    [
        None,
        "",
        "   ",
        "https://127.0.0.1:5173",
        "http://127.0.0.1:0",
        "http://127.0.0.1:65536",
        "http://127.0.0.1:not-a-port",
        "http://127.0.0.1:5173/",
        "http://127.0.0.1:5173/path",
        "http://127.0.0.1:5173?query=1",
        "http://127.0.0.1:5173?",
        "http://127.0.0.1:5173#fragment",
        "http://127.0.0.1:5173#",
        "http://user:pass@127.0.0.1:5173",
        "http://192.168.0.1:5173",
        "http://example.test:5173",
        "127.0.0.1:5173",
        "http://[127.0.0.1]:5173",
    ],
)
def test_config_rejects_unsafe_or_malformed_origin(origin: object) -> None:
    with pytest.raises((TypeError, ValueError), match="workbench_origin"):
        FixedWorkspaceHttpConfig("workspace-demo", origin)  # type: ignore[arg-type]
