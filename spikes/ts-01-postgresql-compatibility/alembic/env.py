"""Alembic environment for the disposable TS-01 schema."""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool, text

from ts01_compatibility.schema import SCHEMA_NAME, metadata

config = context.config
if config.config_file_name is not None and config.get_section("loggers") is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def _database_url() -> str:
    configured = config.get_main_option("sqlalchemy.url")
    if configured:
        return configured
    return os.environ.get(
        "TS01_DATABASE_URL",
        "postgresql+psycopg://mvp0_business:mvp0_business_local_only@"
        "127.0.0.1:55432/ecommerce_business",
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table="alembic_version",
        version_table_schema=SCHEMA_NAME,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_database_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        # Alembic's version table is intentionally inside the disposable
        # namespace. Keep the namespace across ``downgrade base`` so Alembic
        # can record the base revision; tests drop it during teardown.
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA_NAME}"'))
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table="alembic_version",
            version_table_schema=SCHEMA_NAME,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
