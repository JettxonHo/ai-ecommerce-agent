"""Compose the PostgreSQL adapter without reading process configuration.

The caller is responsible for loading and validating configuration before
calling this factory.  Importing this module never reads environment variables
and never connects to PostgreSQL.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    PostgresUnitOfWorkFactory,
    create_postgres_engine,
)


@dataclass(frozen=True, slots=True)
class PostgresComposition:
    """Long-lived engine plus per-command UoW factory."""

    engine: Engine
    uow_factory: PostgresUnitOfWorkFactory

    def close(self) -> None:
        """Dispose the process-lifetime engine at application shutdown."""

        self.engine.dispose()


def compose_postgres(config: PostgresEngineConfig) -> PostgresComposition:
    """Build the engine/sessionmaker/UoW object graph explicitly."""

    engine = create_postgres_engine(config)
    return PostgresComposition(
        engine=engine,
        uow_factory=PostgresUnitOfWorkFactory.from_engine(engine),
    )


__all__ = ["PostgresComposition", "compose_postgres"]
