"""Explicit Alembic environment for the production Business lineage.

Importing the application package does not import this module.  Alembic loads
it only while an explicit ``alembic`` command runs; only then is the configured
URL read and a PostgreSQL connection opened.
"""

from __future__ import annotations

import os
import re
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import MetaData, create_engine, pool
from sqlalchemy.engine import make_url

from ai_ecommerce_agent.platform.postgres.migration import business_schema_scope

config = context.config

if config.config_file_name is not None and config.get_section("loggers") is not None:
    fileConfig(config.config_file_name)


# PostgreSQL's Business schema and Alembic version identity are deliberately
# separate from domain_version_id/version_number/revision and checkpoint
# schema/version identities.  No ORM model is present in this baseline; later
# modules add their tables to this metadata through the same single lineage.
target_metadata = MetaData()

_SAFE_SCHEMA = re.compile(r"^[a-z_][a-z0-9_]*$")


def _setting(name: str, *, default: str = "") -> str:
    """Read an explicit Alembic setting without touching process state."""

    value = (config.get_main_option(name) or "").strip()
    return value if value else default


def _business_schema() -> str:
    schema = _setting("business_schema", default="public")
    if not _SAFE_SCHEMA.fullmatch(schema):
        raise ValueError(
            "business_schema must be a lowercase PostgreSQL identifier "
            "matching [a-z_][a-z0-9_]*"
        )
    return schema


def _version_schema(business_schema: str) -> str:
    configured = _setting("version_table_schema", default=business_schema)
    if not _SAFE_SCHEMA.fullmatch(configured):
        raise ValueError(
            "version_table_schema must be a lowercase PostgreSQL identifier "
            "matching [a-z_][a-z0-9_]*"
        )
    if configured != business_schema:
        raise ValueError(
            "Business Alembic version_table_schema must equal business_schema"
        )
    return configured


def _database_url() -> str:
    """Resolve an explicit URL only during an Alembic command."""

    configured = _setting("sqlalchemy.url")
    url = configured or os.environ.get("MVP0_BUSINESS_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "Business migration requires sqlalchemy.url or "
            "MVP0_BUSINESS_DATABASE_URL; no database was selected"
        )
    parsed = make_url(url)
    if parsed.drivername != "postgresql+psycopg":
        raise ValueError(
            "Business Alembic requires the synchronous postgresql+psycopg dialect"
        )
    return url


def _include_name(
    name: str | None,
    type_: str,
    parent_names: dict[str, str | None],
) -> bool:
    """Keep autogenerate inside the explicitly selected Business schema."""

    business_schema = _business_schema()
    allowed_schemas = business_schema_scope(business_schema)
    if type_ == "schema":
        # Alembic represents the database default schema as ``None`` for some
        # dialect operations and as its concrete name for others.
        return name in allowed_schemas
    if type_ == "table":
        schema = parent_names.get("schema")
        return schema in allowed_schemas
    return True


def _include_object(
    object_: Any,
    name: str,
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    """Never infer drops for unmanaged or out-of-scope database objects."""

    allowed_schemas = business_schema_scope(_business_schema())
    schema = getattr(object_, "schema", None)
    if type_ == "table" and schema not in allowed_schemas:
        return False
    # A reflected table absent from Business metadata is unmanaged.  Excluding
    # it prevents Alembic autogenerate from proposing a destructive drop for an
    # out-of-line, test, or manually managed object.
    if type_ == "table" and reflected and compare_to is None:
        return False
    return True


def _migration_options(version_schema: str) -> dict[str, Any]:
    return {
        "target_metadata": target_metadata,
        "include_schemas": True,
        "include_name": _include_name,
        "include_object": _include_object,
        "compare_type": True,
        "compare_server_default": False,
        "version_table": _setting("version_table", default="alembic_version"),
        "version_table_schema": version_schema,
        "transaction_per_migration": True,
        # Keep the Business schema explicit even when PostgreSQL's search path
        # is altered by a caller or a vendor setup.
        "dialect_opts": {"paramstyle": "named"},
    }


def run_migrations_offline() -> None:
    """Render SQL for review without opening a database connection."""

    business_schema = _business_schema()
    version_schema = _version_schema(business_schema)
    context.configure(
        url=_database_url(),
        literal_binds=True,
        **_migration_options(version_schema),
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run an explicitly requested migration against synchronous PostgreSQL."""

    business_schema = _business_schema()
    version_schema = _version_schema(business_schema)
    connectable = create_engine(_database_url(), poolclass=pool.NullPool)
    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                **_migration_options(version_schema),
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
