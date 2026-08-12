"""Architecture boundaries for the local runtime diagnostic sink."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _BACKEND_ROOT / "src"
_PLATFORM_ROOT = _SRC_ROOT / "ai_ecommerce_agent" / "platform"
_PLATFORM_INIT = _PLATFORM_ROOT / "__init__.py"
_MODULE = _PLATFORM_ROOT / "runtime_diagnostics.py"
_RUNTIME_MODULE = "ai_ecommerce_agent.platform.runtime_diagnostics"
_APPLICATION_MODULE = "ai_ecommerce_agent.application.runtime_diagnostics"
_EXPECTED_EXPORTS = ["RuntimeDiagnosticJsonLineSink"]
_EXPECTED_IMPORTS = [
    ("__future__", "annotations", None),
    ("logging", None, None),
    ("typing", "TextIO", None),
    (_APPLICATION_MODULE, "RuntimeDiagnosticEvent", None),
    (_APPLICATION_MODULE, "RuntimeDiagnosticLevel", None),
    (_APPLICATION_MODULE, "encode_runtime_diagnostic_event", None),
]
_FORBIDDEN_IMPORT_PREFIXES = (
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
_FORBIDDEN_LOGGING_CALLS = {"logging.getLogger", "logging.basicConfig"}
_ALLOWED_LOGGING_MODULE_CALLS = {"Formatter", "Logger", "StreamHandler"}
_FORBIDDEN_GLOBAL_LOGGING_SYMBOLS = {
    "addLevelName",
    "basicConfig",
    "captureWarnings",
    "disable",
    "getLogger",
    "setLoggerClass",
    "setLogRecordFactory",
    "shutdown",
}
_FORBIDDEN_GLOBAL_LOGGING_METHODS = {
    "addHandler",
    "removeHandler",
    "setLevel",
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


def _sink_import_violations(path: Path, tree: ast.Module) -> list[str]:
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
                elif target == "ai_ecommerce_agent.platform" and (
                    alias.name in {*_EXPECTED_EXPORTS, "runtime_diagnostics", "*"}
                ):
                    violations.append(f"{path}:{node.lineno}:{target}.{alias.name}")
    return violations


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


def _calls(node: ast.AST) -> list[ast.Call]:
    return [child for child in ast.walk(node) if isinstance(child, ast.Call)]


def _import_time_calls(tree: ast.Module) -> list[str]:
    calls: list[str] = []

    def scan_expression(node: ast.AST, context: str) -> None:
        calls.extend(f"{context}:{_dotted_name(call.func)}" for call in _calls(node))

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

    def scan_statements(body: list[ast.stmt]) -> None:
        for statement in body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scan_function(statement)
            elif isinstance(statement, ast.ClassDef):
                for decorator in statement.decorator_list:
                    scan_expression(decorator, "class-decorator")
                for base in statement.bases:
                    scan_expression(base, "class-base")
                for keyword in statement.keywords:
                    scan_expression(keyword.value, "class-keyword")
                scan_statements(statement.body)
            else:
                scan_expression(statement, "module-or-class")

    scan_statements(tree.body)
    return calls


def _mutable_module_assignments(tree: ast.Module) -> list[str]:
    issues: list[str] = []

    def scan(body: list[ast.stmt]) -> None:
        for statement in body:
            if isinstance(
                statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                continue
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                targets = (
                    statement.targets
                    if isinstance(statement, ast.Assign)
                    else [statement.target]
                )
                names = {
                    target.id for target in targets if isinstance(target, ast.Name)
                }
                if names != {"__all__"} and isinstance(
                    statement.value, (ast.Call, ast.Dict, ast.List, ast.Set)
                ):
                    issues.append("mutable module assignment")
            for child in ast.iter_child_nodes(statement):
                if isinstance(child, ast.stmt) and not isinstance(
                    child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    scan([child])

    scan(tree.body)
    return issues


def _forbidden_logging_calls(tree: ast.Module) -> list[str]:
    return [
        _dotted_name(node.func) or "<call>"
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and (_dotted_name(node.func) in _FORBIDDEN_LOGGING_CALLS)
    ]


def _logging_global_violations(tree: ast.Module) -> list[str]:
    """Reject global logging configuration while allowing local logger setup."""

    logging_aliases = {"logging"}
    forbidden_symbol_aliases: set[str] = set()
    root_aliases: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "logging":
                    logging_aliases.add(alias.asname or "logging")
        elif isinstance(node, ast.ImportFrom) and node.module == "logging":
            for alias in node.names:
                local_name = alias.asname or alias.name
                if alias.name in _FORBIDDEN_GLOBAL_LOGGING_SYMBOLS:
                    forbidden_symbol_aliases.add(local_name)
                if alias.name == "root":
                    root_aliases.add(local_name)

    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
                continue
            if (
                not isinstance(node.value, ast.Name)
                or node.value.id not in logging_aliases
            ):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                dotted = _dotted_name(target)
                if dotted is not None and dotted not in logging_aliases:
                    logging_aliases.add(dotted)
                    changed = True

    def root_reference(node: ast.AST) -> bool:
        dotted = _dotted_name(node)
        if dotted is None:
            return False
        parts = dotted.split(".")
        return dotted in root_aliases or (
            len(parts) == 2 and parts[0] in logging_aliases and parts[1] == "root"
        )

    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            if node.value is None:
                continue
            if not root_reference(node.value):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                dotted = _dotted_name(target)
                if dotted is not None and dotted not in root_aliases:
                    root_aliases.add(dotted)
                    changed = True

    local_logger_names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Attribute):
            continue
        if not isinstance(value.func.value, ast.Name):
            continue
        if value.func.value.id in logging_aliases and value.func.attr == "Logger":
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            local_logger_names.update(
                dotted
                for target in targets
                if (dotted := _dotted_name(target)) is not None
            )

    def is_root_expression(node: ast.AST) -> bool:
        return root_reference(node)

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name):
                if function.id in forbidden_symbol_aliases:
                    violations.append(f"global logging symbol: {function.id}")
                continue
            if not isinstance(function, ast.Attribute):
                continue
            if is_root_expression(function.value):
                violations.append(f"global logging root: {_dotted_name(function)}")
                continue
            dotted_function = _dotted_name(function)
            dotted_parts = dotted_function.split(".") if dotted_function else []
            if dotted_parts and dotted_parts[0] in logging_aliases:
                if len(dotted_parts) == 2 and dotted_parts[1] in (
                    _ALLOWED_LOGGING_MODULE_CALLS
                ):
                    continue
                violations.append(f"global logging module: {dotted_function}")
                continue
            if isinstance(function.value, ast.Name):
                if function.value.id in logging_aliases:
                    continue
                base = _dotted_name(function.value)
                if (
                    function.attr in _FORBIDDEN_GLOBAL_LOGGING_METHODS
                    and base not in local_logger_names
                ):
                    violations.append(
                        f"global logging method: {_dotted_name(function)}"
                    )
        if isinstance(node, ast.Attribute):
            if node.attr == "handlers" and is_root_expression(node.value):
                violations.append("global logging handlers")
            if is_root_expression(node):
                violations.append(f"global logging root: {_dotted_name(node)}")
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(
                isinstance(target, ast.Attribute)
                and target.attr == "handlers"
                and is_root_expression(target.value)
                for target in targets
            ):
                violations.append("global logging handlers assignment")
    return violations


def _level_mapping(tree: ast.Module) -> list[tuple[str, str]]:
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_logging_level"
    )
    mapping: list[tuple[str, str]] = []
    for node in function.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "level"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Is)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Attribute)
            and isinstance(test.comparators[0].value, ast.Name)
            and test.comparators[0].value.id == "RuntimeDiagnosticLevel"
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Return)
            and node.body[0].value is not None
        ):
            continue
        returned = _dotted_name(node.body[0].value)
        if returned is not None:
            mapping.append((test.comparators[0].attr, returned))
    return mapping


def test_sink_has_exact_one_production_file_and_facade() -> None:
    assert sorted(
        path.name for path in _PLATFORM_ROOT.glob("runtime_diagnostic*.py")
    ) == ["runtime_diagnostics.py"]
    tree = _tree(_MODULE)
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
    assert all(isinstance(element, ast.Constant) for element in exports.elts)
    assert [
        element.value for element in exports.elts if isinstance(element, ast.Constant)
    ] == _EXPECTED_EXPORTS


def test_sink_imports_only_logging_typing_and_validated_application_seam() -> None:
    tree = _tree(_MODULE)
    imports = _imports(tree)
    assert imports == _EXPECTED_IMPORTS
    assert all(
        not module.startswith(_FORBIDDEN_IMPORT_PREFIXES) for module, _, _ in imports
    )


def test_sink_has_no_import_time_effects_mutable_globals_or_global_logger_setup() -> (
    None
):
    tree = _tree(_MODULE)
    assert _import_time_calls(tree) == []
    assert _mutable_module_assignments(tree) == []
    assert _forbidden_logging_calls(tree) == []
    assert _logging_global_violations(tree) == []


def test_level_mapping_is_exact_and_global_logging_mutations_are_rejected() -> None:
    tree = _tree(_MODULE)
    expected_mapping = [
        ("INFO", "logging.INFO"),
        ("WARNING", "logging.WARNING"),
        ("ERROR", "logging.ERROR"),
        ("CRITICAL", "logging.CRITICAL"),
    ]
    assert _level_mapping(tree) == expected_mapping

    baseline = """
