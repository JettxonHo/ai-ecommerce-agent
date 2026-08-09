"""Architecture locks for Source and Evidence application ports."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.modules.source_evidence import public
from ai_ecommerce_agent.modules.source_evidence.application import ports

pytestmark = pytest.mark.architecture


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
