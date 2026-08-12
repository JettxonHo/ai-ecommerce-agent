"""Architecture and inventory guards for the HTTP foundation slice."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).parents[2]
_SRC = _BACKEND / "src" / "ai_ecommerce_agent"
_HTTP_ROOT = (_SRC / "entrypoints" / "http").resolve()
_FRAMEWORK_ROOTS = frozenset({"fastapi", "starlette", "uvicorn"})
_ALLOWED = {
    "apps/backend/pyproject.toml",
    "apps/backend/uv.lock",
    "apps/backend/src/ai_ecommerce_agent/entrypoints/__init__.py",
    "apps/backend/src/ai_ecommerce_agent/entrypoints/http/__init__.py",
    "apps/backend/src/ai_ecommerce_agent/entrypoints/http/config.py",
    "apps/backend/src/ai_ecommerce_agent/entrypoints/http/problems.py",
    "apps/backend/src/ai_ecommerce_agent/entrypoints/http/middleware.py",
    "apps/backend/src/ai_ecommerce_agent/entrypoints/http/app.py",
    "apps/backend/tests/contract/test_http_foundation_contract.py",
    "apps/backend/tests/unit/test_http_foundation.py",
    "apps/backend/tests/architecture/test_http_foundation_boundaries.py",
}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def _is_http_adapter_path(path: Path) -> bool:
    """Identify HTTP adapter files using the source root, not a substring."""

    try:
        path.resolve().relative_to(_HTTP_ROOT)
    except ValueError:
        return False
    return True


def _framework_import_roots(path: Path, source: str) -> set[str]:
    """Return framework roots imported by files outside the HTTP adapter."""

    if _is_http_adapter_path(path):
        return set()
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(
                alias.name.split(".", 1)[0] for alias in node.names if alias.name
            )
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots & _FRAMEWORK_ROOTS


def _qualified_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value)
        if parent is not None:
            return f"{parent}.{node.attr}"
    return None


def _is_mutable_expression(node: ast.AST) -> bool:
    if isinstance(
        node,
        (
            ast.List,
            ast.Dict,
            ast.Set,
            ast.ListComp,
            ast.DictComp,
            ast.SetComp,
        ),
    ):
        return True
    if isinstance(node, ast.Call):
        return _qualified_name(node.func) in {
            "bytearray",
            "collections.deque",
            "collections.defaultdict",
            "deque",
            "defaultdict",
            "dict",
            "list",
            "set",
        }
    return False


class _ModuleScopeMutationScanner(ast.NodeVisitor):
    """Find mutable objects assigned in module scope, not request-time locals."""

    def __init__(self) -> None:
        self.lines: list[int] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_Assign(self, node: ast.Assign) -> None:
        if _is_mutable_expression(node.value):
            self.lines.append(node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None and _is_mutable_expression(node.value):
            self.lines.append(node.lineno)
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        if _is_mutable_expression(node.value):
            self.lines.append(node.lineno)
        self.generic_visit(node)


def _module_scope_mutations(source: str) -> tuple[int, ...]:
    scanner = _ModuleScopeMutationScanner()
    scanner.visit(ast.parse(source))
    return tuple(scanner.lines)


class _ImportAliasScanner(ast.NodeVisitor):
    """Resolve aliases visible to module-level statements."""

    def __init__(self) -> None:
        self.module_aliases: dict[str, str] = {}
        self.symbol_aliases: dict[str, str] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local_name = alias.asname or alias.name.split(".", 1)[0]
            self.module_aliases[local_name] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is None:
            return
        for alias in node.names:
            if alias.name == "*":
                continue
            local_name = alias.asname or alias.name
            self.symbol_aliases[local_name] = f"{node.module}.{alias.name}"


def _resolve_alias(
    name: str,
    module_aliases: dict[str, str],
    symbol_aliases: dict[str, str],
) -> str:
    first, _, suffix = name.partition(".")
    canonical = module_aliases.get(first) or symbol_aliases.get(first)
    if canonical is None:
        return name
    return f"{canonical}.{suffix}" if suffix else canonical


def _is_environment_access(name: str) -> bool:
    return name == "os.getenv" or (
        name.startswith("os.environ.")
        and name.rsplit(".", 1)[-1]
        in {"__contains__", "__getitem__", "get", "pop", "setdefault"}
    )


def _is_clock_access(name: str) -> bool:
    if name in {
        "time.monotonic",
        "time.monotonic_ns",
        "time.perf_counter",
        "time.time",
        "time.time_ns",
    }:
        return True
    return name in {
        "datetime.date.today",
        "datetime.datetime.now",
        "datetime.datetime.utcnow",
    }


def _is_logging_configuration(name: str) -> bool:
    return name in {
        "logging.basicConfig",
        "logging.config.dictConfig",
        "logging.config.fileConfig",
    }


def _import_time_effects(source: str) -> frozenset[str]:
    tree = ast.parse(source)
    aliases = _ImportAliasScanner()
    aliases.visit(tree)
    effects: set[str] = set()

    class ImportTimeVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    self.visit(default)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    self.visit(default)

        def visit_Lambda(self, node: ast.Lambda) -> None:
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    self.visit(default)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for base in node.bases:
                self.visit(base)
            for keyword in node.keywords:
                self.visit(keyword.value)
            for statement in node.body:
                self.visit(statement)

        def visit_Call(self, node: ast.Call) -> None:
            name = _qualified_name(node.func)
            canonical = (
                _resolve_alias(
                    name,
                    aliases.module_aliases,
                    aliases.symbol_aliases,
                )
                if name is not None
                else None
            )
            if canonical is not None:
                if _is_environment_access(canonical):
                    effects.add("environment")
                if _is_clock_access(canonical):
                    effects.add("clock")
                if _is_logging_configuration(canonical):
                    effects.add("logging")
                if canonical in {
                    "socket.connect",
                    "socket.create_connection",
                    "socket.socket",
                }:
                    effects.add("network")
                if canonical in {"uvicorn.run", "uvicorn.Server"}:
                    effects.add("server")
                if canonical == "open":
                    effects.add("filesystem")
                if canonical in {
                    "pathlib.Path.mkdir",
                    "pathlib.Path.open",
                    "pathlib.Path.rename",
                    "pathlib.Path.replace",
                    "pathlib.Path.rmdir",
                    "pathlib.Path.touch",
                    "pathlib.Path.unlink",
                    "pathlib.Path.write_bytes",
                    "pathlib.Path.write_text",
                }:
                    effects.add("filesystem")
            self.generic_visit(node)

        def visit_Subscript(self, node: ast.Subscript) -> None:
            name = _qualified_name(node.value)
            canonical = (
                _resolve_alias(
                    name,
                    aliases.module_aliases,
                    aliases.symbol_aliases,
                )
                if name is not None
                else None
            )
            if canonical == "os.environ":
                effects.add("environment")
            self.generic_visit(node)

    ImportTimeVisitor().visit(tree)
    return frozenset(effects)


def test_allowlisted_new_file_inventory_is_exact() -> None:
    """Only the issue's explicitly owned files may be added or changed."""

    # This test is intentionally path-based: it catches accidental sibling
    # packages without depending on the current implementation details.
    tracked = {
        path.relative_to(_BACKEND.parent.parent).as_posix()
        for path in (_SRC / "entrypoints").rglob("*.py")
        if path.is_file()
    }
    expected_source = {
        path for path in _ALLOWED if path.startswith("apps/backend/src/")
    }
    assert tracked == expected_source


