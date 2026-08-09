"""Typed persistence ports owned by the Source and Evidence application.

The ports intentionally expose only the operations needed by the current
domain slice.  ``SourceVersion`` is immutable, while processing and task
membership are revisioned current-truth records.  Transaction lifecycle stays
owned by the enclosing Unit of Work rather than any repository.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_ecommerce_agent.application.ports import UnitOfWork
from ai_ecommerce_agent.shared_kernel import (
    Revision,
    SourceAssociationId,
    SourceVersionId,
)

from ..domain import (
    SourceVersion,
    SourceVersionProcessing,
    TaskSourceAssociation,
)


@runtime_checkable
class SourceVersionRepositoryPort(Protocol):
    """Load and register immutable Source Version identity records."""

    def get(self, source_version_id: SourceVersionId) -> SourceVersion | None:
        """Return the immutable Source Version, or ``None`` if absent."""

        ...

    def add(self, source_version: SourceVersion) -> None:
        """Stage a newly-created Source Version for the current commit."""

        ...


@runtime_checkable
class SourceVersionProcessingRepositoryPort(Protocol):
    """Load and CAS-save mutable processing Current Truth records."""

    def get(self, source_version_id: SourceVersionId) -> SourceVersionProcessing | None:
        """Return processing Current Truth, or ``None`` if absent."""

        ...

    def add(self, processing: SourceVersionProcessing) -> None:
        """Stage a newly-created processing record for the current commit."""

        ...

    def save(
        self,
        processing: SourceVersionProcessing,
        *,
        expected_revision: Revision,
    ) -> None:
        """CAS-save processing Current Truth without owning the transaction."""

        ...


@runtime_checkable
class TaskSourceAssociationRepositoryPort(Protocol):
    """Load and CAS-save revisioned Task-to-Source membership records."""

    def get(
        self, source_association_id: SourceAssociationId
    ) -> TaskSourceAssociation | None:
        """Return the association, or ``None`` if absent."""

        ...

    def add(self, association: TaskSourceAssociation) -> None:
        """Stage a newly-created association for the current commit."""

        ...

    def save(
        self,
        association: TaskSourceAssociation,
        *,
        expected_revision: Revision,
    ) -> None:
        """CAS-save an association without owning the transaction."""

        ...


@runtime_checkable
class SourceEvidenceUnitOfWork(UnitOfWork, Protocol):
    """One-shot UoW exposing only Source and Evidence repository ports."""

    @property
    def source_versions(self) -> SourceVersionRepositoryPort:
        """Immutable Source Version identity repository."""

        ...

    @property
    def source_version_processing(
        self,
    ) -> SourceVersionProcessingRepositoryPort:
        """Revisioned Source Version processing repository."""

        ...

    @property
    def source_associations(self) -> TaskSourceAssociationRepositoryPort:
        """Revisioned Task-to-Source association repository."""

        ...


@runtime_checkable
class SourceEvidenceUnitOfWorkFactory(Protocol):
    """Create a fresh Source Evidence UoW per transactional command."""

    def __call__(self) -> SourceEvidenceUnitOfWork:
        """Return a new one-shot UoW with private transaction resources."""

        ...


__all__ = [
    "SourceEvidenceUnitOfWork",
    "SourceEvidenceUnitOfWorkFactory",
    "SourceVersionProcessingRepositoryPort",
    "SourceVersionRepositoryPort",
    "TaskSourceAssociationRepositoryPort",
]
