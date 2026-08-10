"""Architecture boundaries for the deterministic scripted model runtime."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_ROOT = (
    _BACKEND_ROOT / "src" / "ai_ecommerce_agent" / "platform" / "model_runtime"
)
_PRODUCTION_FILES = (_PACKAGE_ROOT / "__init__.py", _PACKAGE_ROOT / "scripted.py")
_ALLOWED_STDLIB = {"__future__", "dataclasses"}
_CANONICAL_CONTRACT = "ai_ecommerce_agent.application.model_runtime"
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
_DATACLASS_SCOPES = {
    "module.ScriptedModelStep",
    "module.ScriptedModelScenario",
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


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
    """Inspect module/class expressions, skipping function/method bodies."""

    calls: list[ast.Call] = []
    decorators: list[tuple[str, str | None, bool]] = []

    def scan_expression(node: ast.AST) -> None:
        calls.extend(_expression_calls(node))

    def scan_decorators(nodes: list[ast.expr], scope: str) -> None:
        for decorator in nodes:
            if isinstance(decorator, ast.Call):
                decorators.append((scope, _dotted_name(decorator.func), True))
            else:
                decorators.append((scope, _dotted_name(decorator), False))
            scan_expression(decorator)

    def scan_arguments(arguments: ast.arguments) -> None:
        all_arguments = (
            *arguments.posonlyargs,
            *arguments.args,
            *arguments.kwonlyargs,
        )
        for argument in all_arguments:
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
            class_scope = f"{scope}.{node.name}"
            scan_decorators(node.decorator_list, class_scope)
            for base in node.bases:
                scan_expression(base)
            for keyword in node.keywords:
                scan_expression(keyword.value)
            for child in node.body:
                scan_statement(child, class_scope)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            scan_expression(node.target)
            scan_expression(node.iter)
            for child in (*node.body, *node.orelse):
                scan_statement(child, scope)
            return
        if isinstance(node, ast.While):
            scan_expression(node.test)
            for child in (*node.body, *node.orelse):
                scan_statement(child, scope)
            return
        if isinstance(node, ast.If):
            scan_expression(node.test)
            for child in (*node.body, *node.orelse):
                scan_statement(child, scope)
            return
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                scan_expression(item.context_expr)
                if item.optional_vars is not None:
                    scan_expression(item.optional_vars)
            for child in node.body:
                scan_statement(child, scope)
            return
        if isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                scan_statement(child, scope)
            for handler in node.handlers:
                if handler.type is not None:
                    scan_expression(handler.type)
                for child in handler.body:
                    scan_statement(child, scope)
            return
        calls.extend(_expression_calls(node))

    for statement in tree.body:
        scan_statement(statement, "module")
    return calls, decorators


def _module_assignment_names(tree: ast.Module) -> list[str]:
    names: list[str] = []

    def target_names(target: ast.AST) -> list[str]:
        if isinstance(target, ast.Name):
            return [target.id]
        if isinstance(target, (ast.Tuple, ast.List)):
            found: list[str] = []
            for element in target.elts:
                found.extend(target_names(element))
            return found
        return []

    def scan(statements: list[ast.stmt]) -> None:
        for node in statements:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    names.extend(target_names(target))
            elif isinstance(node, ast.AnnAssign):
                names.extend(target_names(node.target))
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                names.extend(target_names(node.target))
                scan([*node.body, *node.orelse])
            elif isinstance(node, (ast.While, ast.If)):
                scan([*node.body, *node.orelse])
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars is not None:
                        names.extend(target_names(item.optional_vars))
                scan(node.body)
            elif isinstance(node, ast.Try):
                scan([*node.body, *node.orelse, *node.finalbody])
                for handler in node.handlers:
                    if handler.name:
                        names.append(handler.name)
                    scan(handler.body)

    scan(tree.body)
    return names


def _allowed_import(path: Path, module: str) -> bool:
    if path.name == "scripted.py":
        return (
            module == "__future__"
            or module in _ALLOWED_STDLIB
            or module == _CANONICAL_CONTRACT
        )
    return module in {"__future__", ".", ".scripted"}


def _allowed_effects(path: Path, tree: ast.Module) -> bool:
    calls, decorators = _import_time_effects(tree)
    expected: set[tuple[str, str, bool]]
    if path.name == "scripted.py":
        expected = {(scope, "_dataclass", True) for scope in _DATACLASS_SCOPES}
    else:
        expected = set()
    actual = set(decorators)
    return len(calls) == len(expected) and actual == expected


def _production_shaped_baseline() -> ast.Module:
    return ast.parse(
        """
