"""Architecture locks for module-private Source table definitions."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.modules.source_evidence import infrastructure, public
from ai_ecommerce_agent.modules.source_evidence.infrastructure import tables

pytestmark = pytest.mark.architecture


def test_infrastructure_package_does_not_reexport_technical_table_objects() -> None:
    assert not any(
        hasattr(infrastructure, name)
        for name in (
            "SOURCES_TABLE",
            "SOURCE_VERSIONS_TABLE",
            "SOURCE_VERSION_PROCESSING_TABLE",
            "TASK_SOURCE_ASSOCIATIONS_TABLE",
            "Engine",
            "Session",
            "create_engine",
        )
    )


def test_table_module_has_no_process_or_transaction_resources() -> None:
    assert not any(
        hasattr(tables, name)
        for name in (
            "Engine",
            "Session",
            "AsyncSession",
            "create_engine",
            "sessionmaker",
            "Connection",
        )
    )
    assert not hasattr(tables.SOURCE_EVIDENCE_METADATA, "bind")


def test_source_public_facade_remains_the_four_symbol_contract() -> None:
    assert set(public.__all__) == {
        "SourceAssociationMembershipState",
        "SourceAssociationSnapshot",
        "SourceProcessingStatus",
        "SourceVersionSnapshot",
    }
    assert not any(
        hasattr(public, name)
        for name in (
            "SOURCES_TABLE",
            "SOURCE_EVIDENCE_METADATA",
            "Session",
            "Engine",
            "SourceEvidenceUnitOfWork",
        )
    )
