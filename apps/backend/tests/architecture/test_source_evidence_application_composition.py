"""Architecture evidence for the Source Evidence composition root."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import get_type_hints

import pytest

from ai_ecommerce_agent.bootstrap import source_evidence_postgres
from ai_ecommerce_agent.modules.source_evidence import public
from ai_ecommerce_agent.modules.source_evidence.application.protocols import (
    SourceEvidenceApplication,
)
from ai_ecommerce_agent.platform.postgres import PostgresEngineConfig

pytestmark = pytest.mark.architecture

BACKEND_ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP_PATH = (
    BACKEND_ROOT
    / "src"
    / "ai_ecommerce_agent"
    / "bootstrap"
    / "source_evidence_postgres.py"
)


class _Engine:
    def __init__(self) -> None:
        self.dispose_calls = 0

    def dispose(self) -> None:
        self.dispose_calls += 1


class _Factory:
    calls: list[tuple[object, str]] = []

    @classmethod
    def from_engine(cls, engine: object, *, schema: str) -> _Factory:
        cls.calls.append((engine, schema))
        return cls()


def test_composition_wires_engine_factory_and_protocol_without_connecting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _Engine()
    config = PostgresEngineConfig(
        database_url="postgresql+psycopg://user:password@127.0.0.1:5432/database"
    )
    seen_configs: list[PostgresEngineConfig] = []

    def create_engine(value: PostgresEngineConfig) -> _Engine:
        seen_configs.append(value)
        return engine

    _Factory.calls.clear()
    monkeypatch.setattr(
        source_evidence_postgres, "create_postgres_engine", create_engine
    )
    monkeypatch.setattr(
        source_evidence_postgres,
        "SourceEvidencePostgresUnitOfWorkFactory",
        _Factory,
    )

    composition = source_evidence_postgres.compose_source_evidence_postgres(
        config, schema="mvp0_source_application"
    )

    assert seen_configs == [config]
    assert _Factory.calls == [(engine, "mvp0_source_application")]
    assert isinstance(composition.application, SourceEvidenceApplication)
    assert get_type_hints(type(composition))["application"] is SourceEvidenceApplication
    assert engine.dispose_calls == 0

    composition.close()
    assert engine.dispose_calls == 1


def test_bootstrap_module_has_no_import_time_calls_or_environment_io() -> None:
    tree = ast.parse(BOOTSTRAP_PATH.read_text())
    for statement in tree.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in statement.decorator_list:
                assert all(
                    not isinstance(node, ast.Call)
                    or isinstance(node.func, ast.Name)
                    and node.func.id == "dataclass"
                    for node in ast.walk(decorator)
                )
            continue
        assert not any(isinstance(node, ast.Call) for node in ast.walk(statement))

    source = BOOTSTRAP_PATH.read_text()
    assert "os.environ" not in source
    assert "alembic" not in source
    assert "create_all" not in source
    assert "connect(" not in source
    assert "worker" not in source.lower()


def test_source_public_facade_composes_processing_and_association_contracts() -> None:
    assert {
        "SourceEvidenceApplication",
        "SourceEvidenceError",
        "StartSourceProcessing",
        "RemoveSourceAssociation",
        "ReplaceSourceAssociation",
        "SourceAssociationApplication",
        "SourceAssociationError",
        "SourceAssociationReplacementSnapshot",
    }.issubset(public.__all__)
    assert not any(
        hasattr(public, name)
        for name in (
            "SourceEvidenceApplicationService",
            "SourceEvidencePostgresUnitOfWorkFactory",
            "Engine",
            "Session",
        )
    )


def test_composition_contract_exposes_only_lifecycle_objects() -> None:
    annotations = get_type_hints(
        source_evidence_postgres.SourceEvidencePostgresComposition
    )
    assert set(annotations) == {"engine", "uow_factory", "application"}
    assert annotations["application"] is SourceEvidenceApplication
    assert not hasattr(
        source_evidence_postgres.SourceEvidencePostgresComposition, "commit"
    )
    assert not hasattr(
        source_evidence_postgres.SourceEvidencePostgresComposition, "rollback"
    )
