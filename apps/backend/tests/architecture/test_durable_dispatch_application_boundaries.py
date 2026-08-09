"""Architecture boundaries for private Durable Dispatch application ports."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ai_ecommerce_agent.modules.durable_dispatch import public

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_APPLICATION_ROOT = (
    _BACKEND_ROOT
    / "src"
    / "ai_ecommerce_agent"
    / "modules"
    / "durable_dispatch"
    / "application"
)
_PRODUCTION_FILES = (
    _APPLICATION_ROOT / "__init__.py",
    _APPLICATION_ROOT / "ports.py",
)
_ALLOWED_RELATIVE_IMPORTS: dict[Path, frozenset[tuple[int, str | None]]] = {
    _APPLICATION_ROOT / "__init__.py": frozenset({(1, "ports")}),
    _APPLICATION_ROOT / "ports.py": frozenset(
        {(2, "domain.identity"), (2, "domain.snapshots")}
    ),
}
_ALLOWED_STDLIB_IMPORTS: dict[Path, frozenset[str]] = {
    _APPLICATION_ROOT / "__init__.py": frozenset(),
    _APPLICATION_ROOT / "ports.py": frozenset({"__future__", "typing"}),
}
_ALLOWED_ABSOLUTE_IMPORTS: dict[Path, frozenset[str]] = {
    _APPLICATION_ROOT / "__init__.py": frozenset(),
    _APPLICATION_ROOT / "ports.py": frozenset(
        {
            "ai_ecommerce_agent.application.ports",
            "ai_ecommerce_agent.shared_kernel",
        }
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


def test_application_ports_have_only_framework_neutral_allowlisted_imports() -> None:
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    assert (node.level, node.module) in _ALLOWED_RELATIVE_IMPORTS[path]
                    continue
                imported_names = [node.module or ""]
            else:
                continue
            for imported in imported_names:
                if imported in _ALLOWED_ABSOLUTE_IMPORTS[path]:
                    continue
                root_name = imported.split(".", 1)[0]
                assert root_name in _ALLOWED_STDLIB_IMPORTS[path], (
                    f"{path} imports disallowed module {imported!r}"
                )
                assert not imported.startswith(_FORBIDDEN_IMPORT_PREFIXES), (
                    f"{path} imports forbidden module {imported!r}"
                )


def _import_time_calls(tree: ast.Module) -> list[ast.Call]:
    """Collect calls executed while importing modules/classes.

    Function and method bodies are intentionally skipped. Their decorators,
    defaults, annotations, and return annotations are still visited because
    those expressions execute while the definition is created.
    """

    calls: list[ast.Call] = []

    def visit(node: ast.AST) -> None:
        if isinstance(node, ast.Call):
            calls.append(node)
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
                visit(decorator)
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
    return calls


def test_protocols_use_only_exact_bare_runtime_checkable_decorators() -> None:
    path = _APPLICATION_ROOT / "ports.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    protocol_classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    assert [node.name for node in protocol_classes] == [
        "WorkIntentRepositoryPort",
        "DurableDispatchUnitOfWork",
        "DurableDispatchUnitOfWorkFactory",
    ]
    for protocol_class in protocol_classes:
        assert len(protocol_class.decorator_list) == 1
        decorator = protocol_class.decorator_list[0]
        assert isinstance(decorator, ast.Name)
        assert decorator.id == "runtime_checkable"


def test_application_ports_have_no_import_time_resource_or_behavior_calls() -> None:
    for path, tree in _trees():
        calls = _import_time_calls(tree)
        assert not calls, (
            f"{path} performs undeclared import-time call(s): "
            f"{[_dotted_name(call.func) for call in calls]!r}"
        )


def test_import_time_guard_rejects_runtime_checkable_calls() -> None:
    tree = ast.parse(
        """
from typing import Protocol, runtime_checkable

@runtime_checkable
class Allowed(Protocol):
    pass

@runtime_checkable()
class RejectedDecorator(Protocol):
    pass

class RejectedClass:
    token = runtime_checkable()

value = runtime_checkable()

def rejected_function(default=runtime_checkable()):
    pass
"""
    )
    calls = _import_time_calls(tree)
    unexpected = [_dotted_name(call.func) for call in calls]
    assert unexpected == [
        "runtime_checkable",
        "runtime_checkable",
        "runtime_checkable",
        "runtime_checkable",
    ]


def test_application_ports_remain_private_to_durable_dispatch() -> None:
    for name in (
        "DurableDispatchUnitOfWork",
        "DurableDispatchUnitOfWorkFactory",
        "WorkIntentRepositoryPort",
    ):
        assert not hasattr(public, name)