def test_framework_imports_are_confined_to_http_adapter() -> None:
    """FastAPI/Starlette ownership stays under ``entrypoints.http``."""

    for path in _SRC.rglob("*.py"):
        assert (
            _framework_import_roots(path, path.read_text(encoding="utf-8")) == set()
        ), path


def test_http_adapter_does_not_import_business_or_provider_layers() -> None:
    """Foundation construction cannot reach application, persistence, or SDKs."""

    forbidden = {
        "ai_ecommerce_agent.application",
        "ai_ecommerce_agent.bootstrap",
        "ai_ecommerce_agent.modules",
        "ai_ecommerce_agent.orchestration",
        "ai_ecommerce_agent.platform",
        "openai",
        "sqlalchemy",
        "psycopg",
    }
    for path in (_SRC / "entrypoints" / "http").rglob("*.py"):
        imports = _imports(path)
        assert not any(
            imported == target or imported.startswith(f"{target}.")
            for imported in imports
            for target in forbidden
        ), path


def test_http_source_has_no_module_scope_mutation_or_import_time_effects() -> None:
    """Only immutable definitions and request-time bodies are permitted."""

    for path in (_SRC / "entrypoints" / "http").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert _module_scope_mutations(source) == (), path
        assert _import_time_effects(source) == frozenset(), path


