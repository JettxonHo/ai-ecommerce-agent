"""Architecture boundaries for the Product Intake output-only seam."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_SRC = _BACKEND / "src/ai_ecommerce_agent"
_PACKAGE = _SRC / "modules/product_intake"
_FILES = [
    _PACKAGE / "__init__.py",
    _PACKAGE / "application/__init__.py",
    _PACKAGE / "application/skills/__init__.py",
    _PACKAGE / "application/skills/product_intake_fact_extraction/__init__.py",
    _PACKAGE / "application/skills/product_intake_fact_extraction/output_contract.py",
]
_ALLOWED_IMPORTS = {
    "__future__",
    "collections.abc",
    "enum",
    "typing",
    "ai_ecommerce_agent.application.model_runtime",
    "ai_ecommerce_agent.shared_kernel.structured_content",
    ".output_contract",
}
_FORBIDDEN = {
    "openai",
    "langgraph",
    "sqlalchemy",
    "psycopg",
    "repository",
    "uow",
    "source_evidence",
    "fragment",
    "evidence",
    "pathlib",
    "os",
    "socket",
    "requests",
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _import_names(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.append("." * node.level + (node.module or ""))
    return names


def _calls_at_import_time(tree: ast.Module) -> list[ast.Call]:
    calls: list[ast.Call] = []

    def scan_statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                calls.extend(
                    item for item in ast.walk(decorator) if isinstance(item, ast.Call)
                )
            return
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                calls.extend(
                    item for item in ast.walk(decorator) if isinstance(item, ast.Call)
                )
            for child in node.body:
                scan_statement(child)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            return
        calls.extend(item for item in ast.walk(node) if isinstance(item, ast.Call))

    for statement in tree.body:
        scan_statement(statement)
    return calls


def test_exact_allowlisted_files_and_imports() -> None:
    assert all(path.is_file() for path in _FILES)
    for path in _FILES:
        tree = _tree(path)
        for imported in _import_names(tree):
            assert imported in _ALLOWED_IMPORTS, (path.name, imported)
            if imported.startswith("ai_ecommerce_agent."):
                assert not any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for forbidden in _FORBIDDEN
                )
            else:
                assert not any(part in _FORBIDDEN for part in imported.split("."))


def test_no_import_time_calls_or_mutable_module_globals() -> None:
    for path in _FILES:
        tree = _tree(path)
        assert not _calls_at_import_time(tree), path
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names = {
                    target.id for target in node.targets if isinstance(target, ast.Name)
                }
                if names == {"__all__"}:
                    continue
                assert not isinstance(node.value, (ast.List, ast.Dict, ast.Set))


def test_production_shaped_single_mutation_probe_catches_forbidden_import() -> None:
    baseline = ast.parse(
        "from enum import StrEnum\n"
        "from ai_ecommerce_agent.application.model_runtime import "
        "StructuredOutputSpec\n"
    )
    mutation = ast.parse("import openai\n")
    assert all(name not in _FORBIDDEN for name in _import_names(baseline))
    assert any(name == "openai" for name in _import_names(mutation))
