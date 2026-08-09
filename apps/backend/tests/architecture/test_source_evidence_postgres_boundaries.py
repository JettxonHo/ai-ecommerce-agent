"""Architecture locks for the Source Evidence PostgreSQL adapter boundary."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import ai_ecommerce_agent.modules.source_evidence.infrastructure as infrastructure
from ai_ecommerce_agent.modules.source_evidence import public
from ai_ecommerce_agent.modules.source_evidence.infrastructure.repositories import (
    SourceEvidencePostgresSourceVersionProcessingRepository,
    SourceEvidencePostgresSourceVersionRepository,
    SourceEvidencePostgresTaskSourceAssociationRepository,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.uow import (
    SourceEvidencePostgresUnitOfWorkFactory,
)

pytestmark = pytest.mark.architecture

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (
    BACKEND_ROOT / "src" / "ai_ecommerce_agent" / "modules" / "source_evidence"
)


def test_public_facade_and_infrastructure_facade_stay_narrow() -> None:
    assert {
        "SourceAssociationMembershipState",
        "SourceAssociationSnapshot",
        "SourceProcessingStatus",
        "SourceVersionSnapshot",
    }.issubset(public.__all__)
    assert not hasattr(public, "SourceEvidencePostgresUnitOfWorkFactory")
    assert not hasattr(public, "Session")
    assert not hasattr(infrastructure, "Session")
    assert isinstance(SourceEvidencePostgresUnitOfWorkFactory, type)


def test_source_adapter_has_exactly_three_typed_repository_classes() -> None:
    assert all(
        isinstance(repository, type)
        for repository in (
            SourceEvidencePostgresSourceVersionRepository,
            SourceEvidencePostgresSourceVersionProcessingRepository,
            SourceEvidencePostgresTaskSourceAssociationRepository,
        )
    )
    repository_source = (SOURCE_ROOT / "infrastructure" / "repositories.py").read_text()
    tree = ast.parse(repository_source)
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    assert [node.name for node in classes] == [
        "SourceEvidencePostgresSourceVersionRepository",
        "SourceEvidencePostgresSourceVersionProcessingRepository",
        "SourceEvidencePostgresTaskSourceAssociationRepository",
    ]


def test_repositories_do_not_own_transaction_or_generic_access() -> None:
    repository_source = (SOURCE_ROOT / "infrastructure" / "repositories.py").read_text()
    tree = ast.parse(repository_source)
    forbidden = {
        "begin",
        "begin_nested",
        "commit",
        "rollback",
        "close",
        "get_repository",
        "execute_sql",
    }
    assert not {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr in forbidden
    }
    assert "sqlalchemy.text" not in repository_source
    assert "registry" not in repository_source


def test_uow_factory_is_the_only_engine_composition_surface() -> None:
    uow_source = (SOURCE_ROOT / "infrastructure" / "uow.py").read_text()
    tree = ast.parse(uow_source)
    class_names = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
    assert class_names == [
        "SourceEvidencePostgresUnitOfWork",
        "SourceEvidencePostgresUnitOfWorkFactory",
    ]
    assert "schema_translate_map" in uow_source
    assert "sessionmaker" in uow_source
    assert "get_repository" not in uow_source
    assert "execute_sql" not in uow_source
