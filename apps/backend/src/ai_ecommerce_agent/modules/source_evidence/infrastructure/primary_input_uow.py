"""One-shot PostgreSQL Unit of Work for Task primary input."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ai_ecommerce_agent.platform.postgres.uow import PostgresUnitOfWork

from ..application.primary_input_errors import PrimaryInputPersistenceError
from ..application.primary_input_ports import (
    PrimaryInputRepositoryPort,
    PrimaryInputUnitOfWork,
)
from .primary_input_repository import PrimaryInputPostgresRepository
from .tables import primary_input_schema_translate_map

SessionFactory = Callable[[], Session]


class PrimaryInputPostgresUnitOfWork(PostgresUnitOfWork):
    """A disposable UoW exposing only the primary-input repository."""

    def __init__(self, session_factory: SessionFactory) -> None:
        session = session_factory()
        super().__init__(lambda: session)
        self._primary_inputs = PrimaryInputPostgresRepository(session)

    def __enter__(self) -> Self:
        try:
            super().__enter__()
        except SQLAlchemyError as error:
            raise PrimaryInputPersistenceError() from error
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
            raise PrimaryInputPersistenceError() from error

    def commit(self) -> None:
        try:
            super().commit()
        except SQLAlchemyError as error:
            raise PrimaryInputPersistenceError() from error

    @property
    def primary_inputs(self) -> PrimaryInputRepositoryPort:
        return self._primary_inputs


class PrimaryInputPostgresUnitOfWorkFactory:
    """Factory creating fresh sessions mapped to the Business schema."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @classmethod
    def from_engine(
        cls, engine: Engine, *, schema: str = "public"
    ) -> PrimaryInputPostgresUnitOfWorkFactory:
        mapped_engine = engine.execution_options(
            schema_translate_map=primary_input_schema_translate_map(schema)
        )
        factory: sessionmaker[Session] = sessionmaker(
            bind=mapped_engine,
            class_=Session,
            expire_on_commit=False,
        )
        return cls(factory)

    def __call__(self) -> PrimaryInputUnitOfWork:
        return PrimaryInputPostgresUnitOfWork(self._session_factory)


__all__ = [
    "PrimaryInputPostgresUnitOfWork",
    "PrimaryInputPostgresUnitOfWorkFactory",
]
