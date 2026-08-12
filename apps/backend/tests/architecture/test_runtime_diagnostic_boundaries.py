"""Architecture boundaries for the runtime diagnostic contract seam."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ai_ecommerce_agent.application as application_package

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _BACKEND_ROOT / "src"
_APPLICATION_ROOT = _BACKEND_ROOT / "src" / "ai_ecommerce_agent" / "application"
_APPLICATION_INIT = _APPLICATION_ROOT / "__init__.py"
_MODULE = _APPLICATION_ROOT / "runtime_diagnostics.py"
_AUTHORIZED_SINK_CONSUMER = (
    _SRC_ROOT / "ai_ecommerce_agent" / "platform" / "runtime_diagnostics.py"
)
_AUTHORIZED_ERROR_CONSUMER = _APPLICATION_ROOT / "runtime_errors.py"
_RUNTIME_MODULE = "ai_ecommerce_agent.application.runtime_diagnostics"
_EXPECTED_EXPORTS = [
    "CorrelationId",
    "RuntimeDiagnosticLevel",
    "RuntimeDiagnosticEvent",
    "encode_runtime_diagnostic_event",
]
_EXPECTED_IMPORTS = [
    ("__future__", "annotations", None),
    ("json", None, None),
    ("dataclasses", "dataclass", None),
    ("datetime", "UTC", None),
    ("datetime", "datetime", None),
    ("enum", "StrEnum", None),
    ("uuid", "uuid4", None),
]
_FORBIDDEN_PREFIXES = {
    "logging",
    "socket",
    "subprocess",
    "pathlib",
    "os",
    "sqlalchemy",
    "psycopg",
    "openai",
}


def _name(node: ast.AST) -> str | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _calls(node: ast.AST) -> list[ast.Call]:
    return [child for child in ast.walk(node) if isinstance(child, ast.Call)]


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


def _runtime_diagnostic_imports(path: Path, tree: ast.Module) -> list[str]:
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == _RUNTIME_MODULE or alias.name.startswith(
                    f"{_RUNTIME_MODULE}."
                ):
                    violations.append(f"{path}:{node.lineno}:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            target = _resolved_import_target(path, node)
            for alias in node.names:
                if target == _RUNTIME_MODULE or target.startswith(
                    f"{_RUNTIME_MODULE}."
                ):
                    violations.append(f"{path}:{node.lineno}:{target}")
                elif target == "ai_ecommerce_agent.application" and (
                    alias.name in {*_EXPECTED_EXPORTS, "runtime_diagnostics", "*"}
                ):
                    violations.append(f"{path}:{node.lineno}:{target}.{alias.name}")
    return violations


def _import_time_issues(tree: ast.Module) -> list[str]:
    issues: list[str] = []

    def expression(node: ast.AST, context: str) -> None:
        issues.extend(f"{context}: call" for _ in _calls(node))

    def decorator(node: ast.AST, *, class_scope: bool) -> None:
        if isinstance(node, ast.Call):
            if class_scope and _name(node.func) == "dataclass":
                for argument in (
                    *node.args,
                    *(keyword.value for keyword in node.keywords),
                ):
                    expression(argument, "dataclass decorator")
            else:
                issues.append("unauthorized decorator call")
        elif isinstance(node, ast.Name) and node.id == "classmethod":
            return
        elif class_scope:
            issues.append("unauthorized class decorator")
        else:
            issues.append("unauthorized function decorator")

    def function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for item in node.decorator_list:
            decorator(item, class_scope=False)
        for default in (
            *node.args.defaults,
            *(value for value in node.args.kw_defaults if value),
        ):
            expression(default, "function default")
        for argument in (
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
            node.args.vararg,
            node.args.kwarg,
        ):
            if argument is not None and argument.annotation is not None:
                expression(argument.annotation, "function annotation")
        if node.returns is not None:
            expression(node.returns, "function return annotation")

    def statements(body: list[ast.stmt]) -> None:
        for statement in body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function(statement)
            elif isinstance(statement, ast.ClassDef):
                for item in statement.decorator_list:
                    decorator(item, class_scope=True)
                for base in statement.bases:
                    expression(base, "class base")
                for keyword in statement.keywords:
                    expression(keyword.value, "class keyword")
                statements(statement.body)
            else:
                expression(statement, "module/class body")

    statements(tree.body)
    return issues


def _mutable_module_assignments(tree: ast.Module) -> list[str]:
    issues: list[str] = []

    def statements(body: list[ast.stmt]) -> None:
        for statement in body:
            if isinstance(
                statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                continue
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                value = statement.value
                targets = (
                    statement.targets
                    if isinstance(statement, ast.Assign)
                    else [statement.target]
                )
                names = {
                    target.id for target in targets if isinstance(target, ast.Name)
                }
                if names != {"__all__"} and isinstance(
                    value, (ast.List, ast.Dict, ast.Set)
                ):
                    issues.append("mutable module assignment")
            for child in ast.iter_child_nodes(statement):
                if isinstance(child, ast.stmt) and not isinstance(
                    child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    statements([child])

    statements(tree.body)
    return issues


def test_runtime_diagnostic_has_exact_one_production_module_and_facade() -> None:
    assert sorted(
        path.name for path in _APPLICATION_ROOT.glob("runtime_diagnostic*.py")
    ) == ["runtime_diagnostics.py"]
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    exports = next(
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        )
    )
    assert isinstance(exports, (ast.List, ast.Tuple))
    export_values: list[object] = []
    for element in exports.elts:
        assert isinstance(element, ast.Constant)
        export_values.append(element.value)
    assert export_values == _EXPECTED_EXPORTS
    assert all(not hasattr(application_package, name) for name in _EXPECTED_EXPORTS)


def test_application_init_and_repository_have_no_unexpected_consumer() -> None:
    init_tree = ast.parse(_APPLICATION_INIT.read_text(encoding="utf-8"))
    assert _runtime_diagnostic_imports(_APPLICATION_INIT, init_tree) == []
    export_assignment = next(
        node.value
        for node in init_tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        )
    )
    assert isinstance(export_assignment, (ast.List, ast.Tuple))
    exported_names = {
        element.value
        for element in export_assignment.elts
        if isinstance(element, ast.Constant) and isinstance(element.value, str)
    }
    assert exported_names.isdisjoint({*_EXPECTED_EXPORTS, "runtime_diagnostics"})

    violations = [
        violation
        for path in sorted((_SRC_ROOT / "ai_ecommerce_agent").rglob("*.py"))
        if path
        not in {
            _MODULE,
            _AUTHORIZED_SINK_CONSUMER,
            _AUTHORIZED_ERROR_CONSUMER,
        }
        for violation in _runtime_diagnostic_imports(
            path, ast.parse(path.read_text(encoding="utf-8"))
        )
    ]
    assert violations == []


def test_repository_guard_rejects_single_runtime_diagnostic_consumer_mutations() -> (
    None
):
    synthetic_path = _APPLICATION_ROOT / "synthetic_consumer.py"
    baseline = """
