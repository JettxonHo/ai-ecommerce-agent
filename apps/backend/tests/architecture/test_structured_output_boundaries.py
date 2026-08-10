"""Architecture and dependency boundaries for Structured Output validation."""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_ROOT = (
    _BACKEND_ROOT / "src" / "ai_ecommerce_agent" / "application" / "structured_output"
)
_PRODUCTION_FILES = (_PACKAGE_ROOT / "__init__.py", _PACKAGE_ROOT / "validation.py")
_ALLOWED_STDLIB = {"__future__", "collections", "json", "typing"}
_ALLOWED_EXTERNAL = {"jsonschema", "referencing"}
_ALLOWED_ABSOLUTE = {
    "ai_ecommerce_agent.application.model_runtime",
    "ai_ecommerce_agent.shared_kernel.structured_content",
}
_ALLOWED_RELATIVE = {".", ".validation"}
_FORBIDDEN_ROOTS = {
    "openai",
    "anthropic",
    "langgraph",
    "sqlalchemy",
    "psycopg",
    "fastapi",
    "starlette",
    "socket",
    "subprocess",
    "pathlib",
    "os",
    "httpx",
    "requests",
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _imports(tree: ast.Module) -> list[tuple[str, str, str | None]]:
    imports: list[tuple[str, str, str | None]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                (alias.name, alias.name, alias.asname) for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            imports.extend((module, alias.name, alias.asname) for alias in node.names)
    return imports


def _import_time_effects(tree: ast.Module) -> tuple[list[ast.Call], list[ast.expr]]:
    calls: list[ast.Call] = []
    bare_decorators: list[ast.expr] = []

    def expression(node: ast.AST) -> None:
        calls.extend(
            candidate for candidate in ast.walk(node) if isinstance(candidate, ast.Call)
        )

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    bare_decorators.append(decorator)
                expression(decorator)
            for argument in (
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            ):
                if argument.annotation is not None:
                    expression(argument.annotation)
            if node.args.vararg and node.args.vararg.annotation is not None:
                expression(node.args.vararg.annotation)
            if node.args.kwarg and node.args.kwarg.annotation is not None:
                expression(node.args.kwarg.annotation)
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    expression(default)
            if node.returns is not None:
                expression(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    bare_decorators.append(decorator)
                expression(decorator)
            for base in node.bases:
                expression(base)
            for keyword in node.keywords:
                expression(keyword.value)
            for child in node.body:
                statement(child)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            expression(node.iter)
            expression(node.target)
            for child in (*node.body, *node.orelse):
                statement(child)
            return
        if isinstance(node, ast.If | ast.While):
            expression(node.test)
            for child in (*node.body, *node.orelse):
                statement(child)
            return
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                expression(item.context_expr)
                if item.optional_vars is not None:
                    expression(item.optional_vars)
            for child in node.body:
                statement(child)
            return
        if isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                statement(child)
            for handler in node.handlers:
                if handler.type is not None:
                    expression(handler.type)
                for child in handler.body:
                    statement(child)
            return
        expression(node)

    for node in tree.body:
        statement(node)
    return calls, bare_decorators


def _module_assignments(tree: ast.Module) -> list[str]:
    names: list[str] = []

    def target_names(node: ast.AST) -> None:
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for element in node.elts:
                target_names(element)

    def statements(nodes: list[ast.stmt]) -> None:
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    target_names(target)
            elif isinstance(node, ast.AnnAssign):
                target_names(node.target)
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                target_names(node.target)
                statements([*node.body, *node.orelse])
            elif isinstance(node, (ast.If, ast.While)):
                statements([*node.body, *node.orelse])
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars is not None:
                        target_names(item.optional_vars)
                statements(node.body)
            elif isinstance(node, ast.Try):
                statements([*node.body, *node.orelse, *node.finalbody])
                for handler in node.handlers:
                    statements(handler.body)

    statements(tree.body)
    return names


def _module_assignment_values(tree: ast.Module) -> dict[str, ast.expr]:
    values: dict[str, ast.expr] = {}

    def target_names(node: ast.AST) -> list[str]:
        if isinstance(node, ast.Name):
            return [node.id]
        if isinstance(node, (ast.Tuple, ast.List)):
            names: list[str] = []
            for element in node.elts:
                names.extend(target_names(element))
            return names
        return []

    def statements(nodes: list[ast.stmt]) -> None:
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    for name in target_names(target):
                        values[name] = node.value
            elif isinstance(node, ast.AnnAssign):
                if node.value is not None:
                    for name in target_names(node.target):
                        values[name] = node.value
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                for name in target_names(node.target):
                    values[name] = node.iter
                statements([*node.body, *node.orelse])
            elif isinstance(node, (ast.If, ast.While)):
                statements([*node.body, *node.orelse])
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars is not None:
                        for name in target_names(item.optional_vars):
                            values[name] = item.context_expr
                statements(node.body)
            elif isinstance(node, ast.Try):
                statements([*node.body, *node.orelse, *node.finalbody])
                for handler in node.handlers:
                    statements(handler.body)

    statements(tree.body)
    return values


def _immutable_literal(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.Tuple):
        return all(_immutable_literal(element) for element in node.elts)
    return False


def test_exact_two_file_inventory_and_narrow_imports() -> None:
    assert all(path.is_file() for path in _PRODUCTION_FILES)
    assert sorted(path.name for path in _PACKAGE_ROOT.glob("*.py")) == [
        "__init__.py",
        "validation.py",
    ]
    for path in _PRODUCTION_FILES:
        for module, imported, _alias in _imports(_tree(path)):
            root = module.lstrip(".").split(".", 1)[0]
            if module == "." and imported != "validation":
                pytest.fail(f"unexpected package import {imported!r}")
            if (
                module == ".validation"
                and imported != "parse_and_validate_structured_output"
            ):
                pytest.fail(f"unexpected validation import {imported!r}")
            assert (
                module in _ALLOWED_ABSOLUTE
                or module in _ALLOWED_RELATIVE
                or root in _ALLOWED_STDLIB
                or root in _ALLOWED_EXTERNAL
            ), f"unexpected import {module!r} in {path.name}"
            assert root not in _FORBIDDEN_ROOTS


def test_import_time_effects_and_mutable_globals_are_absent() -> None:
    for path in _PRODUCTION_FILES:
        tree = _tree(path)
        calls, bare_decorators = _import_time_effects(tree)
        assert calls == []
        assert bare_decorators == []
        values = _module_assignment_values(tree)
        assert set(values) <= {
            "__all__",
            "_SCHEMA_IDENTITY_MESSAGE",
            "_PROJECT_SCHEMA_MESSAGE",
            "_CANDIDATE_JSON_MESSAGE",
            "_CANDIDATE_OBJECT_MESSAGE",
            "_CANDIDATE_SCHEMA_MESSAGE",
            "_OBJECT_KEYWORDS",
        }
        assert all(
            _immutable_literal(value)
            for name, value in values.items()
            if name != "__all__"
        )
        if "__all__" in values:
            assert isinstance(values["__all__"], ast.List)


def test_valid_baseline_and_single_import_time_mutations_are_distinguishable() -> None:
    baseline = ast.parse(
        """\
__all__ = ['parse_and_validate_structured_output']
def parse_and_validate_structured_output(*, result, spec):
    return result
"""
    )
    calls, bare_decorators = _import_time_effects(baseline)
    assert calls == []
    assert bare_decorators == []
    assert _module_assignments(baseline) == ["__all__"]
    probes = (
        "__all__ = ['x']\nopen('x')\n",
        "__all__ = ['x']\n@print\ndef parse(*, result, spec):\n    return result\n",
        "__all__ = ['x']\ndef parse(*, result=open('x'), spec):\n    return result\n",
        "__all__ = ['x']\ndef parse(*, result: open('x'), spec):\n    return result\n",
        "__all__ = ['x']\ndef parse(*, result, spec) -> open('x'):\n"
        "    return result\n",
        "__all__ = ['x']\n_CACHE = []\n",
    )
    for source in probes:
        tree = ast.parse(source)
        calls, bare_decorators = _import_time_effects(tree)
        assert calls or bare_decorators or _module_assignments(tree) != ["__all__"]


def test_dependencies_are_exact_and_no_second_schema_engine_is_declared() -> None:
    pyproject = tomllib.loads(
        (_BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    dependencies = pyproject["project"]["dependencies"]
    assert "jsonschema==4.26.0" in dependencies
    assert "referencing==0.37.0" in dependencies
    assert not any(
        any(
            token in dependency.lower()
            for token in ("pydantic", "fastjsonschema", "marshmallow")
        )
        for dependency in dependencies
    )
