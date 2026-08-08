"""Long-lived synchronous SQLAlchemy/Psycopg engine resources."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url

from .config import PostgresEngineConfig


def _validate_psycopg_url(database_url: str) -> None:
    """Reject unsupported/async database dialects before engine creation."""

    parsed = make_url(database_url)
    if parsed.drivername != "postgresql+psycopg":
        raise ValueError(
            "MVP PostgreSQL adapter requires the synchronous postgresql+psycopg dialect"
        )


def create_postgres_engine(config: PostgresEngineConfig) -> Engine:
    """Create the process-lifetime sync PostgreSQL engine.

    Engine construction is explicit and side-effect free with respect to the
    database: SQLAlchemy opens a connection only when a caller checks one out.
    The caller (normally Bootstrap) owns disposal at process shutdown.
    """

    _validate_psycopg_url(config.database_url)
    return create_engine(
        config.database_url,
        echo=config.echo,
        pool_pre_ping=config.pool_pre_ping,
        pool_recycle=config.pool_recycle,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
    )


__all__ = ["create_postgres_engine"]
