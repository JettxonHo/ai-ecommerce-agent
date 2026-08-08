"""PostgreSQL-only fixtures with dedicated-schema cleanup."""

from collections.abc import Generator

import pytest
from sqlalchemy import text

from ts01_compatibility.harness import (
    PostgresCompatibilityHarness,
    create_database_engine,
    database_url_from_environment,
)
from ts01_compatibility.migration import run_migration
from ts01_compatibility.schema import SCHEMA_NAME


@pytest.fixture()
def harness() -> Generator[PostgresCompatibilityHarness]:
    database_url = database_url_from_environment()
    # This is the only destructive operation in the suite and is scoped to the
    # test-only schema. It makes every test start from a genuine fresh head.
    engine = create_database_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA_NAME}" CASCADE'))
    engine.dispose()

    run_migration(database_url, "head")
    engine = create_database_engine(database_url)
    fixture_harness = PostgresCompatibilityHarness(engine)
    fixture_harness.clear_fixture_rows()
    try:
        yield fixture_harness
    finally:
        fixture_harness.clear_fixture_rows()
        engine.dispose()
        run_migration(database_url, "base")
        cleanup_engine = create_database_engine(database_url)
        with cleanup_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{SCHEMA_NAME}" CASCADE'))
        cleanup_engine.dispose()
