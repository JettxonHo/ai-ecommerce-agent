"""Explicit composition root for the Task Management PostgreSQL adapter."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from ai_ecommerce_agent.modules.task_management.infrastructure.uow import (
    TaskManagementPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)


@dataclass(frozen=True, slots=True)
class TaskManagementPostgresComposition:
    """Process-lifetime engine and per-command Task Management factory."""

    engine: Engine
    uow_factory: TaskManagementPostgresUnitOfWorkFactory

    def close(self) -> None:
        """Dispose the process-lifetime engine at application shutdown."""

        self.engine.dispose()


def compose_task_management_postgres(
    config: PostgresEngineConfig, *, schema: str = "public"
) -> TaskManagementPostgresComposition:
    """Build the adapter graph without reading environment or connecting."""

    engine = create_postgres_engine(config)
    return TaskManagementPostgresComposition(
        engine=engine,
        uow_factory=TaskManagementPostgresUnitOfWorkFactory.from_engine(
            engine, schema=schema
        ),
    )


__all__ = [
    "TaskManagementPostgresComposition",
    "compose_task_management_postgres",
]
