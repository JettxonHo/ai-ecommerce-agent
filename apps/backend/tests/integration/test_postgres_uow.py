"""Real PostgreSQL acceptance for the MVP0-007 UoW adapter foundation."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, text
from sqlalchemy import event as sqlalchemy_event
from sqlalchemy.engine import URL

from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    PostgresUnitOfWorkFactory,
    create_postgres_engine,
)

pytestmark = [pytest.mark.integration, pytest.mark.live]

if os.environ.get("MVP0_RUN_POSTGRES_INTEGRATION") != "1":
    pytest.skip(
        "set MVP0_RUN_POSTGRES_INTEGRATION=1 for the opt-in real PostgreSQL suite",
        allow_module_level=True,
    )


SCHEMA = "mvp0_007_uow_test"
TABLE = f'"{SCHEMA}"."uow_probe"'
DEFAULT_URL = URL.create(
    "postgresql+psycopg",
    username="mvp0_business",
    password="mvp0_business_local_only",
    host="127.0.0.1",
    port=55432,
    database="ecommerce_business",
).render_as_string(hide_password=False)


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    """Create and remove only the adapter test schema."""

    database_url = os.environ.get("MVP0_DATABASE_URL", DEFAULT_URL)
    engine = create_postgres_engine(
        PostgresEngineConfig(
            database_url=database_url,
            pool_size=1,
            max_overflow=0,
            pool_timeout=2,
        )
    )
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{SCHEMA}"'))
        connection.execute(
            text(f"CREATE TABLE {TABLE} (id integer PRIMARY KEY, value text NOT NULL)")
        )
    try:
        yield engine
    finally:
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{SCHEMA}" CASCADE'))
        engine.dispose()


def _uow_factory(engine: Engine) -> PostgresUnitOfWorkFactory:
    """Build a fresh UoW factory from a long-lived engine."""

    return PostgresUnitOfWorkFactory.from_engine(engine)


def _count_rows(engine: Engine) -> int:
    with engine.connect() as connection:
        return int(connection.scalar(text(f"SELECT count(*) FROM {TABLE}")))


def test_commit_visibility_and_uncommitted_rollback(postgres_engine: Engine) -> None:
    """Commit is visible to a new connection; an uncommitted scope is not."""

    factory = _uow_factory(postgres_engine)
    with factory() as uow:
        uow._session.execute(  # pyright: ignore[reportPrivateUsage]  # adapter test owns private Session
            text(f"INSERT INTO {TABLE} (id, value) VALUES (1, 'committed')")
        )
        uow.commit()

    assert _count_rows(postgres_engine) == 1
    with factory() as uow:
        uow._session.execute(  # pyright: ignore[reportPrivateUsage]  # adapter test owns private Session
            text(f"INSERT INTO {TABLE} (id, value) VALUES (2, 'rolled back')")
        )

    assert _count_rows(postgres_engine) == 1


def test_each_uow_gets_fresh_session_and_connection_is_returned(
    postgres_engine: Engine,
) -> None:
    """A closed UoW releases its connection and the next UoW is independent."""

    checkins = 0

    def on_checkin(*_: object) -> None:
        nonlocal checkins
        checkins += 1

    sqlalchemy_event.listen(postgres_engine, "checkin", on_checkin)
    try:
        factory = _uow_factory(postgres_engine)
        first = factory()
        second = factory()
        assert first._session is not second._session  # pyright: ignore[reportPrivateUsage]

        with first as uow:
            uow._session.execute(  # pyright: ignore[reportPrivateUsage]
                text(f"SELECT 1 FROM {TABLE}")
            )
            uow.commit()
        after_first = checkins
        with second as uow:
            uow._session.execute(  # pyright: ignore[reportPrivateUsage]
                text(f"SELECT 1 FROM {TABLE}")
            )
            uow.commit()

        assert after_first >= 1
        assert checkins > after_first
    finally:
        sqlalchemy_event.remove(postgres_engine, "checkin", on_checkin)
