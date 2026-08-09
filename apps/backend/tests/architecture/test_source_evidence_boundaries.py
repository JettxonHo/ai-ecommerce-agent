"""Architecture locks for the narrow Source public facade."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.modules.source_evidence import public

pytestmark = pytest.mark.architecture


def test_source_facade_does_not_expose_domain_or_technical_internals() -> None:
    assert {
        "SourceAssociationMembershipState",
        "SourceAssociationSnapshot",
        "SourceProcessingStatus",
        "SourceVersionSnapshot",
    }.issubset(public.__all__)
    for internal_name in (
        "Source",
        "SourceVersion",
        "SourceVersionProcessing",
        "TaskSourceAssociation",
        "SourceRepository",
        "SourceEvidenceUnitOfWork",
        "Session",
        "AsyncSession",
        "DeclarativeBase",
        "StateGraph",
    ):
        assert not hasattr(public, internal_name)
