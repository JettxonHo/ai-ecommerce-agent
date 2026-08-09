"""Concrete Source immutable-read application use cases."""

from __future__ import annotations

from ai_ecommerce_agent.modules.source_evidence.application.association_errors import (
    SourceAssociationError,
)
from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceError,
    SourceEvidencePersistenceError,
)
from ai_ecommerce_agent.modules.source_evidence.application.mappers import (
    source_version_to_snapshot,
    task_source_association_to_snapshot,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceEvidenceUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceAssociationSnapshot,
    SourceVersionSnapshot,
)
from ai_ecommerce_agent.shared_kernel import (
    SourceAssociationId,
    SourceVersionId,
)

from .queries import GetSourceAssociation, GetSourceVersion
from .query_protocols import SourceEvidenceQueryApplication


def _source_version_not_found(
    source_version_id: SourceVersionId,
) -> SourceEvidenceError:
    return SourceEvidenceError(
        error_code="not_found",
        category="source_evidence",
        message="Source Version was not found",
        retryability=False,
        relevant_reference=source_version_id,
        recovery_hint="refresh",
    )


def _source_association_error(
    source_association_id: SourceAssociationId,
    *,
    error_code: str,
    message: str,
) -> SourceAssociationError:
    return SourceAssociationError(
        error_code=error_code,
        category="source_association",
        message=message,
        retryability=False,
        relevant_reference=source_association_id,
        recovery_hint="refresh",
    )


def _source_persistence_error(
    source_version_id: SourceVersionId,
) -> SourceEvidenceError:
    return SourceEvidenceError(
        error_code="persistence_error",
        category="source_evidence",
        message="Source Evidence persistence is unavailable",
        retryability=True,
        relevant_reference=source_version_id,
        recovery_hint="retry_later",
    )


def _association_persistence_error(
    source_association_id: SourceAssociationId,
) -> SourceAssociationError:
    return SourceAssociationError(
        error_code="persistence_error",
        category="source_association",
        message="Source association persistence is unavailable",
        retryability=True,
        relevant_reference=source_association_id,
        recovery_hint="retry_later",
    )


class SourceEvidenceQueryApplicationService(SourceEvidenceQueryApplication):
    """Read Source Current Truth in disposable no-commit query scopes."""

    def __init__(self, uow_factory: SourceEvidenceUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def get_source_version(self, query: GetSourceVersion) -> SourceVersionSnapshot:
        try:
            with self._uow_factory() as uow:
                source_version = uow.source_versions.get(query.source_version_id)
                processing = uow.source_version_processing.get(query.source_version_id)
                if source_version is None or processing is None:
                    raise _source_version_not_found(query.source_version_id)
                return source_version_to_snapshot(source_version, processing)
        except SourceEvidencePersistenceError as error:
            if type(error) is not SourceEvidencePersistenceError:
                raise
            raise _source_persistence_error(query.source_version_id) from error

    def get_source_association(
        self, query: GetSourceAssociation
    ) -> SourceAssociationSnapshot:
        try:
            with self._uow_factory() as uow:
                association = uow.source_associations.get(query.source_association_id)
                if association is None:
                    raise _source_association_error(
                        query.source_association_id,
                        error_code="not_found",
                        message="Source association was not found",
                    )
                if association.task_id != query.task_id:
                    raise _source_association_error(
                        query.source_association_id,
                        error_code="ownership_conflict",
                        message=(
                            "The Source association does not belong to the "
                            "requested owner"
                        ),
                    )
                return task_source_association_to_snapshot(association)
        except SourceEvidencePersistenceError as error:
            if type(error) is not SourceEvidencePersistenceError:
                raise
            raise _association_persistence_error(query.source_association_id) from error


__all__ = ["SourceEvidenceQueryApplicationService"]
