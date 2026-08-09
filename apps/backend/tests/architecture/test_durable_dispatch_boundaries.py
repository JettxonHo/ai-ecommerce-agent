"""Architecture boundaries for the Durable Dispatch contract foundation."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_DISPATCH_ROOT = (
    _BACKEND_ROOT / "src" / "ai_ecommerce_agent" / "modules" / "durable_dispatch"
)
_PRODUCTION_FILES = (
    _DISPATCH_ROOT / "__init__.py",
    _DISPATCH_ROOT / "domain" / "__init__.py",
    _DISPATCH_ROOT / "domain" / "identity.py",
    _DISPATCH_ROOT / "domain" / "status.py",
    _DISPATCH_ROOT / "public.py",
)
_ALLOWED_RELATIVE_IMPORTS: dict[Path, frozenset[tuple[int, str | None]]] = {
    _DISPATCH_ROOT / "__init__.py": frozenset(),
    _DISPATCH_ROOT / "domain" / "__init__.py": frozenset(),
    _DISPATCH_ROOT / "domain" / "identity.py": frozenset(),
    _DISPATCH_ROOT / "domain" / "status.py": frozenset(),
    _DISPATCH_ROOT / "public.py": frozenset(
        {(1, "domain.identity"), (1, "domain.status")}
    ),
}
_ALLOWED_STDLIB_IMPORTS = {
    "__future__",
    "dataclasses",
    "enum",
    "typing",
    "uuid",
}
_FORBIDDEN_IMPORT_PREFIXES = (
    "sqlalchemy",
    "psycopg",
    "fastapi",
    "starlette",
    "langgraph",
    "openai",
    "anthropic",
    "os",
    "pathlib",
    "socket",
    "subprocess",
    "dotenv",
)
_FORBIDDEN_CALLS = {
    "open",
    "os.getenv",
    "os.environ",
    "pathlib.Path",
    "Path",
    "socket.socket",
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.call",
}


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


def _trees() -> list[tuple[Path, ast.Module]]:
    return [
        (path, ast.parse(path.read_text(encoding="utf-8")))
        for path in _PRODUCTION_FILES
    ]


def test_durable_dispatch_contract_files_are_framework_neutral() -> None:
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    assert (node.level, node.module) in _ALLOWED_RELATIVE_IMPORTS[
                        path
                    ], (
                        f"{path} imports an undeclared relative module "
                        f"{node.module!r} at level {node.level}"
                    )
                    continue
                imported_names = [node.module or ""]
            else:
                continue
            for imported in imported_names:
                root_name = imported.split(".", 1)[0]
                assert root_name in _ALLOWED_STDLIB_IMPORTS, (
                    f"{path} imports non-stdlib module {imported!r}"
                )
                assert not imported.startswith(_FORBIDDEN_IMPORT_PREFIXES), (
                    f"{path} imports forbidden module {imported!r}"
                )


def _module_scope_calls(tree: ast.Module) -> list[ast.Call]:
    calls: list[ast.Call] = []
    for statement in tree.body:
        if isinstance(statement, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            expressions: list[ast.AST] = [*statement.decorator_list]
            if isinstance(statement, ast.ClassDef):
                expressions.extend(statement.bases)
                expressions.extend(keyword.value for keyword in statement.keywords)
            else:
                expressions.extend(statement.args.defaults)
                expressions.extend(
                    default
                    for default in statement.args.kw_defaults
                    if default is not None
                )
                if statement.returns is not None:
                    expressions.append(statement.returns)
        else:
            expressions = [statement]
        calls.extend(
            node
            for expression in expressions
            for node in ast.walk(expression)
            if isinstance(node, ast.Call)
        )
    return calls


def _allowed_typevar_calls(tree: ast.Module) -> set[int]:
    allowed: set[int] = set()
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        targets = {
            target.id for target in statement.targets if isinstance(target, ast.Name)
        }
        if "_IdentityT" not in targets:
            continue
        allowed.update(
            id(node)
            for node in ast.walk(statement)
            if isinstance(node, ast.Call) and _dotted_name(node.func) == "TypeVar"
        )
    return allowed


def test_durable_dispatch_contract_files_have_no_module_scope_calls() -> None:
    for path, tree in _trees():
        allowed_typevar_calls = _allowed_typevar_calls(tree)
        for call in _module_scope_calls(tree):
            call_name = _dotted_name(call.func)
            if call_name == "dataclass" or id(call) in allowed_typevar_calls:
                continue
            assert call_name not in _FORBIDDEN_CALLS, (
                f"{path} performs forbidden module-scope call {call_name!r}"
            )
            raise AssertionError(
                f"{path} performs undeclared module-scope call {call_name!r}"
            )


def test_durable_dispatch_package_imports_cleanly() -> None:
    import importlib

    public = importlib.import_module(
        "ai_ecommerce_agent.modules.durable_dispatch.public"
    )
    assert public.__name__ == "ai_ecommerce_agent.modules.durable_dispatch.public"
