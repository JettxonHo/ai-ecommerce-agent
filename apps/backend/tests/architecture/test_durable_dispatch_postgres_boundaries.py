"""Architecture boundaries for the private Durable Dispatch PostgreSQL adapter."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Final, TypedDict

import pytest

from ai_ecommerce_agent.modules.durable_dispatch import infrastructure, public
from ai_ecommerce_agent.modules.durable_dispatch.application import errors
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure import (
    lease_repository,
    repositories,
    uow,
)

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_DISPATCH_ROOT = (
    _BACKEND_ROOT / "src" / "ai_ecommerce_agent" / "modules" / "durable_dispatch"
)


class _ImportRules(TypedDict):
    relative: frozenset[tuple[int, str]]
    absolute: frozenset[str]
    stdlib: frozenset[str]


_PRODUCTION_FILES: dict[Path, _ImportRules] = {
    _DISPATCH_ROOT / "application" / "errors.py": {
        "relative": frozenset(),
        "absolute": frozenset({"ai_ecommerce_agent.shared_kernel"}),
        "stdlib": frozenset({"__future__", "collections.abc"}),
    },
    _DISPATCH_ROOT / "infrastructure" / "repositories.py": {
        "relative": frozenset({(1, "mappings"), (1, "tables")}),
        "absolute": frozenset(
            {
                "ai_ecommerce_agent.modules.durable_dispatch.application.errors",
                "ai_ecommerce_agent.modules.durable_dispatch.domain.envelope",
                "ai_ecommerce_agent.modules.durable_dispatch.domain.identity",
                "ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots",
                "ai_ecommerce_agent.shared_kernel",
                "sqlalchemy",
                "sqlalchemy.exc",
                "sqlalchemy.orm",
            }
        ),
        "stdlib": frozenset({"__future__", "collections.abc", "typing"}),
    },
    _DISPATCH_ROOT / "infrastructure" / "lease_repository.py": {
        "relative": frozenset({(1, "mappings"), (1, "repositories"), (1, "tables")}),
        "absolute": frozenset(
            {
                "ai_ecommerce_agent.modules.durable_dispatch.application.errors",
                "ai_ecommerce_agent.modules.durable_dispatch.application.lease_commands",
                "ai_ecommerce_agent.modules.durable_dispatch.domain.identity",
                "ai_ecommerce_agent.modules.durable_dispatch.domain.ownership",
                "ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots",
                "ai_ecommerce_agent.modules.durable_dispatch.domain.status",
                "sqlalchemy",
                "sqlalchemy.orm",
            }
        ),
        "stdlib": frozenset({"__future__", "dataclasses", "typing"}),
    },
    _DISPATCH_ROOT / "infrastructure" / "uow.py": {
        "relative": frozenset(
            {(1, "lease_repository"), (1, "repositories"), (1, "tables")}
        ),
        "absolute": frozenset(
            {
                "ai_ecommerce_agent.modules.durable_dispatch.application.errors",
                "ai_ecommerce_agent.modules.durable_dispatch.application.ports",
                "ai_ecommerce_agent.platform.postgres.uow",
                "sqlalchemy",
                "sqlalchemy.exc",
                "sqlalchemy.orm",
            }
        ),
        "stdlib": frozenset({"__future__", "collections.abc", "types", "typing"}),
    },
}
_FORBIDDEN_NAMES: Final = {
    "AsyncEngine",
    "Connection",
    "create_engine",
    "execute_sql",
    "for_update",
    "skip_locked",
    "claim",
    "heartbeat",
    "takeover",
    "commit_fence",
    "worker",
    "poll",
}


def test_private_exports_and_public_facade_boundaries_are_exact() -> None:
    assert errors.__all__ == [
        "DurableDispatchConstraintError",
        "DurableDispatchPersistenceError",
        "DurableDispatchRevisionConflictError",
    ]
    assert repositories.__all__ == ["DurableDispatchPostgresWorkIntentRepository"]
    assert lease_repository.__all__ == [
        "DurableDispatchPostgresWorkIntentLeaseRepository"
    ]
    assert uow.__all__ == [
        "DurableDispatchPostgresUnitOfWork",
        "DurableDispatchPostgresUnitOfWorkFactory",
    ]
    assert not any(
        hasattr(public, name)
        for name in (
            "DurableDispatchPostgresWorkIntentRepository",
            "DurableDispatchPostgresWorkIntentLeaseRepository",
            "DurableDispatchPostgresUnitOfWork",
            "DurableDispatchPostgresUnitOfWorkFactory",
            "DurableDispatchPersistenceError",
        )
    )
    assert not any(
        hasattr(infrastructure, name)
        for name in (
            "DurableDispatchPostgresWorkIntentRepository",
            "DurableDispatchPostgresUnitOfWork",
            "DurableDispatchPostgresUnitOfWorkFactory",
        )
    )


def test_repository_has_no_transaction_lifecycle_methods() -> None:
    assert not any(
        hasattr(repositories.DurableDispatchPostgresWorkIntentRepository, name)
        for name in ("commit", "rollback", "close")
    )
    assert not any(
        hasattr(lease_repository.DurableDispatchPostgresWorkIntentLeaseRepository, name)
        for name in ("commit", "rollback", "close")
    )
    assert not any(
        hasattr(uow.DurableDispatchPostgresUnitOfWork, name)
        for name in ("session", "registry", "get_repository", "execute_sql")
    )


def test_adapter_imports_are_path_specific_and_framework_bounded() -> None:
    for path, rules in _PRODUCTION_FILES.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name in rules["absolute"], (
                        f"{path} imports {alias.name!r}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    assert (node.level, node.module) in rules["relative"], (
                        f"{path} imports relative {node.level}:{node.module}"
                    )
                else:
                    assert node.module in rules["stdlib"] | rules["absolute"], (
                        f"{path} imports {node.module!r}"
                    )


def test_adapter_contains_no_claim_lifecycle_or_resource_escape_symbols() -> None:
    for path in _PRODUCTION_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        forbidden_names: set[str] = set(_FORBIDDEN_NAMES)
        if path.name == "lease_repository.py":
            forbidden_names.discard("takeover")
        if path.name != "uow.py":
            forbidden_names.add("Engine")
        assert not names & forbidden_names, path
        assert not attributes & forbidden_names, path


def test_adapter_has_no_import_time_calls_or_decorators() -> None:
    for path in _PRODUCTION_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls: list[ast.Call] = []
        decorators: list[str] = []

        def visit(
            node: ast.AST,
            *,
            call_nodes: list[ast.Call] = calls,
            decorator_names: list[str] = decorators,
        ) -> None:
            if isinstance(node, ast.Call):
                call_nodes.append(node)
                return
            if isinstance(node, ast.Module):
                for statement in node.body:
                    visit(statement)
                return
            if isinstance(node, ast.ClassDef):
                decorator_names.extend(
                    decorator.id
                    for decorator in node.decorator_list
                    if isinstance(decorator, ast.Name)
                )
                for statement in node.body:
                    visit(statement)
                return
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorator_names.extend(
                    decorator.id
                    for decorator in node.decorator_list
                    if isinstance(decorator, ast.Name)
                )
                for default in node.args.defaults:
                    visit(default)
                for default in node.args.kw_defaults:
                    if default is not None:
                        visit(default)
                for argument in [
                    *node.args.posonlyargs,
                    *node.args.args,
                    *node.args.kwonlyargs,
                ]:
                    if argument.annotation is not None:
                        visit(argument.annotation)
                if node.returns is not None:
                    visit(node.returns)
                return
            for child in ast.iter_child_nodes(node):
                visit(child)

        visit(tree)
        assert calls == [], path
        expected = (
            ["property", "property", "classmethod"] if path.name == "uow.py" else []
        )
        assert decorators == expected, path