from ai_ecommerce_agent.application.errors import UnitOfWorkError
__all__ = ["UnitOfWorkError"]
"""
    assert _runtime_diagnostic_imports(synthetic_path, ast.parse(baseline)) == []
    for mutation in (
        "from . import runtime_diagnostics\n__all__ = ['runtime_diagnostics']",
        "from . import RuntimeDiagnosticEvent as Event",
        "from ai_ecommerce_agent.application.runtime_diagnostics import "
        "CorrelationId as RootCorrelation",
        "import ai_ecommerce_agent.application.runtime_diagnostics as "
        "diagnostic_module",
    ):
        assert _runtime_diagnostic_imports(synthetic_path, ast.parse(mutation))


def test_runtime_diagnostic_imports_only_allowlisted_stdlib_modules() -> None:
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    imports: list[tuple[str, str | None, str | None]] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend((alias.name, None, alias.asname) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0
            imports.extend(
                (node.module or "", alias.name, alias.asname) for alias in node.names
            )
        else:
            continue
    assert imports == _EXPECTED_IMPORTS
    for module, _, _ in imports:
        assert module not in _FORBIDDEN_PREFIXES


def test_runtime_diagnostic_has_no_import_time_calls_or_mutable_globals() -> None:
    tree = ast.parse(_MODULE.read_text(encoding="utf-8"))
    assert _import_time_issues(tree) == []
    assert _mutable_module_assignments(tree) == []


def test_import_time_guard_rejects_single_mutations_of_a_valid_shape() -> None:
    baseline = """
from dataclasses import dataclass
__all__ = ["Event"]
@dataclass(frozen=True, slots=True)
class Event:
    value: str
def encode(value: str = "ok") -> str:
    return value
"""
    assert _import_time_issues(ast.parse(baseline)) == []
    assert _mutable_module_assignments(ast.parse(baseline)) == []
    for mutation in (
        baseline.replace(
            'def encode(value: str = "ok")', 'def encode(value: str = print("x"))'
        ),
        baseline.replace(
            'def encode(value: str = "ok")', '@print\ndef encode(value: str = "ok")'
        ),
        baseline.replace("class Event:", "class Event(uuid4()):"),
        baseline.replace(
            "class Event:\n    value: str", "class Event:\n    value: str = uuid4()"
        ),
        baseline.replace('__all__ = ["Event"]', '__all__ = ["Event"]\n_CACHE = []'),
        baseline.replace(
            '__all__ = ["Event"]', '__all__ = ["Event"]\nif True:\n    _CACHE = []'
        ),
    ):
        tree = ast.parse(mutation)
        assert _import_time_issues(tree) or _mutable_module_assignments(tree)
