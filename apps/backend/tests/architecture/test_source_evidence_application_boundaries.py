"""Architecture locks for Source and Evidence application ports."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ai_ecommerce_agent.modules.source_evidence import public
from ai_ecommerce_agent.modules.source_evidence.application import ports

pytestmark = pytest.mark.architecture

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (
    BACKEND_ROOT / "src" / "ai_ecommerce_agent" / "modules" / "source_evidence"
)
_APPLICATION_PUBLIC_MODULES = (
    SOURCE_ROOT / "application" / "commands.py",
    SOURCE_ROOT / "application" / "errors.py",
    SOURCE_ROOT / "application" / "mappers.py",
    SOURCE_ROOT / "application" / "protocols.py",
    SOURCE_ROOT / "application" / "association_commands.py",
    SOURCE_ROOT / "application" / "association_errors.py",
    SOURCE_ROOT / "application" / "association_protocols.py",
    SOURCE_ROOT / "application" / "association_results.py",
    SOURCE_ROOT / "application" / "queries.py",
    SOURCE_ROOT / "application" / "query_protocols.py",
    SOURCE_ROOT / "public.py",
)
_ALLOWED_DECORATORS = {"dataclass", "runtime_checkable"}


def _call_name(node: ast.Call) -> str | None:
    function = node.func
    if isinstance(function, ast.Name):
        return function.id
    if isinstance(function, ast.Attribute):
        return function.attr
    return None


def _top_level_calls(node: ast.AST) -> list[ast.Call]:
    """Find calls in a module-level statement without entering definitions."""

    calls: list[ast.Call] = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        calls.extend(
            descendant
            for descendant in ast.walk(child)
            if isinstance(descendant, ast.Call)
        )
    return calls


def test_new_application_public_modules_have_no_import_time_resources() -> None:
    """Bounded AST guard against import-time construction or I/O."""

    for path in _APPLICATION_PUBLIC_MODULES:
        tree = ast.parse(path.read_text())
        for statement in tree.body:
            if isinstance(
                statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                for decorator in statement.decorator_list:
                    calls = [
                        node
                        for node in ast.walk(decorator)
                        if isinstance(node, ast.Call)
                    ]
                    assert all(
                        _call_name(node) in _ALLOWED_DECORATORS for node in calls
                    ), path
                continue
            assert not _top_level_calls(statement), path


def test_source_ports_are_module_private_and_framework_neutral() -> None:
    assert set(ports.__all__) == {
        "SourceEvidenceUnitOfWork",
        "SourceEvidenceUnitOfWorkFactory",
        "SourceVersionProcessingRepositoryPort",
        "SourceVersionRepositoryPort",
        "TaskSourceAssociationRepositoryPort",
    }
    assert not any(
        hasattr(ports, name)
        for name in (
            "Session",
            "AsyncSession",
            "Engine",
            "DeclarativeBase",
            "select",
            "registry",
        )
    )


def test_source_public_facade_retains_the_existing_four_symbols() -> None:
    assert {
        "SourceAssociationMembershipState",
        "SourceAssociationSnapshot",
        "SourceProcessingStatus",
        "SourceVersionSnapshot",
    }.issubset(public.__all__)
    assert not hasattr(public, "SourceEvidenceUnitOfWork")


def test_source_query_contract_is_public_without_technical_leakage() -> None:
    assert {
        "GetSourceVersion",
        "GetSourceAssociation",
        "SourceEvidenceQueryApplication",
    }.issubset(public.__all__)
    assert not any(
        hasattr(public, name)
        for name in (
            "SourceEvidenceQueryApplicationService",
            "SourceEvidencePostgresUnitOfWorkFactory",
            "Engine",
            "Session",
        )
    )
