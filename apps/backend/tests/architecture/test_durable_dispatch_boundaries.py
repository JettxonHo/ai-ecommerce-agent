"""Architecture boundaries for the Durable Dispatch contract foundation."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_DISPATCH_ROOT = (
    _BACKEND_ROOT / "src" / "ai_ecommerce_agent" / "modules" / "durable_dispatch"
)
_PRODUCTION_FILES = (
    _DISPATCH_ROOT / "__init__.py",
    _DISPATCH_ROOT / "domain" / "__init__.py",
    _DISPATCH_ROOT / "domain" / "identity.py",
    _DISPATCH_ROOT / "domain" / "status.py",
    _DISPATCH_ROOT / "domain" / "envelope.py",
    _DISPATCH_ROOT / "domain" / "ownership.py",
    _DISPATCH_ROOT / "domain" / "snapshots.py",
    _DISPATCH_ROOT / "public.py",
)
_ALLOWED_RELATIVE_IMPORTS: dict[Path, frozenset[tuple[int, str | None]]] = {
    _DISPATCH_ROOT / "__init__.py": frozenset(),
    _DISPATCH_ROOT / "domain" / "__init__.py": frozenset(),
    _DISPATCH_ROOT / "domain" / "identity.py": frozenset(),
    _DISPATCH_ROOT / "domain" / "status.py": frozenset(),
    _DISPATCH_ROOT / "domain" / "envelope.py": frozenset({(1, "identity")}),
    _DISPATCH_ROOT / "domain" / "ownership.py": frozenset({(1, "identity")}),
    _DISPATCH_ROOT / "domain" / "snapshots.py": frozenset(
        {(1, "envelope"), (1, "identity"), (1, "ownership"), (1, "status")}
    ),
    _DISPATCH_ROOT / "public.py": frozenset(
        {
            (1, "domain.envelope"),
            (1, "domain.identity"),
            (1, "domain.ownership"),
            (1, "domain.snapshots"),
            (1, "domain.status"),
            (1, "application.lease_commands"),
            (1, "application.lease_errors"),
            (1, "application.lease_protocols"),
            (1, "application.control_commands"),
            (1, "application.control_errors"),
            (1, "application.control_protocols"),
            (1, "application.control_queries"),
            (1, "application.control_results"),
        }
    ),
}
_ALLOWED_STDLIB_IMPORTS = {
    "__future__",
    "dataclasses",
    "datetime",
    "enum",
    "typing",
    "uuid",
}
_ALLOWED_ABSOLUTE_IMPORTS = {"ai_ecommerce_agent.shared_kernel"}
_PATH_STDLIB_IMPORTS: dict[Path, frozenset[str]] = {
    _DISPATCH_ROOT / "domain" / "ownership.py": frozenset(
        {"__future__", "dataclasses", "datetime"}
    ),
    _DISPATCH_ROOT / "domain" / "snapshots.py": frozenset(
        {"__future__", "dataclasses"}
    ),
}
_PATH_ABSOLUTE_IMPORTS: dict[Path, frozenset[str]] = {
    _DISPATCH_ROOT / "domain" / "ownership.py": frozenset(),
    _DISPATCH_ROOT / "domain" / "snapshots.py": frozenset(
        {"ai_ecommerce_agent.shared_kernel"}
    ),
}
_FORBIDDEN_IMPORT_PREFIXES = (
    "sqlalchemy",
    "psycopg",
    "fastapi",
    "starlette",
    "langgraph",
    "openai",
    "anthropic",
    "os",
    "pathlib",
    "socket",
    "subprocess",
    "dotenv",
)


def _dotted_name(node: ast.AST) -> str | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _trees() -> list[tuple[Path, ast.Module]]:
    return [
        (path, ast.parse(path.read_text(encoding="utf-8")))
        for path in _PRODUCTION_FILES
    ]


def test_durable_dispatch_contract_files_are_framework_neutral() -> None:
    for path, tree in _trees():
        allowed_stdlib_imports = _PATH_STDLIB_IMPORTS.get(
            path, frozenset(_ALLOWED_STDLIB_IMPORTS)
        )
        allowed_absolute_imports = _PATH_ABSOLUTE_IMPORTS.get(
            path, frozenset(_ALLOWED_ABSOLUTE_IMPORTS)
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    assert (node.level, node.module) in _ALLOWED_RELATIVE_IMPORTS[
                        path
                    ], (
                        f"{path} imports an undeclared relative module "
                        f"{node.module!r} at level {node.level}"
                    )
                    continue
                imported_names = [node.module or ""]
            else:
                continue
            for imported in imported_names:
                if imported in allowed_absolute_imports:
                    continue
                root_name = imported.split(".", 1)[0]
                assert root_name in allowed_stdlib_imports, (
                    f"{path} imports disallowed module {imported!r}"
                )
                assert not imported.startswith(_FORBIDDEN_IMPORT_PREFIXES), (
                    f"{path} imports forbidden module {imported!r}"
                )


def _allowed_typevar_calls(tree: ast.Module) -> set[int]:
    allowed: set[int] = set()
    for statement in tree.body:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        value = statement.value
        if not isinstance(target, ast.Name) or target.id != "_IdentityT":
            continue
        if not isinstance(value, ast.Call) or _dotted_name(value.func) != "TypeVar":
            continue
        if len(value.args) != 1 or len(value.keywords) != 1:
            continue
        bound_keyword = value.keywords[0]
        if bound_keyword.arg != "bound":
            continue
        bound_name = bound_keyword.value
        if (
            not isinstance(bound_name, ast.Constant)
            or bound_name.value != "_OpaqueDispatchIdentity"
        ):
            continue
        typevar_name = value.args[0]
        if (
            not isinstance(typevar_name, ast.Constant)
            or typevar_name.value != "_IdentityT"
        ):
            continue
        allowed.add(id(value))
    return allowed


def _import_time_calls(tree: ast.Module) -> tuple[list[ast.Call], set[int], set[int]]:
    calls: list[ast.Call] = []
    allowed_dataclass_calls: set[int] = set()

    def visit(node: ast.AST, *, class_decorator: bool = False) -> None:
        if isinstance(node, ast.Call):
            calls.append(node)
            if class_decorator and _dotted_name(node.func) == "dataclass":
                allowed_dataclass_calls.add(id(node))
            visit(node.func)
            for argument in node.args:
                visit(argument)
            for keyword in node.keywords:
                visit(keyword.value)
            return

        if isinstance(node, ast.Module):
            for statement in node.body:
                visit(statement)
            return

        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                visit(decorator, class_decorator=True)
            for base in node.bases:
                visit(base)
            for keyword in node.keywords:
                visit(keyword.value)
            for statement in node.body:
                visit(statement)
            return

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                visit(decorator)
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
    return calls, allowed_dataclass_calls, _allowed_typevar_calls(tree)


def test_durable_dispatch_contract_files_have_no_module_scope_calls() -> None:
    for path, tree in _trees():
        calls, allowed_dataclass_calls, allowed_typevar_calls = _import_time_calls(tree)
        for call in calls:
            call_name = _dotted_name(call.func)
            if id(call) in allowed_dataclass_calls or id(call) in allowed_typevar_calls:
                continue
            raise AssertionError(
                f"{path} performs undeclared module-scope call {call_name!r}"
            )


def test_module_scope_call_guard_rejects_non_decorator_calls() -> None:
    tree = ast.parse(
        """
from dataclasses import dataclass
from typing import TypeVar
from uuid import uuid4

_IdentityT = TypeVar("_IdentityT", bound="_OpaqueDispatchIdentity")

@dataclass(frozen=True)
class Allowed:
    pass

class Rejected:
    token = uuid4()

value = dataclass()
"""
    )
    calls, allowed_dataclass_calls, allowed_typevar_calls = _import_time_calls(tree)

    unexpected = [
        _dotted_name(call.func)
        for call in calls
        if id(call) not in allowed_dataclass_calls
        and id(call) not in allowed_typevar_calls
    ]
    assert unexpected == ["uuid4", "dataclass"]


def test_durable_dispatch_package_imports_cleanly() -> None:
    import importlib

    public = importlib.import_module(
        "ai_ecommerce_agent.modules.durable_dispatch.public"
    )
    assert public.__name__ == "ai_ecommerce_agent.modules.durable_dispatch.public"
