"""Architecture evidence for the framework-neutral Human Review contracts."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ai_ecommerce_agent.modules.human_review.domain.contracts as contracts
import ai_ecommerce_agent.modules.human_review.public as public

pytestmark = pytest.mark.architecture

_FORBIDDEN_IMPORTS = (
    "sqlalchemy",
    "langgraph",
    "fastapi",
    "starlette",
    "openai",
    "anthropic",
)
_FORBIDDEN_TOP_LEVEL_CALLS = {
    "connect",
    "create_engine",
    "getenv",
    "open",
    "read_text",
    "write_text",
}


def _module_tree(module: object) -> ast.Module:
    module_file = Path(module.__file__)  # type: ignore[attr-defined]
    return ast.parse(module_file.read_text(encoding="utf-8"))


def test_human_review_contract_modules_are_framework_neutral() -> None:
    for module in (contracts, public):
        tree = _module_tree(module)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        assert not any(
            imported == forbidden or imported.startswith(f"{forbidden}.")
            for imported in imports
            for forbidden in _FORBIDDEN_IMPORTS
        )


def test_human_review_contract_imports_have_no_io_or_resource_construction() -> None:
    for module in (contracts, public):
        tree = _module_tree(module)
        module_body = tree.body
        top_level_calls = {
            node.func.attr
            for statement in module_body
            for node in ast.walk(statement)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        top_level_calls.update(
            node.func.id
            for statement in module_body
            for node in ast.walk(statement)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        )
        assert top_level_calls.isdisjoint(_FORBIDDEN_TOP_LEVEL_CALLS)
