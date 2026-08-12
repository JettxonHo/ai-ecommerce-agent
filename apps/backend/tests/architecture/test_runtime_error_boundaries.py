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
                    if not (
                        isinstance(decorator, ast.Call)
                        and _dotted_name(decorator.func) == "dataclass"
                    ):
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
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            names = {
                target.id
                for target in statement.targets
                if isinstance(target, ast.Name)
            }
            if names != {"__all__"} and isinstance(
                statement.value, (ast.Call, ast.Dict, ast.List, ast.Set)
            ):
                issues.append("mutable assignment")
        elif isinstance(statement, ast.AnnAssign) and isinstance(
            statement.value, (ast.Call, ast.Dict, ast.List, ast.Set)
        ):
            issues.append("mutable assignment")
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
    violations: list[str] = []
    for path in sorted((_SRC_ROOT / "ai_ecommerce_agent").rglob("*.py")):
        if path == _MODULE:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == _MODULE_NAME or alias.name.startswith(
                        f"{_MODULE_NAME}."
                    ):
                        violations.append(f"{path}:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                target = node.module or ""
                if node.level:
                    continue
                if target == _MODULE_NAME or target.startswith(f"{_MODULE_NAME}."):
                    violations.append(f"{path}:{target}")
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
    for mutation in (
        "import logging\nlogging.basicConfig()",
        "_CACHE = []",
        "from pathlib import Path\nPath('x')",
        "class ErrorId:\n    payload: dict[str, str]",
        "class ErrorId:\n    traceback: str",
    ):
        tree = ast.parse(baseline + "\n" + mutation)
        assert (
            _import_time_calls(tree)
            or _mutable_module_assignments(tree)
            or (_field_names(tree) & _FORBIDDEN_FIELD_NAMES)
        ), mutation
