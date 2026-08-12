"""Architecture and inventory guards for the HTTP foundation slice."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).parents[2]
_SRC = _BACKEND / "src" / "ai_ecommerce_agent"
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
        imports = _imports(path)
        if "entrypoints/http" in path.as_posix():
            continue
        assert not imports & {"fastapi", "starlette", "uvicorn"}, path


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


def test_http_source_has_no_environment_network_or_server_start_side_effects() -> None:
    """The adapter may only define request-time behavior and pure values."""

    forbidden_names = {
        "getenv",
        "environ",
        "load_dotenv",
        "socket",
        "create_connection",
        "connect",
        "uvicorn",
        "run",
        "open",
        "Path",
    }
    for path in (_SRC / "entrypoints" / "http").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                assert node.id not in forbidden_names, f"{node.id} in {path}"
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_names, (
                    f"{node.func.attr} in {path}"
                )


def test_dependency_pins_are_exact() -> None:
    """The accepted transport/runtime versions cannot drift silently."""

    pyproject = (_BACKEND / "pyproject.toml").read_text(encoding="utf-8")
    assert '"fastapi==0.141.1"' in pyproject
    assert '"uvicorn==0.52.1"' in pyproject
