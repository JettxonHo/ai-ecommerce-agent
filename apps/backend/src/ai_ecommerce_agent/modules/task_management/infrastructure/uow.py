"""Task Management Unit of Work composition over the shared Postgres lifecycle."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ai_ecommerce_agent.modules.task_management.application.errors import (
    TaskManagementPersistenceError,
)
from ai_ecommerce_agent.modules.task_management.application.ports import (
    RunRepositoryPort,
    StageRepositoryPort,
    TaskRepositoryPort,
)
from ai_ecommerce_agent.platform.postgres.uow import PostgresUnitOfWork

from .repositories import (
    TaskManagementPostgresRunRepository,
    TaskManagementPostgresStageRepository,
    TaskManagementPostgresTaskRepository,
)
from .tables import schema_translate_map

SessionFactory = Callable[[], Session]


class TaskManagementPostgresUnitOfWork(PostgresUnitOfWork):
    """One-shot UoW exposing only the three typed module repositories."""

    def __init__(self, session_factory: SessionFactory) -> None:
        session = session_factory()
        super().__init__(lambda: session)
        self._tasks = TaskManagementPostgresTaskRepository(session)
        self._runs = TaskManagementPostgresRunRepository(session)
        self._stages = TaskManagementPostgresStageRepository(session)

    def __enter__(self) -> Self:
        try:
            super().__enter__()
        except SQLAlchemyError as error:
            raise TaskManagementPersistenceError() from error
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Preserve one-shot cleanup while translating cleanup SQL errors."""

        try:
            super().__exit__(exc_type, exc_value, traceback)
        except SQLAlchemyError as error:
            raise TaskManagementPersistenceError() from error

    def commit(self) -> None:
        """Commit once, translating SQLAlchemy failures after cleanup."""

        try:
            super().commit()
        except SQLAlchemyError as error:
            raise TaskManagementPersistenceError() from error

    @property
    def tasks(self) -> TaskRepositoryPort:
        return self._tasks

    @property
    def runs(self) -> RunRepositoryPort:
        return self._runs

    @property
    def stages(self) -> StageRepositoryPort:
        return self._stages


class TaskManagementPostgresUnitOfWorkFactory:
    """Long-lived factory creating a fresh mapped-session UoW per command."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @classmethod
    def from_engine(
        cls, engine: Engine, *, schema: str = "public"
    ) -> TaskManagementPostgresUnitOfWorkFactory:
        """Bind the logical table token to an explicit deployment schema."""

        mapped_engine = engine.execution_options(
            schema_translate_map=schema_translate_map(schema)
        )
        factory: sessionmaker[Session] = sessionmaker(
            bind=mapped_engine, class_=Session, expire_on_commit=False
        )
        return cls(factory)

    def __call__(self) -> TaskManagementPostgresUnitOfWork:
        return TaskManagementPostgresUnitOfWork(self._session_factory)


__all__ = [
    "TaskManagementPostgresUnitOfWork",
    "TaskManagementPostgresUnitOfWorkFactory",
]
