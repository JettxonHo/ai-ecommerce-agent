"""Architecture evidence for the Durable Dispatch composition root."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import get_type_hints

import pytest

from ai_ecommerce_agent.bootstrap import durable_dispatch_postgres
from ai_ecommerce_agent.modules.durable_dispatch import public
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_protocols import (
    DurableDispatchLeaseApplication,
)
from ai_ecommerce_agent.platform.postgres import PostgresEngineConfig

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BOOTSTRAP_PATH = (
    _BACKEND_ROOT
    / "src"
    / "ai_ecommerce_agent"
    / "bootstrap"
    / "durable_dispatch_postgres.py"
)


class _Engine:
    def __init__(self) -> None:
        self.dispose_calls = 0

    def dispose(self) -> None:
        self.dispose_calls += 1


class _Application:
    def claim_next_work_intent(self, command: object) -> None:
        del command

    def heartbeat_work_intent_lease(self, command: object) -> None:
        del command


class _Factory:
    calls: list[tuple[object, str]] = []

    @classmethod
    def from_engine(cls, engine: object, *, schema: str) -> _Factory:
        cls.calls.append((engine, schema))
        return cls()


def test_composition_wires_one_engine_factory_and_protocol_without_connecting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _Engine()
    application = _Application()
    config = PostgresEngineConfig(
        database_url="postgresql+psycopg://user:password@127.0.0.1:5432/database"
    )
    seen_configs: list[PostgresEngineConfig] = []

    def create_engine(value: PostgresEngineConfig) -> _Engine:
        seen_configs.append(value)
        return engine

    def create_application(factory: object) -> _Application:
        assert isinstance(factory, _Factory)
        return application

    _Factory.calls.clear()
    monkeypatch.setattr(
        durable_dispatch_postgres, "create_postgres_engine", create_engine
    )
    monkeypatch.setattr(
        durable_dispatch_postgres,
        "DurableDispatchPostgresUnitOfWorkFactory",
        _Factory,
    )
    monkeypatch.setattr(
        durable_dispatch_postgres,
        "DurableDispatchLeaseApplicationService",
        create_application,
    )

    composition = durable_dispatch_postgres.compose_durable_dispatch_postgres(
        config, schema="mvp0_018l_application"
    )

    assert seen_configs == [config]
    assert _Factory.calls == [(engine, "mvp0_018l_application")]
    assert composition.engine is engine
    assert composition.lease_application is application
    assert isinstance(composition.lease_application, DurableDispatchLeaseApplication)
    annotations = get_type_hints(type(composition))
    assert set(annotations) == {"engine", "uow_factory", "lease_application"}
    assert annotations["lease_application"] is DurableDispatchLeaseApplication
    assert engine.dispose_calls == 0

    composition.close()
    assert engine.dispose_calls == 1


def test_composition_module_has_only_explicit_imports() -> None:
    tree = ast.parse(_BOOTSTRAP_PATH.read_text(encoding="utf-8"))
    allowed_absolute = {
        "sqlalchemy",
        "ai_ecommerce_agent.modules.durable_dispatch.application.lease_protocols",
        "ai_ecommerce_agent.modules.durable_dispatch.application.lease_services",
        "ai_ecommerce_agent.modules.durable_dispatch.infrastructure.uow",
        "ai_ecommerce_agent.platform.postgres",
    }
    allowed_stdlib = {"__future__", "dataclasses"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imported = [node.module or ""]
        else:
            continue
        for name in imported:
            assert name in allowed_absolute or name.split(".", 1)[0] in allowed_stdlib


def test_composition_has_no_import_time_io_or_background_work() -> None:
    tree = ast.parse(_BOOTSTRAP_PATH.read_text(encoding="utf-8"))
    calls, decorators = _import_time_effects(tree)
    assert [_dotted_name(call.func) for call in calls] == ["dataclass"]
    assert decorators == [
        ("class:DurableDispatchPostgresComposition", "dataclass", True)
    ]

    source = _BOOTSTRAP_PATH.read_text(encoding="utf-8")
    assert "os.environ" not in source
    assert "connect(" not in source
    assert "create_all" not in source
    assert "alembic" not in source
    assert "worker" not in source.lower()


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix is not None else node.attr
    return None


def _import_time_effects(
    tree: ast.Module,
) -> tuple[list[ast.Call], list[tuple[str, str | None, bool]]]:
    """Inspect executable module/class expressions, not function bodies."""

    calls: list[ast.Call] = []
    decorators: list[tuple[str, str | None, bool]] = []

    def visit_call(node: ast.Call) -> None:
        calls.append(node)
        visit(node.func)
        for argument in node.args:
            visit(argument)
        for keyword in node.keywords:
            visit(keyword.value)

    def visit_decorator(node: ast.AST, scope: str) -> None:
        if isinstance(node, ast.Call):
            decorators.append((scope, _dotted_name(node.func), True))
            visit_call(node)
            return
        decorators.append((scope, _dotted_name(node), False))
        visit(node)

    def visit(node: ast.AST, *, class_name: str | None = None) -> None:
        if isinstance(node, ast.Call):
            visit_call(node)
            return
        if isinstance(node, ast.Module):
            for statement in node.body:
                visit(statement)
            return
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                visit_decorator(decorator, f"class:{node.name}")
            for base in node.bases:
                visit(base)
            for keyword in node.keywords:
                visit(keyword.value)
            for statement in node.body:
                visit(statement, class_name=node.name)
            return
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = (
                f"method:{class_name}.{node.name}"
                if class_name is not None
                else f"function:{node.name}"
            )
            for decorator in node.decorator_list:
                visit_decorator(decorator, scope)
            for default in node.args.defaults:
                visit(default)
            for default in node.args.kw_defaults:
                if default is not None:
                    visit(default)
            arguments = [
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            ]
            if node.args.vararg is not None:
                arguments.append(node.args.vararg)
            if node.args.kwarg is not None:
                arguments.append(node.args.kwarg)
            for argument in arguments:
                if argument.annotation is not None:
                    visit(argument.annotation)
            if node.returns is not None:
                visit(node.returns)
            return
        if isinstance(node, ast.Lambda):
            for default in node.args.defaults:
                visit(default)
            for default in node.args.kw_defaults:
                if default is not None:
                    visit(default)
            return
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return calls, decorators


def test_import_time_guard_rejects_behavior_decorators_and_class_calls() -> None:
    tree = ast.parse(
        """
from dataclasses import dataclass

@dataclass(frozen=True)
class Allowed:
    pass

@print
def leaked(default=uuid4()):
    pass

class Rejected:
    token = uuid4()

    @print
    def method(self):
        pass
"""
    )
    calls, decorators = _import_time_effects(tree)
    assert [_dotted_name(call.func) for call in calls] == [
        "dataclass",
        "uuid4",
        "uuid4",
    ]
    assert ("class:Allowed", "dataclass", True) in decorators
    assert ("function:leaked", "print", False) in decorators
    assert ("method:Rejected.method", "print", False) in decorators


def test_durable_public_facade_keeps_technical_composition_private() -> None:
    assert not any(
        hasattr(public, name)
        for name in (
            "DurableDispatchLeaseApplicationService",
            "DurableDispatchPostgresUnitOfWorkFactory",
            "DurableDispatchPostgresComposition",
            "Engine",
            "Session",
        )
    )
