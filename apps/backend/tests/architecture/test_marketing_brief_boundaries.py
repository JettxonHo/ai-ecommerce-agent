"""Architecture evidence for framework-neutral Marketing Brief contracts."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ai_ecommerce_agent.modules.marketing_brief.domain as domain
import ai_ecommerce_agent.modules.marketing_brief.domain.contracts as contracts
import ai_ecommerce_agent.modules.marketing_brief.public as public

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


def test_marketing_brief_contract_modules_are_framework_neutral() -> None:
    for module in (contracts, public, domain):
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


def test_marketing_brief_contract_imports_have_no_io_or_resource_construction() -> None:
    for module in (contracts, public, domain):
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


def test_marketing_brief_public_facade_contains_only_immutable_contracts() -> None:
    assert public.__all__ == [
        "MarketingBriefSemanticGroupName",
        "MarketingBriefSemanticGroup",
        "MarketingBriefVersionSnapshot",
    ]
    assert not hasattr(public, "DomainVersionReference")
    assert not hasattr(public, "ResourceReference")
    assert not hasattr(public, "StructuredContent")


def test_marketing_brief_contract_uses_task_public_version_reference() -> None:
    tree = _module_tree(contracts)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "ai_ecommerce_agent.modules.task_management.public" in imports
    assert not any(
        module_name is not None
        and module_name.startswith("ai_ecommerce_agent.modules.task_management.")
        and module_name != "ai_ecommerce_agent.modules.task_management.public"
        for module_name in imports
    )
