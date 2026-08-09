"""One-shot Source Evidence PostgreSQL Unit of Work composition."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidencePersistenceError,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceVersionProcessingRepositoryPort,
    SourceVersionRepositoryPort,
    TaskSourceAssociationRepositoryPort,
)
from ai_ecommerce_agent.platform.postgres.uow import PostgresUnitOfWork

from .repositories import (
    SourceEvidencePostgresSourceVersionProcessingRepository,
    SourceEvidencePostgresSourceVersionRepository,
    SourceEvidencePostgresTaskSourceAssociationRepository,
)
from .tables import schema_translate_map

SessionFactory = Callable[[], Session]


class SourceEvidencePostgresUnitOfWork(PostgresUnitOfWork):
    """A disposable UoW exposing exactly the three Source repositories."""

    def __init__(self, session_factory: SessionFactory) -> None:
        session = session_factory()
        super().__init__(lambda: session)
        self._source_versions = SourceEvidencePostgresSourceVersionRepository(session)
        self._source_version_processing = (
            SourceEvidencePostgresSourceVersionProcessingRepository(session)
        )
        self._source_associations = (
            SourceEvidencePostgresTaskSourceAssociationRepository(session)
        )

    def __enter__(self) -> Self:
        try:
            super().__enter__()
        except SQLAlchemyError as error:
            raise SourceEvidencePersistenceError() from error
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            super().__exit__(exc_type, exc_value, traceback)
        except SQLAlchemyError as error:
            raise SourceEvidencePersistenceError() from error

    def commit(self) -> None:
        try:
            super().commit()
        except SQLAlchemyError as error:
            raise SourceEvidencePersistenceError() from error

    def rollback(self) -> None:
        try:
            super().rollback()
        except SQLAlchemyError as error:
            raise SourceEvidencePersistenceError() from error

    def close(self) -> None:
        try:
            super().close()
        except SQLAlchemyError as error:
            raise SourceEvidencePersistenceError() from error

    @property
    def source_versions(self) -> SourceVersionRepositoryPort:
        return self._source_versions

    @property
    def source_version_processing(
        self,
    ) -> SourceVersionProcessingRepositoryPort:
        return self._source_version_processing

    @property
    def source_associations(self) -> TaskSourceAssociationRepositoryPort:
        return self._source_associations


class SourceEvidencePostgresUnitOfWorkFactory:
    """Long-lived factory creating one fresh Session/UoW per command."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @classmethod
    def from_engine(
        cls, engine: Engine, *, schema: str = "public"
    ) -> SourceEvidencePostgresUnitOfWorkFactory:
        """Bind logical Source tables to one explicit Business schema."""

        mapped_engine = engine.execution_options(
            schema_translate_map=schema_translate_map(schema)
        )
        factory: sessionmaker[Session] = sessionmaker(
            bind=mapped_engine,
            class_=Session,
            expire_on_commit=False,
        )
        return cls(factory)

    def __call__(self) -> SourceEvidencePostgresUnitOfWork:
        return SourceEvidencePostgresUnitOfWork(self._session_factory)


__all__ = [
    "SourceEvidencePostgresUnitOfWork",
    "SourceEvidencePostgresUnitOfWorkFactory",
]
