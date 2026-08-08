"""Small configuration and dialect-boundary checks for the PostgreSQL adapter."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)

pytestmark = pytest.mark.unit


def test_engine_config_is_validated_without_connecting() -> None:
    """Creating an engine validates configuration but does not open a socket."""

    engine = create_postgres_engine(
        PostgresEngineConfig(
            "postgresql+psycopg://user:password@127.0.0.1:1/example",
            pool_size=1,
            max_overflow=0,
        )
    )
    engine.dispose()


@pytest.mark.parametrize(
    "database_url",
    [
        "sqlite:///not-supported.db",
        "postgresql+psycopg_async://user:password@localhost/example",
    ],
)
def test_engine_rejects_non_sync_postgresql_dialects(database_url: str) -> None:
    """SQLite and asynchronous drivers are outside the MVP acceptance tuple."""

    with pytest.raises(ValueError, match=r"synchronous postgresql\+psycopg"):
        create_postgres_engine(PostgresEngineConfig(database_url))
