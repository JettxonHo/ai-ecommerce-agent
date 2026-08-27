"""One-shot PostgreSQL Unit of Work for Needs Input."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ai_ecommerce_agent.platform.postgres.uow import PostgresUnitOfWork

from ..application.errors import NeedsInputPersistenceError
from ..application.ports import NeedsInputRequestRepository
from .repositories import NeedsInputPostgresRequestRepository
from .tables import schema_translate_map

SessionFactory = Callable[[], Session]


class NeedsInputPostgresUnitOfWork(PostgresUnitOfWork):
    """Expose only the typed request repository to application code."""

    def __init__(self, session_factory: SessionFactory) -> None:
        session = session_factory()
        super().__init__(lambda: session)
        self._needs_input_requests = NeedsInputPostgresRequestRepository(session)

    def __enter__(self) -> Self:
        try:
            super().__enter__()
        except SQLAlchemyError as error:
            raise NeedsInputPersistenceError() from error
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
            raise NeedsInputPersistenceError() from error

    def commit(self) -> None:
        try:
            super().commit()
        except SQLAlchemyError as error:
            raise NeedsInputPersistenceError() from error

    @property
    def needs_input_requests(self) -> NeedsInputRequestRepository:
        return self._needs_input_requests


class NeedsInputPostgresUnitOfWorkFactory:
    """Create fresh mapped-session UoWs against one Business schema."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @classmethod
    def from_engine(
        cls, engine: Engine, *, schema: str = "public"
    ) -> NeedsInputPostgresUnitOfWorkFactory:
        mapped_engine = engine.execution_options(
            schema_translate_map=schema_translate_map(schema)
        )
        factory: sessionmaker[Session] = sessionmaker(
            bind=mapped_engine, class_=Session, expire_on_commit=False
        )
        return cls(factory)

    def __call__(self) -> NeedsInputPostgresUnitOfWork:
        return NeedsInputPostgresUnitOfWork(self._session_factory)


__all__ = [
    "NeedsInputPostgresUnitOfWork",
    "NeedsInputPostgresUnitOfWorkFactory",
]
