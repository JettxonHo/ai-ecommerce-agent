"""Architecture boundaries for the primitive Workflow Checkpoint seam."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _BACKEND_ROOT / "src" / "ai_ecommerce_agent"
_ORCHESTRATION_ROOT = _SRC_ROOT / "orchestration"
_RUNTIME_ROOT = _ORCHESTRATION_ROOT / "workflow_runtime"
_PRODUCTION_FILES = (
    _ORCHESTRATION_ROOT / "__init__.py",
    _RUNTIME_ROOT / "__init__.py",
    _RUNTIME_ROOT / "checkpoint_state.py",
)
_ALLOWED_STDLIB_IMPORTS = {
    "__future__",
    "collections.abc",
    "dataclasses",
    "typing",
}
_ALLOWED_ABSOLUTE_IMPORTS = {"ai_ecommerce_agent.shared_kernel"}
_FORBIDDEN_IMPORT_PREFIXES = (
    "langgraph",
    "sqlalchemy",
    "psycopg",
    "fastapi",
    "starlette",
    "openai",
    "anthropic",
    "os",
    "pathlib",
    "socket",
    "subprocess",
    "dotenv",
)
_FORBIDDEN_CALL_NAMES = {
    "connect",
    "create_engine",
    "getenv",
    "open",
    "read_text",
    "write_text",
    "mkdir",
    "create_task",
}


def _trees() -> list[tuple[Path, ast.Module]]:
    return [
        (path, ast.parse(path.read_text(encoding="utf-8")))
        for path in _PRODUCTION_FILES
    ]


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


def _import_time_calls(tree: ast.Module) -> list[ast.Call]:
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


def test_workflow_runtime_has_exact_three_production_files() -> None:
    assert _ORCHESTRATION_ROOT.is_dir()
    assert _RUNTIME_ROOT.is_dir()
    assert set(_PRODUCTION_FILES) == {
        _ORCHESTRATION_ROOT / "__init__.py",
        _RUNTIME_ROOT / "__init__.py",
        _RUNTIME_ROOT / "checkpoint_state.py",
    }
    assert sorted(path.name for path in _ORCHESTRATION_ROOT.glob("*.py")) == [
        "__init__.py"
    ]
    assert sorted(path.name for path in _RUNTIME_ROOT.glob("*.py")) == [
        "__init__.py",
        "checkpoint_state.py",
    ]


def test_workflow_runtime_imports_only_stdlib_and_shared_identities() -> None:
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    raise AssertionError(f"{path} has relative import {node.module!r}")
                imported_names = [node.module or ""]
            else:
                continue
            for imported in imported_names:
                if imported in _ALLOWED_ABSOLUTE_IMPORTS:
                    continue
                assert imported in _ALLOWED_STDLIB_IMPORTS, (
                    f"{path} imports disallowed module {imported!r}"
                )
                assert not imported.startswith(_FORBIDDEN_IMPORT_PREFIXES), (
                    f"{path} imports forbidden module {imported!r}"
                )


def test_package_initializers_are_private_and_reexport_nothing() -> None:
    for path in (_ORCHESTRATION_ROOT / "__init__.py", _RUNTIME_ROOT / "__init__.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert not any(
            isinstance(node, (ast.Import, ast.ImportFrom)) for node in tree.body
        )
        assert not any(
            isinstance(node, (ast.Assign, ast.AnnAssign)) for node in tree.body
        )
        assert not any(
            isinstance(node, (ast.ClassDef, ast.FunctionDef)) for node in tree.body
        )


def test_checkpoint_module_has_no_import_time_io_or_mutable_global_state() -> None:
    path = _RUNTIME_ROOT / "checkpoint_state.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    calls = _import_time_calls(tree)
    assert [_dotted_name(call.func) for call in calls] == [
        "dataclass",
        "dataclass",
        "dataclass",
    ]
    assert all(_dotted_name(call.func) not in _FORBIDDEN_CALL_NAMES for call in calls)
    for statement in tree.body:
        if isinstance(statement, (ast.Assign, ast.AnnAssign)):
            raise AssertionError("checkpoint module must not define mutable globals")


def test_checkpoint_module_has_no_business_or_public_facade_imports() -> None:
    tree = ast.parse(
        (_RUNTIME_ROOT / "checkpoint_state.py").read_text(encoding="utf-8")
    )
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert not any(
        module.startswith("ai_ecommerce_agent.modules.") for module in imported
    )
    assert "ai_ecommerce_agent.modules" not in imported
