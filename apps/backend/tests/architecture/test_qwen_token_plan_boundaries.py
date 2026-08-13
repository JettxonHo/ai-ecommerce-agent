"""Architecture boundaries for the private Qwen supplemental adapter."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ai_ecommerce_agent.platform.model_runtime as _runtime_package

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_SOURCE = _BACKEND / "src" / "ai_ecommerce_agent"
_PACKAGE = _SOURCE / "platform" / "model_runtime" / "qwen_token_plan"
_FILES = tuple(
    _PACKAGE / name
    for name in (
        "__init__.py",
        "_runtime.py",
        "_request_preparation.py",
        "_response_mapping.py",
    )
)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            values.add(("." * node.level) + (node.module or ""))
    return values


def test_private_package_inventory_and_empty_facade_are_exact() -> None:
    assert sorted(path.name for path in _PACKAGE.glob("*.py")) == [
        "__init__.py",
        "_request_preparation.py",
        "_response_mapping.py",
        "_runtime.py",
    ]
    _runtime_package.__dict__.pop("qwen_token_plan", None)
    assert _runtime_package.__dict__.get("__all__") == [
        "ScriptedModelRuntime",
        "ScriptedModelScenario",
        "ScriptedModelStep",
    ]
    assert "qwen_token_plan" not in _runtime_package.__dict__


def test_adapter_imports_stay_inside_the_private_infrastructure_seam() -> None:
    forbidden = {
        "ai_ecommerce_agent.bootstrap",
        "ai_ecommerce_agent.entrypoints",
        "ai_ecommerce_agent.modules",
        "ai_ecommerce_agent.orchestration",
        "ai_ecommerce_agent.platform.model_runtime.openai_responses",
        "fastapi",
        "httpx",
        "pathlib",
        "psycopg",
        "sqlalchemy",
        "socket",
        "subprocess",
    }
    for path in _FILES:
        imports = _imports(path)
        assert not any(
            value in forbidden or value.startswith(tuple(forbidden))
            for value in imports
        ), (path.name, imports)


def test_top_level_runtime_source_does_not_select_qwen_by_default() -> None:
    source = (_SOURCE / "platform" / "model_runtime" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert "qwen_token_plan" not in source
