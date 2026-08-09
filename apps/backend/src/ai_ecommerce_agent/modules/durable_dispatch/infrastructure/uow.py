"""One-shot PostgreSQL Unit of Work composition for Durable Dispatch."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ai_ecommerce_agent.modules.durable_dispatch.application.errors import (
    DurableDispatchPersistenceError,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.ports import (
    WorkIntentRepositoryPort,
)
from ai_ecommerce_agent.platform.postgres.uow import PostgresUnitOfWork

from .repositories import DurableDispatchPostgresWorkIntentRepository
from .tables import schema_translate_map

SessionFactory = Callable[[], Session]


class DurableDispatchPostgresUnitOfWork(PostgresUnitOfWork):
    """A disposable UoW exposing only the typed Work Intent repository."""

    def __init__(self, session_factory: SessionFactory) -> None:
        session = session_factory()
        super().__init__(lambda: session)
        self._work_intents = DurableDispatchPostgresWorkIntentRepository(session)

    def __enter__(self) -> Self:
        try:
            super().__enter__()
        except SQLAlchemyError as error:
            raise DurableDispatchPersistenceError() from error
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
            raise DurableDispatchPersistenceError() from error

    def commit(self) -> None:
        try:
            super().commit()
        except SQLAlchemyError as error:
            raise DurableDispatchPersistenceError() from error

    def rollback(self) -> None:
        try:
            super().rollback()
        except SQLAlchemyError as error:
            raise DurableDispatchPersistenceError() from error

    def close(self) -> None:
        try:
            super().close()
        except SQLAlchemyError as error:
            raise DurableDispatchPersistenceError() from error

    @property
    def work_intents(self) -> WorkIntentRepositoryPort:
        return self._work_intents


class DurableDispatchPostgresUnitOfWorkFactory:
    """Long-lived factory creating a fresh mapped-session UoW per command."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @classmethod
    def from_engine(
        cls, engine: Engine, *, schema: str = "public"
    ) -> DurableDispatchPostgresUnitOfWorkFactory:
        """Bind logical Durable Dispatch tables to one explicit schema."""

        mapped_engine = engine.execution_options(
            schema_translate_map=schema_translate_map(schema)
        )
        factory: sessionmaker[Session] = sessionmaker(
            bind=mapped_engine,
            class_=Session,
            expire_on_commit=False,
        )
        return cls(factory)

    def __call__(self) -> DurableDispatchPostgresUnitOfWork:
        return DurableDispatchPostgresUnitOfWork(self._session_factory)


__all__ = [
    "DurableDispatchPostgresUnitOfWork",
    "DurableDispatchPostgresUnitOfWorkFactory",
]
