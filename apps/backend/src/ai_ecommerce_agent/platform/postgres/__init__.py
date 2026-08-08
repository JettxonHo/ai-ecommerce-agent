"""Synchronous PostgreSQL adapter foundation.

The package exports engine and UoW factory construction. SQLAlchemy ``Session``
objects intentionally remain private to this platform package and are not part
of any application-facing API.
"""

from .config import PostgresEngineConfig
from .engine import (
    create_postgres_engine,
)
from .uow import PostgresUnitOfWorkFactory

__all__ = [
    "PostgresEngineConfig",
    "PostgresUnitOfWorkFactory",
    "create_postgres_engine",
]