import logging
__all__ = ["RuntimeDiagnosticJsonLineSink"]
class RuntimeDiagnosticJsonLineSink:
    def __init__(self) -> None:
        logger = logging.Logger("sink")
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.log(logging.INFO, "message")
    def emit(self) -> None:
        self._logger.log(logging.WARNING, "message")

def _logging_level(level):
    if level is RuntimeDiagnosticLevel.INFO:
        return logging.INFO
    if level is RuntimeDiagnosticLevel.WARNING:
        return logging.WARNING
    if level is RuntimeDiagnosticLevel.ERROR:
        return logging.ERROR
    if level is RuntimeDiagnosticLevel.CRITICAL:
        return logging.CRITICAL
"""
    baseline_tree = ast.parse(baseline)
    assert _logging_global_violations(baseline_tree) == []
    assert _level_mapping(baseline_tree) == expected_mapping

    mutations = (
        "logging.root.addHandler(handler)",
        "import logging as log\nlog.root.removeHandler(handler)",
        (
            "import logging as log\n"
            "root_alias = log.root\n"
            "root_alias.setLevel(logging.WARNING)"
        ),
        (
            "import logging as log\n"
            "module_alias = log\n"
            "module_alias.root.setLevel(logging.WARNING)"
        ),
        ("import logging as log\nroot_alias = log.root\nroot_alias.handlers.clear()"),
        (
            "from logging import root as global_root\n"
            "global_root.setLevel(logging.WARNING)"
        ),
        "import logging as log\nlog.root.handlers.clear()",
        "import logging\nlogging.root.handlers = []",
        "import logging\nlogging.captureWarnings(True)",
        "from logging import shutdown as stop\nstop()",
        "import logging as log\nlog.config.dictConfig({})",
        "import logging\nlogging.disable(logging.CRITICAL)",
        (
            "class Leaked:\n"
            "    def __init__(self):\n"
            "        logging.root.addHandler(handler)"
        ),
        (
            "class Leaked:\n"
            "    def emit(self):\n"
            "        from logging import shutdown as stop\n"
            "        stop()"
        ),
    )
    for mutation in mutations:
        mutated_tree = ast.parse(baseline + "\n" + mutation)
        assert _logging_global_violations(mutated_tree), mutation

    always_info = (
        baseline.replace("return logging.WARNING", "return logging.INFO")
        .replace("return logging.ERROR", "return logging.INFO")
        .replace("return logging.CRITICAL", "return logging.INFO")
    )
    assert _logging_global_violations(ast.parse(always_info)) == []
    assert _level_mapping(ast.parse(always_info)) != expected_mapping


def test_platform_and_repository_have_no_sink_reexport() -> None:
    init_tree = _tree(_PLATFORM_INIT)
    assert _sink_import_violations(_PLATFORM_INIT, init_tree) == []
    violations = [
        violation
        for path in sorted((_SRC_ROOT / "ai_ecommerce_agent").rglob("*.py"))
        if path != _MODULE
        for violation in _sink_import_violations(path, _tree(path))
    ]
    assert violations == []


def test_repository_guard_rejects_single_sink_import_or_reexport_mutations() -> None:
    synthetic_path = _PLATFORM_ROOT / "synthetic_consumer.py"
    baseline = "from .postgres import engine\n__all__ = []"
    assert _sink_import_violations(synthetic_path, ast.parse(baseline)) == []
    for mutation in (
        "from . import runtime_diagnostics\n__all__ = ['runtime_diagnostics']",
        "from .runtime_diagnostics import RuntimeDiagnosticJsonLineSink as Sink",
        "from ai_ecommerce_agent.platform.runtime_diagnostics import "
        "RuntimeDiagnosticJsonLineSink as Sink",
        "import ai_ecommerce_agent.platform.runtime_diagnostics as sink_module",
        "from ai_ecommerce_agent.platform import RuntimeDiagnosticJsonLineSink as Sink",
    ):
        assert _sink_import_violations(synthetic_path, ast.parse(mutation))


def test_architecture_guard_rejects_import_time_and_global_logging_mutations() -> None:
    baseline = """
import logging
__all__ = ["RuntimeDiagnosticJsonLineSink"]
class RuntimeDiagnosticJsonLineSink:
    def __init__(self) -> None:
        self.value = 1
"""
    baseline_tree = ast.parse(baseline)
    assert _import_time_calls(baseline_tree) == []
    assert _mutable_module_assignments(baseline_tree) == []
    assert _forbidden_logging_calls(baseline_tree) == []
    for mutation in (
        "import logging\n_LOGGER = logging.getLogger('sink')",
        "import logging\nlogging.basicConfig()",
        "import logging\n_HANDLER = logging.StreamHandler()",
        "open('runtime.log', 'w')",
        "_CACHE = []",
    ):
        tree = ast.parse(mutation)
        assert (
            _import_time_calls(tree)
            or _mutable_module_assignments(tree)
            or _forbidden_logging_calls(tree)
        )
