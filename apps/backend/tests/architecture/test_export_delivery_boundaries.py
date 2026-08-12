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
_BOUNDED_EXPORT_CONSUMER = _SRC / "bootstrap/review_export_postgres.py"
_PRODUCTION_FILES = (_APPLICATION / "__init__.py", _RENDERER)
_RENDERER_ALLOWED_IMPORTS = {
    "__future__",
    "json",
    "re",
    "datetime",
    "enum",
    "itertools",
    "typing",
    "ai_ecommerce_agent.modules.export_delivery.public",
    "ai_ecommerce_agent.modules.marketing_brief.public",
    "ai_ecommerce_agent.modules.task_management.public",
    "ai_ecommerce_agent.modules.xiaohongshu_adapter.public",
    "ai_ecommerce_agent.shared_kernel",
}


def _import_time_effects(tree: ast.Module) -> tuple[list[ast.Call], list[ast.AST]]:
    calls: list[ast.Call] = []
    mutable: list[ast.AST] = []

    def scan_expression(node: ast.AST | None) -> None:
        if node is None:
            return
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                calls.append(child)

    class Scanner(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._scan_function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._scan_function(node)

        def _scan_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            for expression in (
                *node.decorator_list,
                *node.args.defaults,
                *node.args.kw_defaults,
                node.returns,
                *(argument.annotation for argument in node.args.posonlyargs),
                *(argument.annotation for argument in node.args.args),
                *(argument.annotation for argument in node.args.kwonlyargs),
                node.args.vararg.annotation if node.args.vararg else None,
                node.args.kwarg.annotation if node.args.kwarg else None,
            ):
                scan_expression(expression)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            for expression in (*node.decorator_list, *node.bases):
                scan_expression(expression)
            for keyword in node.keywords:
                scan_expression(keyword.value)
            for statement in node.body:
                self.visit(statement)

        def visit_Assign(self, node: ast.Assign) -> None:
            scan_expression(node.value)
            if isinstance(
                node.value,
                (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp),
            ):
                mutable.append(node)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            scan_expression(node.annotation)
            scan_expression(node.value)
            if isinstance(
                node.value,
                (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp),
            ):
                mutable.append(node)

        def visit_Expr(self, node: ast.Expr) -> None:
            scan_expression(node.value)

        def visit_If(self, node: ast.If) -> None:
            scan_expression(node.test)
            for statement in (*node.body, *node.orelse):
                self.visit(statement)

        def visit_For(self, node: ast.For) -> None:
            scan_expression(node.iter)
            for statement in (*node.body, *node.orelse):
                self.visit(statement)

        def visit_While(self, node: ast.While) -> None:
            scan_expression(node.test)
            for statement in (*node.body, *node.orelse):
                self.visit(statement)

        def visit_With(self, node: ast.With) -> None:
            for item in node.items:
                scan_expression(item.context_expr)
            for statement in node.body:
                self.visit(statement)

        def visit_Try(self, node: ast.Try) -> None:
            for statement in (
                *node.body,
                *node.orelse,
                *node.finalbody,
                *(statement for handler in node.handlers for statement in handler.body),
            ):
                self.visit(statement)

        def visit_Match(self, node: ast.Match) -> None:
            scan_expression(node.subject)
            for case in node.cases:
                scan_expression(case.guard)
                for statement in case.body:
                    self.visit(statement)

    scanner = Scanner()
    for statement in tree.body:
        scanner.visit(statement)
    return calls, mutable


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
    assert {path.name for path in _APPLICATION.iterdir() if path.is_file()} == {
        "__init__.py",
        "markdown_renderer.py",
    }
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
    # FL-1C owns one narrow PostgreSQL adapter that consumes the existing
    # renderer; no other adapter may become a renderer consumer.
    assert consumers == [_BOUNDED_EXPORT_CONSUMER]


def test_renderer_has_no_import_time_effects_or_global_mutable_state() -> None:
    tree = ast.parse(_RENDERER.read_text(encoding="utf-8"))
    calls, mutable = _import_time_effects(tree)
    assert calls == []
    assert mutable == []


def test_renderer_architecture_probes_reject_effectful_mutations() -> None:
    baseline = ast.parse(
        "from datetime import UTC\n"
        "def render(*, value: str) -> str:\n"
        "    return value\n"
    )
    assert not [node for node in ast.walk(baseline) if isinstance(node, ast.Call)]
    baseline_source = (
        "from __future__ import annotations\n"
        "import json\n"
        "def render(*, value: str = 'ok') -> str:\n"
        "    return value\n"
    )
    assert _import_time_effects(ast.parse(baseline_source)) == ([], [])
    for source in (
        baseline_source + "if print('x'):\n    pass\n",
        baseline_source + "for _ in range(print('x')):\n    pass\n",
        baseline_source + "while print('x'):\n    break\n",
        baseline_source + "with print('x'):\n    pass\n",
        baseline_source + "try:\n    print('x')\nexcept Exception:\n    pass\n",
        baseline_source + "match 1:\n    case _ if print('x'):\n        pass\n",
        baseline_source + "_cache = []\n",
    ):
        calls, mutable = _import_time_effects(ast.parse(source))
        assert calls or mutable


def test_renderer_import_time_guard_covers_class_bodies_and_annotations() -> None:
    baseline_source = (
        "from __future__ import annotations\n"
        "class Render:\n"
        "    value: str\n"
        "    def render(self, value: str = 'ok') -> str:\n"
        "        return value\n"
        "def render(*, value: str = 'ok') -> str:\n"
        "    return value\n"
    )
    baseline = ast.parse(baseline_source)
    assert _import_time_effects(baseline) == ([], [])
    for source in (
        baseline_source.replace("    value: str\n", "    token = print('x')\n"),
        baseline_source.replace("value: str = 'ok'", "value: str = print('x')"),
        baseline_source.replace("value: str\n", "value: factory()\n"),
    ):
        calls, _ = _import_time_effects(ast.parse(source))
        assert calls
