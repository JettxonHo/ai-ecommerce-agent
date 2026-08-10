"""Architecture boundaries for the OpenAI Responses request projection."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_PACKAGE = _BACKEND / "src/ai_ecommerce_agent/platform/model_runtime/openai_responses"
_FILES = [_PACKAGE / "__init__.py", _PACKAGE / "request_preparation.py"]
_ALLOWED_STDLIB = {"__future__", "dataclasses", "enum", "json", "typing"}
_ALLOWED_ABSOLUTE = {
    "ai_ecommerce_agent.application.model_runtime",
    "ai_ecommerce_agent.shared_kernel",
}
_ALLOWED_RELATIVE = {
    "__init__.py": {"request_preparation"},
    "request_preparation.py": {"_schema_compatibility"},
}
_FORBIDDEN = (
    "openai",
    "httpx",
    "requests",
    "socket",
    "os",
    "pathlib",
    "subprocess",
    "sqlalchemy",
    "psycopg",
    "langgraph",
    "fastapi",
    "starlette",
)
_DATACLASS_CLASSES = {
    "OpenAIResponsesCallParameters",
    "PreparedOpenAIResponsesCall",
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _imports(tree: ast.Module) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.extend(("absolute", alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                values.append(("relative", node.module or ""))
            else:
                values.append(("absolute", node.module or ""))
    return values


def _import_time_violations(tree: ast.Module) -> list[ast.AST]:
    violations: list[ast.AST] = []

    def expression(node: ast.AST) -> None:
        violations.extend(
            candidate for candidate in ast.walk(node) if isinstance(candidate, ast.Call)
        )

    def decorators(nodes: list[ast.expr], class_name: str | None = None) -> None:
        for decorator in nodes:
            allowed = (
                class_name in _DATACLASS_CLASSES
                and isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "_dataclass"
            )
            if allowed:
                nested = [
                    candidate
                    for candidate in ast.walk(decorator)
                    if isinstance(candidate, ast.Call) and candidate is not decorator
                ]
                violations.extend(nested)
            elif isinstance(decorator, ast.Call):
                expression(decorator)
            else:
                violations.append(decorator)

    def arguments(node: ast.arguments) -> None:
        for argument in (
            *node.posonlyargs,
            *node.args,
            *node.kwonlyargs,
        ):
            if argument.annotation is not None:
                expression(argument.annotation)
        if node.vararg and node.vararg.annotation:
            expression(node.vararg.annotation)
        if node.kwarg and node.kwarg.annotation:
            expression(node.kwarg.annotation)
        for default in (*node.defaults, *node.kw_defaults):
            if default is not None:
                expression(default)

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators(node.decorator_list)
            arguments(node.args)
            if node.returns is not None:
                expression(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            decorators(node.decorator_list, node.name)
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
        if isinstance(node, ast.While):
            expression(node.test)
            for child in (*node.body, *node.orelse):
                statement(child)
            return
        if isinstance(node, ast.If):
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
    return violations


def _mutable_module_globals(tree: ast.Module) -> list[str]:
    names: list[str] = []

    def target_name(node: ast.AST) -> str | None:
        return node.id if isinstance(node, ast.Name) else None

    def mutable(value: ast.AST) -> bool:
        return isinstance(
            value,
            (
                ast.Call,
                ast.Dict,
                ast.DictComp,
                ast.List,
                ast.ListComp,
                ast.NamedExpr,
                ast.Set,
                ast.SetComp,
            ),
        )

    def expression(node: ast.AST) -> None:
        for candidate in ast.walk(node):
            if isinstance(candidate, ast.NamedExpr) and mutable(candidate.value):
                name = target_name(candidate.target)
                if name is not None and name != "__all__":
                    names.append(name)

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if isinstance(node, ast.Assign):
            if mutable(node.value):
                for target in node.targets:
                    name = target_name(target)
                    if name is not None and name != "__all__":
                        names.append(name)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if mutable(node.value):
                name = target_name(node.target)
                if name is not None and name != "__all__":
                    names.append(name)
        elif isinstance(node, ast.NamedExpr):
            name = target_name(node.target)
            if (
                node.value is not None
                and mutable(node.value)
                and name is not None
                and name != "__all__"
            ):
                names.append(name)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            expression(node.iter)
            expression(node.target)
            for child in (*node.body, *node.orelse):
                statement(child)
        elif isinstance(node, (ast.While, ast.If)):
            expression(node.test)
            for child in (*node.body, *node.orelse):
                statement(child)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                expression(item.context_expr)
                if item.optional_vars is not None:
                    expression(item.optional_vars)
            for child in node.body:
                statement(child)
        elif isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                statement(child)
            for handler in node.handlers:
                for child in handler.body:
                    statement(child)

    for node in tree.body:
        statement(node)
    return names


def test_inventory_import_direction_and_private_schema_consumer() -> None:
    assert sorted(path.name for path in _PACKAGE.glob("*.py")) == [
        "__init__.py",
        "_schema_compatibility.py",
        "request_preparation.py",
    ]
    for path in _FILES:
        for kind, module in _imports(_tree(path)):
            if kind == "absolute" and (
                module in _ALLOWED_STDLIB or module in _ALLOWED_ABSOLUTE
            ):
                continue
            if kind == "relative" and module in _ALLOWED_RELATIVE[path.name]:
                continue
            if module.startswith(_FORBIDDEN) or module.startswith("ai_ecommerce_agent"):
                pytest.fail(f"forbidden import in {path.name}: {kind} {module}")
            pytest.fail(f"unexpected import in {path.name}: {kind} {module}")

    preparation_imports = _imports(_tree(_PACKAGE / "request_preparation.py"))
    assert ("relative", "_schema_compatibility") in preparation_imports
    schema_imports = _imports(_tree(_PACKAGE / "_schema_compatibility.py"))
    assert not any(module == "request_preparation" for _, module in schema_imports)


def test_import_time_effects_and_mutable_globals_are_absent() -> None:
    for path in _FILES:
        tree = _tree(path)
        assert _import_time_violations(tree) == []
        assert _mutable_module_globals(tree) == []


@pytest.mark.parametrize(
    "mutation",
    [
        "class Bad:\n    value = open('x')",
        "@print\ndef leaked():\n    pass",
        "def leaked(value=open('x')):\n    pass",
        "def leaked(value: open('x')):\n    pass",
        "def leaked() -> open('x'):\n    pass",
        "class Bad(_factory()):\n    pass",
        "_CACHE = []",
        "if (_CACHE := []):\n    pass",
    ],
)
def test_import_time_probes_use_one_mutation_against_production_shaped_baseline(
    mutation: str,
) -> None:
    baseline = """\
from dataclasses import dataclass as _dataclass
@_dataclass(frozen=True, slots=True)
class OpenAIResponsesCallParameters:
    value: str
@_dataclass(frozen=True, slots=True)
class PreparedOpenAIResponsesCall:
    value: str
__all__ = ["OpenAIResponsesCallParameters", "PreparedOpenAIResponsesCall"]
"""
    baseline_tree = ast.parse(baseline)
    assert _import_time_violations(baseline_tree) == []
    assert _mutable_module_globals(baseline_tree) == []
    mutated = ast.parse(baseline + "\n" + mutation)
    assert _import_time_violations(mutated) or _mutable_module_globals(mutated)
