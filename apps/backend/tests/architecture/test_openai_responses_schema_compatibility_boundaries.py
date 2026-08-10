"""Architecture boundaries for the offline schema compatibility module."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ai_ecommerce_agent import application as application_package

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_PACKAGE = _BACKEND / "src/ai_ecommerce_agent/platform/model_runtime/openai_responses"
_FILES = [
    _PACKAGE / "__init__.py",
    _PACKAGE / "_schema_compatibility.py",
    _PACKAGE / "request_preparation.py",
]
_ALLOWED_STDLIB = {
    "__future__",
    "collections.abc",
    "dataclasses",
    "enum",
    "json",
    "re",
    "typing",
    "urllib.parse",
}
_ALLOWED_ABSOLUTE = {
    "ai_ecommerce_agent.application.model_runtime",
    "ai_ecommerce_agent.shared_kernel",
}
_ALLOWED_RELATIVE: dict[str, set[str]] = {
    "__init__.py": {".request_preparation"},
    "_schema_compatibility.py": set(),
    "request_preparation.py": {"._schema_compatibility"},
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


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _imports(tree: ast.Module) -> list[str]:
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            values.append("." * node.level + (node.module or ""))
    return values


def _import_time_effects(tree: ast.Module) -> tuple[list[ast.Call], list[ast.expr]]:
    calls: list[ast.Call] = []
    bare_decorators: list[ast.expr] = []

    def scan_expression(node: ast.AST) -> None:
        calls.extend(
            candidate for candidate in ast.walk(node) if isinstance(candidate, ast.Call)
        )

    def scan_decorators(nodes: list[ast.expr], class_name: str | None = None) -> None:
        for decorator in nodes:
            allowed_dataclass = (
                class_name
                in {"OpenAIResponsesCallParameters", "PreparedOpenAIResponsesCall"}
                and isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Name)
                and decorator.func.id == "_dataclass"
            )
            if allowed_dataclass:
                calls.extend(
                    candidate
                    for candidate in ast.walk(decorator)
                    if isinstance(candidate, ast.Call) and candidate is not decorator
                )
            elif isinstance(decorator, ast.Call):
                scan_expression(decorator)
            else:
                bare_decorators.append(decorator)

    def scan_arguments(arguments: ast.arguments) -> None:
        for argument in (
            *arguments.posonlyargs,
            *arguments.args,
            *arguments.kwonlyargs,
        ):
            if argument.annotation is not None:
                scan_expression(argument.annotation)
        if arguments.vararg and arguments.vararg.annotation:
            scan_expression(arguments.vararg.annotation)
        if arguments.kwarg and arguments.kwarg.annotation:
            scan_expression(arguments.kwarg.annotation)
        for default in (*arguments.defaults, *arguments.kw_defaults):
            if default is not None:
                scan_expression(default)

    def scan_statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scan_decorators(node.decorator_list)
            scan_arguments(node.args)
            if node.returns is not None:
                scan_expression(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            scan_decorators(node.decorator_list, node.name)
            for base in node.bases:
                scan_expression(base)
            for keyword in node.keywords:
                scan_expression(keyword.value)
            for child in node.body:
                scan_statement(child)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            scan_expression(node.iter)
            scan_expression(node.target)
            for child in (*node.body, *node.orelse):
                scan_statement(child)
            return
        if isinstance(node, ast.While):
            scan_expression(node.test)
            for child in (*node.body, *node.orelse):
                scan_statement(child)
            return
        if isinstance(node, ast.If):
            scan_expression(node.test)
            for child in (*node.body, *node.orelse):
                scan_statement(child)
            return
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                scan_expression(item.context_expr)
                if item.optional_vars is not None:
                    scan_expression(item.optional_vars)
            for child in node.body:
                scan_statement(child)
            return
        if isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                scan_statement(child)
            for handler in node.handlers:
                if handler.type is not None:
                    scan_expression(handler.type)
                for child in handler.body:
                    scan_statement(child)
            return
        scan_expression(node)

    for statement in tree.body:
        scan_statement(statement)
    return calls, bare_decorators


def _module_assignments(tree: ast.Module) -> list[str]:
    names: list[str] = []

    def target_names(target: ast.AST) -> list[str]:
        if isinstance(target, ast.Name):
            return [target.id]
        if isinstance(target, (ast.Tuple, ast.List)):
            return [name for item in target.elts for name in target_names(item)]
        return []

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                names.extend(target_names(target))
        elif isinstance(node, ast.AnnAssign):
            names.extend(target_names(node.target))
    return names


def _mutable_module_assignments(tree: ast.Module) -> list[str]:
    names: list[str] = []

    def target_name(target: ast.AST) -> str | None:
        return target.id if isinstance(target, ast.Name) else None

    def value_is_mutable(value: ast.AST) -> bool:
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

    def visit_expression(expression: ast.AST) -> None:
        for candidate in ast.walk(expression):
            if isinstance(candidate, ast.NamedExpr) and value_is_mutable(
                candidate.value
            ):
                target = target_name(candidate.target)
                if target is not None and target != "__all__":
                    names.append(target)

    def visit(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if isinstance(node, ast.Assign):
            if value_is_mutable(node.value):
                names.extend(
                    target
                    for target in (target_name(item) for item in node.targets)
                    if target is not None and target != "__all__"
                )
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if value_is_mutable(node.value):
                target = target_name(node.target)
                if target is not None and target != "__all__":
                    names.append(target)
        elif isinstance(node, ast.NamedExpr):
            value = node.value
            if value is not None and value_is_mutable(value):
                target = target_name(node.target)
                if target is not None and target != "__all__":
                    names.append(target)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            visit_expression(node.iter)
            visit_expression(node.target)
            for child in (*node.body, *node.orelse):
                visit(child)
        elif isinstance(node, (ast.While, ast.If)):
            visit_expression(node.test)
            for child in (*node.body, *node.orelse):
                visit(child)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                visit_expression(item.context_expr)
                if item.optional_vars is not None:
                    visit_expression(item.optional_vars)
            for child in node.body:
                visit(child)
        elif isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                visit(child)
            for handler in node.handlers:
                for child in handler.body:
                    visit(child)

    for statement in tree.body:
        visit(statement)
    return names


def test_exact_inventory_imports_and_private_facade() -> None:
    assert sorted(path.name for path in _PACKAGE.glob("*.py")) == [
        "__init__.py",
        "_schema_compatibility.py",
        "request_preparation.py",
    ]
    for path in _FILES:
        for module in _imports(_tree(path)):
            if module in _ALLOWED_STDLIB or module in _ALLOWED_ABSOLUTE:
                continue
            if module in _ALLOWED_RELATIVE[path.name]:
                continue
            if module.startswith(_FORBIDDEN) or module.startswith("ai_ecommerce_agent"):
                pytest.fail(f"forbidden import in {path.name}: {module}")
            pytest.fail(f"unexpected import in {path.name}: {module}")
    assert _module_assignments(_tree(_FILES[0])) == ["__all__"]
    assert ast.literal_eval(_tree(_FILES[0]).body[-1].value) == [  # type: ignore[union-attr]
        "OpenAIReasoningEffort",
        "OpenAIResponsesCallParameters",
        "PreparedOpenAIResponsesCall",
        "prepare_openai_responses_call",
    ]
    assert not hasattr(application_package, "ensure_openai_responses_schema_compatible")


def test_request_preparation_is_the_only_private_schema_consumer() -> None:
    preparation_imports = _imports(_tree(_PACKAGE / "request_preparation.py"))
    schema_imports = _imports(_tree(_PACKAGE / "_schema_compatibility.py"))
    assert "._schema_compatibility" in preparation_imports
    assert all("request_preparation" not in module for module in schema_imports)


def test_no_import_time_calls_or_mutable_globals() -> None:
    for path in _FILES:
        calls, bare_decorators = _import_time_effects(_tree(path))
        assert calls == []
        assert bare_decorators == []
        assert _mutable_module_assignments(_tree(path)) == []


@pytest.mark.parametrize(
    "mutation",
    [
        "_CACHE = []",
        "if True:\n    _CACHE = []",
        "for _item in []:\n    _CACHE = []",
        "if (_CACHE := []):\n    pass",
        "class Bad:\n    value = open('x')",
        "@print\ndef leaked():\n    pass",
    ],
)
def test_import_time_and_mutable_global_probes_are_detectable(mutation: str) -> None:
    baseline = """\
from __future__ import annotations
class Good:
    value: str
\n__all__ = []
"""
    baseline_tree = ast.parse(baseline)
    baseline_calls, baseline_decorators = _import_time_effects(baseline_tree)
    assert baseline_calls == []
    assert baseline_decorators == []
    assert _mutable_module_assignments(baseline_tree) == []
    mutated = ast.parse(baseline + "\n" + mutation)
    calls, bare_decorators = _import_time_effects(mutated)
    assert calls or bare_decorators or _mutable_module_assignments(mutated)
