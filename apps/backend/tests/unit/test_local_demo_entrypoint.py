"""Tests for the private local-demo composition seam."""

# Test doubles deliberately stand in for the typed SQLAlchemy compositions;
# keep strict checking for production code without expanding their fixture API.
# pyright: reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false

from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit


def test_local_demo_entrypoint_exposes_a_runtime_composition() -> None:
    """The local operator path has one explicit composition seam."""

    module = importlib.import_module("ai_ecommerce_agent.bootstrap.local_demo")

    assert hasattr(module, "LocalDemoConfig")
    assert hasattr(module, "LocalDemoComposition")
    assert hasattr(module, "compose_local_demo")


def test_local_demo_config_rejects_non_loopback_workbench_origin() -> None:
    """The private executable still honours the fixed-workspace boundary."""

    module = importlib.import_module("ai_ecommerce_agent.bootstrap.local_demo")

    with pytest.raises(ValueError, match="loopback"):
        module.LocalDemoConfig(
            database_url="postgresql+psycopg://user:password@127.0.0.1:55432/database",
            workspace_id="local-demo",
            workbench_origin="http://192.0.2.10:5173",
        )


def test_local_demo_config_reads_only_explicit_operator_values() -> None:
    """Provider settings are irrelevant to the local scripted composition."""

    module = importlib.import_module("ai_ecommerce_agent.bootstrap.local_demo")

    config = module.LocalDemoConfig.from_environment(
        {
            "MVP0_LOCAL_DEMO_DATABASE_URL": (
                "postgresql+psycopg://user:password@127.0.0.1:55432/database"
            ),
            "MVP0_LOCAL_DEMO_WORKSPACE_ID": "local-demo",
            "MVP0_LOCAL_DEMO_WORKBENCH_ORIGIN": "http://127.0.0.1:5173",
            "PROVIDER_SECRET_SENTINEL": "must-not-be-read-or-used",
        }
    )

    assert config.workspace_id == "local-demo"
    assert config.workbench_origin == "http://127.0.0.1:5173"


def test_local_demo_composition_binds_existing_seams_and_closes_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The private graph delegates to existing compositions and owns cleanup."""

    module = importlib.import_module("ai_ecommerce_agent.bootstrap.local_demo")

    class FakeParticipant:
        def __init__(self, name: str) -> None:
            self.name = name
            self.application = object()
            self.close_calls = 0

        def close(self) -> None:
            self.close_calls += 1

    task = FakeParticipant("task")
    primary = FakeParticipant("primary")
    result = FakeParticipant("result")
    result.coordinator = object()
    result.export_application = object()
    app = SimpleNamespace(router=SimpleNamespace())
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(
        module,
        "compose_task_management_postgres",
        lambda config: (calls.append(("task", config)), task)[1],
    )
    monkeypatch.setattr(
        module,
        "compose_primary_input_postgres",
        lambda config: (calls.append(("primary", config)), primary)[1],
    )
    monkeypatch.setattr(
        module,
        "compose_deterministic_result_postgres",
        lambda config: (calls.append(("result", config)), result)[1],
    )
    monkeypatch.setattr(module, "create_task_http_application", lambda **_: app)

    composition = module.compose_local_demo(
        module.LocalDemoConfig(
            database_url="postgresql+psycopg://user:password@127.0.0.1:55432/database",
            workspace_id="local-demo",
            workbench_origin="http://127.0.0.1:5173",
        )
    )

    assert composition.application is app
    assert [name for name, _ in calls] == ["task", "primary", "result"]
    assert app.router.lifespan_context is not None
    composition.close()
    composition.close()
    assert task.close_calls == 1
    assert primary.close_calls == 1
    assert result.close_calls == 1


def test_local_demo_partial_construction_closes_created_participants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed later adapter cannot leak an earlier SQLAlchemy engine."""

    module = importlib.import_module("ai_ecommerce_agent.bootstrap.local_demo")

    class FakeParticipant:
        def __init__(self) -> None:
            self.application = object()
            self.close_calls = 0

        def close(self) -> None:
            self.close_calls += 1

    task = FakeParticipant()
    monkeypatch.setattr(module, "compose_task_management_postgres", lambda _: task)

    def fail_primary(_: object) -> object:
        raise RuntimeError("primary composition failed")

    monkeypatch.setattr(module, "compose_primary_input_postgres", fail_primary)

    with pytest.raises(RuntimeError, match="primary composition failed"):
        module.compose_local_demo(
            module.LocalDemoConfig(
                database_url="postgresql+psycopg://user:password@127.0.0.1:55432/database",
                workspace_id="local-demo",
                workbench_origin="http://127.0.0.1:5173",
            )
        )

    assert task.close_calls == 1
