"""Architecture boundaries for private Durable Dispatch row mappings."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ai_ecommerce_agent.modules.durable_dispatch import infrastructure, public
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure import mappings

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_MAPPINGS_PATH = (
    _BACKEND_ROOT
    / "src"
    / "ai_ecommerce_agent"
    / "modules"
    / "durable_dispatch"
    / "infrastructure"
    / "mappings.py"
)
_ALLOWED_IMPORTS = {
    "__future__",
    "collections.abc",
    "datetime",
    "typing",
    "ai_ecommerce_agent.modules.durable_dispatch.domain.envelope",
    "ai_ecommerce_agent.modules.durable_dispatch.domain.identity",
    "ai_ecommerce_agent.modules.durable_dispatch.domain.ownership",
    "ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots",
    "ai_ecommerce_agent.modules.durable_dispatch.domain.status",
    "ai_ecommerce_agent.shared_kernel",
}
_FORBIDDEN_NAMES = {
    "Engine",
    "Session",
    "AsyncSession",
    "Connection",
    "create_engine",
    "sessionmaker",
    "create_all",
    "drop_all",
    "execute",
    "connect",
    "getenv",
    "load_dotenv",
    "WORK_INTENTS_TABLE",
    "DURABLE_DISPATCH_METADATA",
}


def test_mapping_module_has_exact_private_facade_and_no_generic_alias() -> None:
    assert mappings.__all__ == [
        "work_intent_row_to_snapshot",
        "work_intent_snapshot_to_insert_row",
        "work_intent_snapshot_to_update_values",
    ]
    assert not hasattr(mappings, "work_intent_snapshot_to_row")
    assert not any(hasattr(mappings, name) for name in _FORBIDDEN_NAMES)


def test_infrastructure_package_and_public_facade_do_not_reexport_mappings() -> None:
    assert not any(hasattr(infrastructure, name) for name in mappings.__all__)
    assert not any(hasattr(public, name) for name in mappings.__all__)


def test_mapping_module_imports_only_framework_neutral_dependencies() -> None:
    tree = ast.parse(_MAPPINGS_PATH.read_text(encoding="utf-8"))
    _assert_allowed_imports(tree)


def _assert_allowed_imports(tree: ast.Module) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise AssertionError("relative imports are not allowed")
            imported_names = [node.module or ""]
        else:
            continue
        for imported in imported_names:
            assert imported in _ALLOWED_IMPORTS, (
                f"{_MAPPINGS_PATH} imports disallowed module {imported!r}"
            )


def test_mapping_module_has_no_import_time_io_or_resource_calls() -> None:
    tree = ast.parse(_MAPPINGS_PATH.read_text(encoding="utf-8"))
    calls, decorators = _import_time_effects(tree)
    assert calls == []
    assert decorators == []


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


def _import_time_effects(
    tree: ast.Module,
) -> tuple[list[ast.Call], list[tuple[str, str | None, bool]]]:
    """Collect calls/decorator applications executed while importing a module."""

    calls: list[ast.Call] = []
    decorators: list[tuple[str, str | None, bool]] = []

    def visit_decorator(node: ast.AST, scope: str) -> None:
        if isinstance(node, ast.Call):
            decorators.append((scope, _dotted_name(node.func), True))
        else:
            decorators.append((scope, _dotted_name(node), False))
        visit(node)

    def visit(node: ast.AST, *, class_name: str | None = None) -> None:
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
            visit(child, class_name=class_name)

    visit(tree)
    return calls, decorators


def test_import_guard_rejects_aliased_infrastructure_and_definition_calls() -> None:
    probe = ast.parse(
        """
import ai_ecommerce_agent.modules.durable_dispatch.infrastructure.tables as hidden

@print
def leaked(default=uuid4()):
    pass
"""
    )

    with pytest.raises(AssertionError, match="disallowed module"):
        _assert_allowed_imports(probe)
    calls, decorators = _import_time_effects(probe)
    assert [_dotted_name(call.func) for call in calls] == ["uuid4"]
    assert decorators == [("function:leaked", "print", False)]
    with pytest.raises(AssertionError, match="import-time"):
        _assert_no_import_time_effects(probe)


def _assert_no_import_time_effects(tree: ast.Module) -> None:
    calls, decorators = _import_time_effects(tree)
    if calls or decorators:
        raise AssertionError(
            f"import-time effects found: calls={calls!r}, decorators={decorators!r}"
        )
