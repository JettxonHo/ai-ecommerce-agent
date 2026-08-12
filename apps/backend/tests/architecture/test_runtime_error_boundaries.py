"""Architecture boundaries for the runtime error value seam."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _BACKEND_ROOT / "src"
_APPLICATION_ROOT = _SRC_ROOT / "ai_ecommerce_agent" / "application"
_MODULE = _APPLICATION_ROOT / "runtime_errors.py"
_MODULE_NAME = "ai_ecommerce_agent.application.runtime_errors"
_MODULE_SYMBOLS = {
    "ErrorId",
    "RuntimeErrorCategory",
    "RuntimeErrorRetryability",
    "RuntimeErrorDisposition",
    "RuntimeErrorIdentity",
    "RuntimeErrorRecord",
    "runtime_error_to_diagnostic_event",
}
_EXPECTED_IMPORTS = [
    ("__future__", "annotations", None),
    ("dataclasses", "dataclass", None),
    ("datetime", "UTC", None),
    ("datetime", "datetime", None),
    ("enum", "StrEnum", None),
    ("uuid", "uuid4", None),
    ("ai_ecommerce_agent.application.runtime_diagnostics", "CorrelationId", None),
    (
        "ai_ecommerce_agent.application.runtime_diagnostics",
        "RuntimeDiagnosticEvent",
        None,
    ),
    (
        "ai_ecommerce_agent.application.runtime_diagnostics",
        "RuntimeDiagnosticLevel",
        None,
    ),
    ("ai_ecommerce_agent.shared_kernel", "ResourceReference", None),
    ("ai_ecommerce_agent.shared_kernel", "RunId", None),
    ("ai_ecommerce_agent.shared_kernel", "TaskId", None),
]
_FORBIDDEN_PREFIXES = (
    "logging",
    "openai",
    "httpx",
    "requests",
    "socket",
    "os",
    "pathlib",
    "subprocess",
    "sqlalchemy",
    "psycopg",
    "fastapi",
    "starlette",
    "langgraph",
)
_FORBIDDEN_FIELD_NAMES = {
    "error_code",
    "cause_chain",
    "input_versions",
    "input_version_ids",
    "exception",
    "traceback",
    "stack",
    "locals",
    "headers",
    "url",
    "payload",
    "context",
    "message",
}


def _tree() -> ast.Module:
    return ast.parse(_MODULE.read_text(encoding="utf-8"))


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


def _imports(tree: ast.Module) -> list[tuple[str, str | None, str | None]]:
    imports: list[tuple[str, str | None, str | None]] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend((alias.name, None, alias.asname) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imports.extend(
                (node.module or "", alias.name, alias.asname) for alias in node.names
            )
    return imports


def _package_for(path: Path) -> tuple[str, ...]:
    parts = list(
        path.relative_to(_SRC_ROOT / "ai_ecommerce_agent").with_suffix("").parts
    )
    parts.pop()
    return ("ai_ecommerce_agent", *parts)


def _resolved_import_target(path: Path, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""
    package = _package_for(path)
    base = package[: len(package) - (node.level - 1)]
    if node.module:
        base = (*base, *node.module.split("."))
    return ".".join(base)


def _runtime_error_import_violations(path: Path, tree: ast.Module) -> list[str]:
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == _MODULE_NAME or alias.name.startswith(
                    f"{_MODULE_NAME}."
                ):
                    violations.append(f"{path}:{node.lineno}:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            target = _resolved_import_target(path, node)
            if target == _MODULE_NAME or target.startswith(f"{_MODULE_NAME}."):
                violations.extend(
                    f"{path}:{node.lineno}:{target}.{alias.name}"
                    for alias in node.names
                )
            elif target == "ai_ecommerce_agent.application" and any(
                alias.name in {*_MODULE_SYMBOLS, "runtime_errors", "*"}
                for alias in node.names
            ):
                violations.extend(
                    f"{path}:{node.lineno}:{target}.{alias.name}"
                    for alias in node.names
                )
    return violations


def _import_time_calls(tree: ast.Module) -> list[str]:
    calls: list[str] = []

    def scan_expression(node: ast.AST, context: str) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                calls.append(f"{context}:{_dotted_name(child.func)}")

    def scan_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for decorator in node.decorator_list:
            scan_expression(decorator, "decorator")
        for default in (
            *node.args.defaults,
            *(value for value in node.args.kw_defaults if value),
        ):
            scan_expression(default, "default")
        for argument in (
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
            node.args.vararg,
            node.args.kwarg,
        ):
            if argument is not None and argument.annotation is not None:
                scan_expression(argument.annotation, "annotation")
        if node.returns is not None:
            scan_expression(node.returns, "return")

    def scan(body: list[ast.stmt]) -> None:
        for statement in body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scan_function(statement)
            elif isinstance(statement, ast.ClassDef):
                for decorator in statement.decorator_list:
                    if (
                        isinstance(decorator, ast.Call)
                        and _dotted_name(decorator.func) == "dataclass"
                    ):
                        for argument in (
                            *decorator.args,
                            *(keyword.value for keyword in decorator.keywords),
                        ):
                            scan_expression(argument, "dataclass decorator")
                    elif (
                        isinstance(decorator, ast.Name) and decorator.id == "dataclass"
                    ):
                        continue
                    else:
                        scan_expression(decorator, "class-decorator")
                for base in statement.bases:
                    scan_expression(base, "class-base")
                for keyword in statement.keywords:
                    scan_expression(keyword.value, "class-keyword")
                scan(statement.body)
            else:
                scan_expression(statement, "module-or-class")

    scan(tree.body)
    return calls


def _mutable_module_assignments(tree: ast.Module) -> list[str]:
    issues: list[str] = []

    def is_mutable_literal(node: ast.AST | None) -> bool:
        return isinstance(node, (ast.Call, ast.Dict, ast.List, ast.Set))

    def scan_expression(node: ast.AST) -> None:
        for child in ast.walk(node):
            if isinstance(child, ast.NamedExpr) and is_mutable_literal(child.value):
                issues.append("mutable named assignment")

    def scan(body: list[ast.stmt]) -> None:
        for statement in body:
            if isinstance(
                statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                continue
            if isinstance(statement, ast.Assign):
                names = {
                    target.id
                    for target in statement.targets
                    if isinstance(target, ast.Name)
                }
                if names != {"__all__"} and is_mutable_literal(statement.value):
                    issues.append("mutable assignment")
                scan_expression(statement.value)
            elif isinstance(statement, ast.AnnAssign) and is_mutable_literal(
                statement.value
            ):
                issues.append("mutable assignment")
            elif isinstance(statement, ast.AnnAssign):
                scan_expression(statement.value) if statement.value else None
            elif isinstance(statement, ast.Expr):
                scan_expression(statement.value)
            elif isinstance(statement, (ast.If, ast.While)):
                scan_expression(statement.test)
                scan([*statement.body, *statement.orelse])
            elif isinstance(statement, (ast.For, ast.AsyncFor)):
                scan_expression(statement.iter)
                scan([*statement.body, *statement.orelse])
            elif isinstance(statement, (ast.With, ast.AsyncWith)):
                for item in statement.items:
                    scan_expression(item.context_expr)
                scan(statement.body)
            elif isinstance(statement, ast.Try):
                scan([*statement.body, *statement.orelse, *statement.finalbody])
                for handler in statement.handlers:
                    scan(handler.body)

    scan(tree.body)
    return issues


def _field_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def test_runtime_error_has_exact_one_production_file_and_facade() -> None:
    assert sorted(
        path.name for path in _APPLICATION_ROOT.glob("runtime_error*.py")
    ) == ["runtime_errors.py"]
    tree = _tree()
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        )
    )
    assert isinstance(assignment.value, ast.List)
    assert [
        element.value
        for element in assignment.value.elts
        if isinstance(element, ast.Constant)
    ] == [
        "ErrorId",
        "RuntimeErrorCategory",
        "RuntimeErrorRetryability",
        "RuntimeErrorDisposition",
        "RuntimeErrorIdentity",
        "RuntimeErrorRecord",
        "runtime_error_to_diagnostic_event",
    ]


def test_runtime_error_imports_and_effects_are_exact() -> None:
    tree = _tree()
    assert _imports(tree) == _EXPECTED_IMPORTS
    assert all(
        not module.startswith(_FORBIDDEN_PREFIXES) for module, _, _ in _imports(tree)
    )
    assert _import_time_calls(tree) == []
    assert _mutable_module_assignments(tree) == []
    assert _field_names(tree).isdisjoint(_FORBIDDEN_FIELD_NAMES)


def test_runtime_error_has_no_unauthorized_consumer_or_reexport() -> None:
    init_path = _APPLICATION_ROOT / "__init__.py"
    init_tree = ast.parse(init_path.read_text(encoding="utf-8"))
    assert _runtime_error_import_violations(init_path, init_tree) == []
    assert not any(
        isinstance(node, ast.Name) and node.id in {*_MODULE_SYMBOLS, "runtime_errors"}
        for node in ast.walk(init_tree)
    )
    for node in ast.walk(init_tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        ):
            assert isinstance(node.value, (ast.List, ast.Tuple))
            assert {
                element.value
                for element in node.value.elts
                if isinstance(element, ast.Constant)
            }.isdisjoint({*_MODULE_SYMBOLS, "runtime_errors"})
    violations: list[str] = []
    for path in sorted((_SRC_ROOT / "ai_ecommerce_agent").rglob("*.py")):
        if path == _MODULE:
            continue
        violations.extend(
            _runtime_error_import_violations(
                path, ast.parse(path.read_text(encoding="utf-8"))
            )
        )
    assert violations == []


def test_architecture_probes_reject_payload_and_import_effect_mutations() -> None:
    baseline = """
