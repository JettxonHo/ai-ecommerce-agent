"""Typed Source and Evidence repository/UoW contracts for #112."""

from __future__ import annotations

from inspect import getattr_static, getmro, signature
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.modules.source_evidence.application import (
    SourceEvidenceUnitOfWork,
    SourceEvidenceUnitOfWorkFactory,
    SourceVersionProcessingRepositoryPort,
    SourceVersionRepositoryPort,
    TaskSourceAssociationRepositoryPort,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceVersion,
    SourceVersionProcessing,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceVersionId,
)

pytestmark = pytest.mark.contract


def test_source_repository_ports_are_typed_and_do_not_own_transactions() -> None:
    repository_shapes = (
        (
            SourceVersionRepositoryPort,
            {"get", "add"},
            {"source_version_id": SourceVersionId, "return": SourceVersion | None},
            {"source_version": SourceVersion, "return": type(None)},
        ),
        (
            SourceVersionProcessingRepositoryPort,
            {"get", "add", "save"},
            {
                "source_version_id": SourceVersionId,
                "return": SourceVersionProcessing | None,
            },
            {"processing": SourceVersionProcessing, "return": type(None)},
        ),
        (
            TaskSourceAssociationRepositoryPort,
            {"get", "add", "save"},
            {
                "source_association_id": SourceAssociationId,
                "return": TaskSourceAssociation | None,
            },
            {"association": TaskSourceAssociation, "return": type(None)},
        ),
    )

    for repository, methods, get_hints, add_hints in repository_shapes:
        assert {
            name
            for name in ("get", "add", "save", "commit", "rollback", "close")
            if callable(getattr(repository, name, None))
        } == methods
        assert get_type_hints(repository.get) == get_hints
        assert get_type_hints(repository.add) == add_hints

    for save_method in (
        SourceVersionProcessingRepositoryPort.save,
        TaskSourceAssociationRepositoryPort.save,
    ):
        save_hints = get_type_hints(save_method)
        assert save_hints["expected_revision"] is Revision
        assert "expected_revision" in signature(save_method).parameters
        assert len(signature(save_method).parameters) == 3


def test_immutable_source_version_has_no_save_or_update_port() -> None:
    assert not hasattr(SourceVersionRepositoryPort, "save")
    assert not hasattr(SourceVersionRepositoryPort, "update")


def test_source_uow_inherits_shared_lifecycle_and_only_exposes_typed_repositories() -> (
    None
):
    assert UnitOfWork in getmro(SourceEvidenceUnitOfWork)
    properties: tuple[tuple[str, type[object]], ...] = (
        ("source_versions", SourceVersionRepositoryPort),
        ("source_version_processing", SourceVersionProcessingRepositoryPort),
        ("source_associations", TaskSourceAssociationRepositoryPort),
    )
    for name, repository in properties:
        property_value = cast(property, getattr_static(SourceEvidenceUnitOfWork, name))
        assert isinstance(property_value, property)
        assert property_value.fget is not None
        assert get_type_hints(property_value.fget)["return"] is repository
    assert not any(
        hasattr(SourceEvidenceUnitOfWork, name)
        for name in ("session", "registry", "get_repository")
    )
    assert get_type_hints(SourceEvidenceUnitOfWorkFactory.__call__)["return"] is (
        SourceEvidenceUnitOfWork
    )