from dataclasses import dataclass as _dataclass

@_dataclass(frozen=True, slots=True)
class ScriptedModelStep:
    pass

@_dataclass(frozen=True, slots=True)
class ScriptedModelScenario:
    pass

__all__ = ["ScriptedModelRuntime", "ScriptedModelScenario", "ScriptedModelStep"]
"""
    )


def test_scripted_runtime_inventory_and_imports_are_allowlisted() -> None:
    assert all(path.is_file() for path in _PRODUCTION_FILES)
    assert sorted(path.name for path in _PACKAGE_ROOT.glob("*.py")) == [
        "__init__.py",
        "scripted.py",
    ]
    for path in _PRODUCTION_FILES:
        for module, _imported, _alias in _import_names(_tree(path)):
            if _allowed_import(path, module):
                continue
            if module.startswith(_FORBIDDEN_PREFIXES) or module.startswith(
                "ai_ecommerce_agent"
            ):
                pytest.fail(f"{path} imports forbidden module {module!r}")
            pytest.fail(f"{path} imports unexpected module {module!r}")


def test_import_time_effects_and_module_globals_are_frozen() -> None:
    for path in _PRODUCTION_FILES:
        tree = _tree(path)
        assert _allowed_effects(path, tree), path
        assert _module_assignment_names(tree) == ["__all__"], path


def test_import_guard_rejects_nested_calls_decorators_and_mutable_globals() -> None:
    baseline = _production_shaped_baseline()
    assert _allowed_effects(_PACKAGE_ROOT / "scripted.py", baseline)
    assert _module_assignment_names(baseline) == ["__all__"]
    source = ast.unparse(baseline)
    probes = (
        source.replace(
            "@_dataclass(frozen=True, slots=True)\nclass ScriptedModelStep",
            "@print\nclass ScriptedModelStep",
            1,
        ),
        source.replace(
            "class ScriptedModelStep:\n    pass",
            "class ScriptedModelStep:\n    token = uuid4()",
            1,
        ),
        source + "\n@print\ndef leaked(value=open('x')):\n    return value\n",
        source + "\nif open('x'):\n    leaked = True\n",
        source + "\nfor value in open('x'):\n    leaked = value\n",
        source + "\nfor sink[open('x')] in [1]:\n    leaked = True\n",
        source + "\nwith open('x') as handle:\n    leaked = handle\n",
        source + "\nif True:\n    _CACHE = []\n",
        source + "\ntry:\n    _CACHE = []\nexcept Exception:\n    pass\n",
    )
    for probe in probes[:7]:
        assert not _allowed_effects(_PACKAGE_ROOT / "scripted.py", ast.parse(probe))
    for probe in probes[7:]:
        tree = ast.parse(probe)
        assert _allowed_effects(_PACKAGE_ROOT / "scripted.py", tree)
        assert _module_assignment_names(tree) != ["__all__"]


def test_import_guard_rejects_forbidden_alias_imports() -> None:
    imports = _import_names(ast.parse("from openai import Client as _Client\n"))
    assert imports == [("openai", "Client", "_Client")]
    assert not _allowed_import(_PACKAGE_ROOT / "scripted.py", imports[0][0])


def test_package_facade_exports_only_scripted_symbols() -> None:
    tree = _tree(_PRODUCTION_FILES[0])
    assignments = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        )
    ]
    assert len(assignments) == 1
    value = assignments[0].value
    assert isinstance(value, ast.List)
    assert [elt.value for elt in value.elts if isinstance(elt, ast.Constant)] == [
        "ScriptedModelRuntime",
        "ScriptedModelScenario",
        "ScriptedModelStep",
    ]