def test_framework_import_scanner_has_valid_baseline_and_single_mutation_probe() -> (
    None
):
    """Submodule imports are caught without substring-based path false positives."""

    baseline = "from dataclasses import dataclass\nIMMUTABLE = frozenset({'ok'})\n"
    assert _framework_import_roots(_SRC / "modules" / "baseline.py", baseline) == set()
    mutation = (
        "import fastapi.routing\n"
        "from starlette.responses import JSONResponse\n"
        "import uvicorn.config as runtime\n"
    )
    assert _framework_import_roots(_SRC / "modules" / "mutated.py", mutation) == {
        "fastapi",
        "starlette",
        "uvicorn",
    }
    assert (
        _framework_import_roots(
            _SRC / "entrypoints" / "http" / "synthetic.py",
            mutation,
        )
        == set()
    )


def test_module_scope_mutation_scanner_has_valid_baseline_and_single_probe() -> None:
    """Mutable globals fail while mutable request-time locals remain valid."""

    baseline = (
        "from typing import Final\n"
        "IMMUTABLE: Final = frozenset({'ok'})\n"
        "def request_time():\n"
        "    local = []\n"
        "    return local\n"
    )
    assert _module_scope_mutations(baseline) == ()
    assert _module_scope_mutations(f"{baseline}\nMUTABLE = []\n")


def test_import_time_clock_scanner_has_valid_baseline_and_single_probe() -> None:
    """Request-time clocks are allowed; module-time clock acquisition is not."""

    baseline = (
        "from typing import Final\n"
        "IMMUTABLE: Final = frozenset({'ok'})\n"
        "def request_time():\n"
        "    import time as clock\n"
        "    return clock.time()\n"
    )
    assert _import_time_effects(baseline) == frozenset()
    mutation = "import time as clock\nVALUE = clock.time()\n"
    assert _import_time_effects(mutation) == frozenset({"clock"})


def test_import_time_logging_scanner_has_valid_baseline_and_single_probe() -> None:
    """Request-time logging stays possible without import-time configuration."""

    baseline = (
        "def request_time():\n"
        "    import logging\n"
        "    return logging.getLogger(__name__)\n"
    )
    assert _import_time_effects(baseline) == frozenset()
    mutation = "import logging as log\nlog.basicConfig()\n"
    assert _import_time_effects(mutation) == frozenset({"logging"})


def test_import_time_environment_scanner_has_valid_baseline_and_alias_probe() -> None:
    """Aliased environment reads are caught only when evaluated at import time."""

    baseline = (
        "def request_time():\n    import os as env\n    return env.getenv('VALUE')\n"
    )
    assert _import_time_effects(baseline) == frozenset()
    mutation = "from os import getenv as read_env\nVALUE = read_env('SECRET')\n"
    assert _import_time_effects(mutation) == frozenset({"environment"})


def test_dependency_pins_are_exact() -> None:
    """The accepted transport/runtime versions cannot drift silently."""

    pyproject = (_BACKEND / "pyproject.toml").read_text(encoding="utf-8")
    assert '"fastapi==0.141.1"' in pyproject
    assert '"uvicorn==0.52.1"' in pyproject
