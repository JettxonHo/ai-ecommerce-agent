"""Architecture boundaries for private Durable Dispatch table metadata."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ai_ecommerce_agent.modules.durable_dispatch import infrastructure, public
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure import tables

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_INFRA_ROOT = (
    _BACKEND_ROOT
    / "src"
    / "ai_ecommerce_agent"
    / "modules"
    / "durable_dispatch"
    / "infrastructure"
)
_TABLES_PATH = _INFRA_ROOT / "tables.py"
_INIT_PATH = _INFRA_ROOT / "__init__.py"
_FORBIDDEN_IMPORT_PREFIXES = (
    "alembic",
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
_FORBIDDEN_TECHNICAL_NAMES = {
    "Engine",
    "Session",
    "AsyncSession",
    "Connection",
    "create_engine",
    "sessionmaker",
    "create_all",
    "drop_all",
    "create_table",
    "drop_table",
    "execute",
    "connect",
    "getenv",
    "load_dotenv",
}


def _trees() -> tuple[tuple[Path, ast.Module], ...]:
    return tuple(
        (path, ast.parse(path.read_text(encoding="utf-8")))
        for path in (_TABLES_PATH, _INIT_PATH)
    )


def test_infrastructure_package_does_not_reexport_table_objects() -> None:
    assert not any(
        hasattr(infrastructure, name)
        for name in (
            "DURABLE_DISPATCH_SCHEMA_TOKEN",
            "DURABLE_DISPATCH_METADATA",
            "WORK_INTENTS_TABLE",
            "schema_translate_map",
        )
    )
    assert not hasattr(infrastructure, "__all__")


def test_table_module_exposes_only_the_exact_four_contract_symbols() -> None:
    assert tables.__all__ == [
        "DURABLE_DISPATCH_SCHEMA_TOKEN",
        "DURABLE_DISPATCH_METADATA",
        "WORK_INTENTS_TABLE",
        "schema_translate_map",
    ]
    assert not any(hasattr(tables, name) for name in _FORBIDDEN_TECHNICAL_NAMES)
    assert not hasattr(tables.DURABLE_DISPATCH_METADATA, "bind")


def test_durable_public_facade_remains_technical_free() -> None:
    assert not any(
        hasattr(public, name)
        for name in (
            "DURABLE_DISPATCH_METADATA",
            "WORK_INTENTS_TABLE",
            "MetaData",
            "Table",
            "Engine",
            "Session",
        )
    )


def test_table_modules_use_only_sqlalchemy_and_stdlib_imports() -> None:
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    assert path == _INIT_PATH
                    continue
                imported = [node.module or ""]
            else:
                continue
            for module in imported:
                root = module.split(".", 1)[0]
                assert root in {"__future__", "re", "sqlalchemy"}, (
                    f"{path} imports disallowed module {module!r}"
                )
                assert not module.startswith(_FORBIDDEN_IMPORT_PREFIXES), (
                    f"{path} imports forbidden module {module!r}"
                )


def test_table_modules_do_not_construct_process_resources_or_execute_ddl() -> None:
    for path, tree in _trees():
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        assert not names & _FORBIDDEN_TECHNICAL_NAMES, path
        assert not attributes & _FORBIDDEN_TECHNICAL_NAMES, path
