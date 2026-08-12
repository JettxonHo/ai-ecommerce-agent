"""Architecture locks for the framework-neutral Export Delivery contracts."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ai_ecommerce_agent.modules.export_delivery.domain.contracts as contracts
import ai_ecommerce_agent.modules.export_delivery.public as public

pytestmark = pytest.mark.architecture

_FORBIDDEN_IMPORTS = (
    "sqlalchemy",
    "langgraph",
    "fastapi",
    "starlette",
    "openai",
    "anthropic",
)
_FORBIDDEN_TOP_LEVEL_CALLS = {
    "connect",
    "create_engine",
    "getenv",
    "open",
    "read_text",
    "write_text",
}

_BACKEND = Path(__file__).resolve().parents[2]
_SRC = _BACKEND / "src/ai_ecommerce_agent"
_APPLICATION = _SRC / "modules/export_delivery/application"
_RENDERER = _APPLICATION / "markdown_renderer.py"
_PRODUCTION_FILES = (_APPLICATION / "__init__.py", _RENDERER)
_RENDERER_ALLOWED_IMPORTS = {
    "__future__",
    "json",
    "datetime",
    "enum",
    "typing",
    "ai_ecommerce_agent.modules.export_delivery.public",
    "ai_ecommerce_agent.modules.marketing_brief.public",
    "ai_ecommerce_agent.modules.task_management.public",
    "ai_ecommerce_agent.modules.xiaohongshu_adapter.public",
    "ai_ecommerce_agent.shared_kernel",
}


def _module_tree(module: object) -> ast.Module:
    module_file = Path(module.__file__)  # type: ignore[attr-defined]
    return ast.parse(module_file.read_text(encoding="utf-8"))


def test_export_contract_modules_are_framework_neutral() -> None:
    for module in (contracts, public):
        tree = _module_tree(module)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        assert not any(
            imported == forbidden or imported.startswith(f"{forbidden}.")
            for imported in imports
            for forbidden in _FORBIDDEN_IMPORTS
        )


def test_export_contract_imports_have_no_io_or_resource_construction() -> None:
    for module in (contracts, public):
        tree = _module_tree(module)
        module_body = tree.body
        top_level_calls = {
            node.func.attr
            for statement in module_body
            for node in ast.walk(statement)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        top_level_calls.update(
            node.func.id
            for statement in module_body
            for node in ast.walk(statement)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        )
        assert top_level_calls.isdisjoint(_FORBIDDEN_TOP_LEVEL_CALLS)


def test_export_contract_uses_only_the_task_public_facade_for_versions() -> None:
    tree = _module_tree(contracts)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "ai_ecommerce_agent.modules.task_management.public" in imports
    assert not any(
        module is not None
        and module.startswith("ai_ecommerce_agent.modules.task_management.")
        and module != "ai_ecommerce_agent.modules.task_management.public"
        for module in imports
    )


def test_renderer_inventory_imports_and_private_ownership_are_exact() -> None:
    assert all(path.is_file() for path in _PRODUCTION_FILES)
    tree = ast.parse(_RENDERER.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add("." * node.level + (node.module or ""))
    assert imports <= _RENDERER_ALLOWED_IMPORTS
    application = __import__(
        "ai_ecommerce_agent.modules.export_delivery.application", fromlist=["x"]
    )
    assert not hasattr(application, "render_export_markdown")
    consumers: list[Path] = []
    for path in _SRC.rglob("*.py"):
        if path == _RENDERER:
            continue
        source = path.read_text(encoding="utf-8")
        if "markdown_renderer" in source or "render_export_markdown" in source:
            consumers.append(path)
    assert consumers == []


def test_renderer_has_no_import_time_effects_or_global_mutable_state() -> None:
    tree = ast.parse(_RENDERER.read_text(encoding="utf-8"))
    calls: list[ast.Call] = []
    mutable: list[ast.AST] = []

    def inspect_statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in getattr(node, "decorator_list", []):
                calls.extend(
                    child
                    for child in ast.walk(decorator)
                    if isinstance(child, ast.Call)
                )
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for expression in (
                    *node.args.defaults,
                    *node.args.kw_defaults,
                    node.returns,
                ):
                    if expression is not None:
                        calls.extend(
                            child
                            for child in ast.walk(expression)
                            if isinstance(child, ast.Call)
                        )
            return
        calls.extend(child for child in ast.walk(node) if isinstance(child, ast.Call))
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(
                value,
                (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp),
            ):
                mutable.append(node)

    for statement in tree.body:
        inspect_statement(statement)
    assert calls == []
    assert mutable == []


def test_renderer_architecture_probes_reject_effectful_mutations() -> None:
    baseline = ast.parse(
        "from datetime import UTC\n"
        "def render(*, value: str) -> str:\n"
        "    return value\n"
    )
    assert not [node for node in ast.walk(baseline) if isinstance(node, ast.Call)]
    for source in (
        "def render(*, value: str = open('x')) -> str:\n    return value\n",
        "if True:\n    _cache = []\n",
        "import socket\n",
    ):
        mutated = ast.parse(source)
        assert (
            any(isinstance(node, ast.Call) for node in ast.walk(mutated))
            or any(isinstance(node, ast.Import) for node in ast.walk(mutated))
            or any(isinstance(node, ast.List) for node in ast.walk(mutated))
        )