from dataclasses import dataclass
__all__ = ["ErrorId"]
@dataclass(frozen=True, slots=True)
class ErrorId:
    value: str
"""
    assert _import_time_calls(ast.parse(baseline)) == []
    assert _mutable_module_assignments(ast.parse(baseline)) == []
    synthetic_path = _APPLICATION_ROOT / "synthetic_runtime_error_consumer.py"
    assert (
        _runtime_error_import_violations(
            synthetic_path, ast.parse("from .errors import UnitOfWorkError")
        )
        == []
    )
    for mutation in (
        "from .runtime_errors import ErrorId as Alias",
        "from . import runtime_errors",
        "from .runtime_errors import *",
        "from ai_ecommerce_agent.application.runtime_errors import ErrorId as Alias",
        "import ai_ecommerce_agent.application.runtime_errors as errors",
        "from ai_ecommerce_agent.application import runtime_errors as errors",
    ):
        assert _runtime_error_import_violations(synthetic_path, ast.parse(mutation)), (
            mutation
        )
    for mutation in (
        "import logging\nlogging.basicConfig()",
        "_CACHE = []",
        "from pathlib import Path\nPath('x')",
        "class ErrorId:\n    payload: dict[str, str]",
        "class ErrorId:\n    traceback: str",
        "from dataclasses import dataclass\n"
        "@dataclass(frozen=print())\nclass ErrorId:\n    value: str",
        "if True:\n    _CACHE: list[str] = []",
        "if (_CACHE := []):\n    pass",
    ):
        tree = ast.parse(baseline + "\n" + mutation)
        assert (
            _import_time_calls(tree)
            or _mutable_module_assignments(tree)
            or (_field_names(tree) & _FORBIDDEN_FIELD_NAMES)
        ), mutation
