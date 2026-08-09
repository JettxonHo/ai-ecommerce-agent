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


def test_durable_dispatch_contract_files_have_no_import_time_resource_calls() -> None:
    for path, tree in _trees():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            call_name = _dotted_name(node.func)
            assert call_name not in _FORBIDDEN_CALLS, (
                f"{path} performs forbidden resource call {call_name!r}"
            )


def test_durable_dispatch_package_imports_cleanly() -> None:
    import importlib

    public = importlib.import_module(
        "ai_ecommerce_agent.modules.durable_dispatch.public"
    )
    assert public.__name__ == "ai_ecommerce_agent.modules.durable_dispatch.public"
