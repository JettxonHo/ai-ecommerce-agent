"""Architecture boundaries for the provider-neutral model runtime port."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _BACKEND_ROOT / "src" / "ai_ecommerce_agent"
_PRODUCTION_FILE = _SRC_ROOT / "application" / "model_runtime.py"
_ALLOWED_STDLIB = {"__future__", "dataclasses", "enum", "typing"}
_ALLOWED_ABSOLUTE = {"ai_ecommerce_agent.shared_kernel.structured_content"}
_FORBIDDEN_PREFIXES = (
    "openai",
    "anthropic",
    "langgraph",
    "sqlalchemy",
    "psycopg",
    "fastapi",
    "starlette",
    "os",
    "pathlib",
    "socket",
    "subprocess",
    "dotenv",
)
_DATACLASS_CLASSES = {
    "ModelCallId",
    "ProviderAttemptId",
    "ModelCallIdentity",
    "ModelExecutionProfile",
    "StructuredOutputSpec",
    "ModelCallContractVersions",
    "ModelCallRequest",
    "ModelRuntimeVersionTuple",
    "ModelTokenUsage",
    "ProviderCallMetadata",
    "ModelOutputEnvelope",
    "ModelCallResult",
    "ModelRuntimeError",
}


def _tree() -> ast.Module:
    return ast.parse(_PRODUCTION_FILE.read_text(encoding="utf-8"))


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


def _import_names(tree: ast.Module) -> list[tuple[str, str, str | None]]:
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


def _expression_calls(node: ast.AST) -> list[ast.Call]:
    return [
        candidate for candidate in ast.walk(node) if isinstance(candidate, ast.Call)
    ]


def _import_time_effects(
    tree: ast.Module,
) -> tuple[list[ast.Call], list[tuple[str, str | None, bool]]]:
    """Inspect import-time module/class expressions, skipping function bodies."""

    calls: list[ast.Call] = []
    decorators: list[tuple[str, str | None, bool]] = []

    def scan_expression(node: ast.AST) -> None:
        calls.extend(_expression_calls(node))

    def scan_decorators(nodes: list[ast.expr], scope: str) -> None:
        for decorator in nodes:
            if isinstance(decorator, ast.Call):
                decorators.append((scope, _dotted_name(decorator.func), True))
                scan_expression(decorator)
            else:
                decorators.append((scope, _dotted_name(decorator), False))
                scan_expression(decorator)

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

    def scan_statement(node: ast.stmt, scope: str) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scan_decorators(node.decorator_list, f"{scope}.{node.name}")
            scan_arguments(node.args)
            if node.returns is not None:
                scan_expression(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            scan_decorators(node.decorator_list, f"{scope}.{node.name}")
            for base in node.bases:
                scan_expression(base)
            for keyword in node.keywords:
                scan_expression(keyword.value)
            for child in node.body:
                scan_statement(child, f"{scope}.{node.name}")
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            return
        if isinstance(
            node,
            (
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.If,
                ast.Try,
                ast.With,
                ast.AsyncWith,
            ),
        ):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.stmt):
                    scan_statement(child, scope)
            return
        calls.extend(_expression_calls(node))

    for statement in tree.body:
        scan_statement(statement, "module")
    return calls, decorators


def _allowed_dataclass_decorator(scope: str, target: str | None, is_call: bool) -> bool:
    class_name = scope.removeprefix("module.")
    return (
        is_call
        and target == "_dataclass"
        and scope.startswith("module.")
        and scope.count(".") == 1
        and class_name in _DATACLASS_CLASSES
    )


def _allowed_import(module: str) -> bool:
    return (
        module == "__future__"
        or module in _ALLOWED_STDLIB
        or module in _ALLOWED_ABSOLUTE
    )


def test_production_inventory_and_imports_are_narrow() -> None:
    assert _PRODUCTION_FILE.is_file()
    assert sorted(path.name for path in _PRODUCTION_FILE.parent.glob("*.py")) == [
        "__init__.py",
        "errors.py",
        "model_runtime.py",
        "ports.py",
    ]
    imports = _import_names(_tree())
    for module, imported, alias in imports:
        del imported, alias
        if module.startswith("."):
            pytest.fail(f"relative import is not allowed: {module}")
        if _allowed_import(module):
            continue
        if module.startswith(_FORBIDDEN_PREFIXES) or module.startswith(
            "ai_ecommerce_agent"
        ):
            pytest.fail(f"technical or business import is not allowed: {module}")
        pytest.fail(f"unexpected import: {module}")


def test_import_time_effect_guard_allows_only_exact_dataclass_decorators() -> None:
    calls, decorators = _import_time_effects(_tree())
    assert all(
        _allowed_dataclass_decorator(scope, target, True)
        for scope, target, is_call in decorators
        if is_call
    )
    assert all(
        not is_call
        and target == "_runtime_checkable"
        and scope == "module.ModelRuntimePort"
        for scope, target, is_call in decorators
        if not is_call
    )
    assert len(calls) == sum(
        1
        for scope, target, is_call in decorators
        if _allowed_dataclass_decorator(scope, target, is_call)
    )


def test_import_time_effect_guard_rejects_synthetic_effects() -> None:
    probes = (
        "@print\ndef leaked(value=open('x')):\n    return value\n",
        "class Leaked:\n    token = uuid4()\n",
        "@_runtime_checkable()\nclass Leaked: pass\n",
        "def leaked(value: getenv('X')) -> open('x'):\n    return value\n",
    )
    for source in probes:
        calls, decorators = _import_time_effects(ast.parse(source))
        allowed_calls = sum(
            1
            for scope, target, is_call in decorators
            if _allowed_dataclass_decorator(scope, target, is_call)
        )
        allowed_bare = all(
            not is_call
            and target == "_runtime_checkable"
            and scope == "module.ModelRuntimePort"
            for scope, target, is_call in decorators
            if not is_call
        )
        assert not (allowed_bare and len(calls) == allowed_calls)


def test_import_guard_rejects_forbidden_alias_imports() -> None:
    imports = _import_names(ast.parse("from openai import Client as _Client\n"))
    assert imports == [("openai", "Client", "_Client")]
    assert not _allowed_import(imports[0][0])
