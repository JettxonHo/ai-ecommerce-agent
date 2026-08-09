"""Typed SQLAlchemy Core repositories for Source Evidence."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy import CursorResult, Executable, insert, select, update
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceConstraintError,
    SourceEvidenceOwnershipError,
    SourceEvidencePersistenceError,
    SourceEvidenceRevisionConflictError,
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

from .mappings import (
    source_version_domain_to_row,
    source_version_processing_domain_to_row,
    source_version_processing_row_to_domain,
    source_version_row_to_domain,
    task_source_association_domain_to_row,
    task_source_association_row_to_domain,
)
from .tables import (
    SOURCE_VERSION_PROCESSING_TABLE,
    SOURCE_VERSIONS_TABLE,
    SOURCES_TABLE,
    TASK_SOURCE_ASSOCIATIONS_TABLE,
)

_OWNER_CONSTRAINTS = frozenset(
    {
        "fk_source_evidence_source_versions_source_owner",
        "fk_source_evidence_source_version_processing_version_owner",
        "fk_source_evidence_task_source_associations_task_owner",
        "fk_source_evidence_task_source_associations_source_owner",
        "fk_source_evidence_assoc_source_version_owner",
        "fk_source_evidence_task_source_associations_replacement_owner",
    }
)


def _constraint_name(error: IntegrityError) -> str | None:
    diagnostic = getattr(error.orig, "diag", None)
    name = getattr(diagnostic, "constraint_name", None)
    return name if isinstance(name, str) and name else None


def _translate_integrity(
    error: IntegrityError,
) -> SourceEvidenceConstraintError | SourceEvidenceOwnershipError:
    name = _constraint_name(error)
    if name in _OWNER_CONSTRAINTS:
        return SourceEvidenceOwnershipError(
            resource="source_evidence_relationship", constraint_name=name
        )
    return SourceEvidenceConstraintError(constraint_name=name)


def _execute(session: Session, statement: Executable) -> CursorResult[Any]:
    try:
        return cast(CursorResult[Any], session.execute(statement))
    except IntegrityError as error:
        raise _translate_integrity(error) from error
    except SQLAlchemyError as error:
        raise SourceEvidencePersistenceError() from error


def _fetch_one(session: Session, statement: Executable) -> Mapping[str, object] | None:
    try:
        row = _execute(session, statement).mappings().one_or_none()
    except IntegrityError as error:
        raise _translate_integrity(error) from error
    except SQLAlchemyError as error:
        raise SourceEvidencePersistenceError() from error
    return cast(Mapping[str, object] | None, row)


class SourceEvidencePostgresSourceVersionRepository:
    """Immutable Source Version identity repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, source_version_id: SourceVersionId) -> SourceVersion | None:
        row = _fetch_one(
            self._session,
            select(SOURCE_VERSIONS_TABLE).where(
                SOURCE_VERSIONS_TABLE.c.source_version_id == str(source_version_id)
            ),
        )
        return source_version_row_to_domain(row) if row is not None else None

    def add(self, source_version: SourceVersion) -> None:
        anchor = postgres_insert(SOURCES_TABLE).values(
            source_id=str(source_version.source_id)
        )
        _execute(
            self._session,
            anchor.on_conflict_do_nothing(index_elements=[SOURCES_TABLE.c.source_id]),
        )
        _execute(
            self._session,
            insert(SOURCE_VERSIONS_TABLE).values(
                source_version_domain_to_row(source_version)
            ),
        )


class SourceEvidencePostgresSourceVersionProcessingRepository:
    """Revisioned Source Version processing Current Truth repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, source_version_id: SourceVersionId) -> SourceVersionProcessing | None:
        row = _fetch_one(
            self._session,
            select(SOURCE_VERSION_PROCESSING_TABLE).where(
                SOURCE_VERSION_PROCESSING_TABLE.c.source_version_id
                == str(source_version_id)
            ),
        )
        return source_version_processing_row_to_domain(row) if row is not None else None

    def add(self, processing: SourceVersionProcessing) -> None:
        _execute(
            self._session,
            insert(SOURCE_VERSION_PROCESSING_TABLE).values(
                source_version_processing_domain_to_row(processing)
            ),
        )

    def save(
        self,
        processing: SourceVersionProcessing,
        *,
        expected_revision: Revision,
    ) -> None:
        values = source_version_processing_domain_to_row(processing)
        values.pop("source_version_id")
        result = _execute(
            self._session,
            update(SOURCE_VERSION_PROCESSING_TABLE)
            .where(
                SOURCE_VERSION_PROCESSING_TABLE.c.source_version_id
                == str(processing.source_version_id)
            )
            .where(
                SOURCE_VERSION_PROCESSING_TABLE.c.revision == expected_revision.value
            )
            .values(values),
        )
        if result.rowcount != 1:
            raise SourceEvidenceRevisionConflictError(
                resource="source_version_processing",
                identity=str(processing.source_version_id),
                expected_revision=expected_revision,
            )


class SourceEvidencePostgresTaskSourceAssociationRepository:
    """Revisioned Task-to-Source membership repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(
        self, source_association_id: SourceAssociationId
    ) -> TaskSourceAssociation | None:
        row = _fetch_one(
            self._session,
            select(TASK_SOURCE_ASSOCIATIONS_TABLE).where(
                TASK_SOURCE_ASSOCIATIONS_TABLE.c.source_association_id
                == str(source_association_id)
            ),
        )
        return task_source_association_row_to_domain(row) if row is not None else None

    def add(self, association: TaskSourceAssociation) -> None:
        _execute(
            self._session,
            insert(TASK_SOURCE_ASSOCIATIONS_TABLE).values(
                task_source_association_domain_to_row(association)
            ),
        )

    def save(
        self,
        association: TaskSourceAssociation,
        *,
        expected_revision: Revision,
    ) -> None:
        values = task_source_association_domain_to_row(association)
        values.pop("source_association_id")
        result = _execute(
            self._session,
            update(TASK_SOURCE_ASSOCIATIONS_TABLE)
            .where(
                TASK_SOURCE_ASSOCIATIONS_TABLE.c.source_association_id
                == str(association.source_association_id)
            )
            .where(TASK_SOURCE_ASSOCIATIONS_TABLE.c.revision == expected_revision.value)
            .values(values),
        )
        if result.rowcount != 1:
            raise SourceEvidenceRevisionConflictError(
                resource="task_source_association",
                identity=str(association.source_association_id),
                expected_revision=expected_revision,
            )


__all__ = [
    "SourceEvidencePostgresSourceVersionRepository",
    "SourceEvidencePostgresSourceVersionProcessingRepository",
    "SourceEvidencePostgresTaskSourceAssociationRepository",
]
