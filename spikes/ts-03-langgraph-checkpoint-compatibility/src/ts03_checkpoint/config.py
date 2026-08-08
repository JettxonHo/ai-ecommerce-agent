"""Connection configuration for the dedicated local Checkpoint database.

The defaults intentionally mirror ``compose.yaml``.  A caller may provide a
complete URI through ``TS03_CHECKPOINT_DATABASE_URL`` so that this disposable
slice can run against an operator-provided local instance without touching
shared repository configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = "55432"
DEFAULT_CHECKPOINT_DATABASE = "ecommerce_checkpoint"
DEFAULT_CHECKPOINT_ROLE = "mvp0_checkpoint"
DEFAULT_CHECKPOINT_PASSWORD = "mvp0_checkpoint_local_only"
DEFAULT_BUSINESS_DATABASE = "ecommerce_business"
DEFAULT_BUSINESS_ROLE = "mvp0_business"
DEFAULT_BUSINESS_PASSWORD = "mvp0_business_local_only"


@dataclass(frozen=True, slots=True)
class DatabaseConnection:
    """A named database connection without exposing its password in reprs."""

    uri: str = field(repr=False)
    database: str
    role: str


def _component(name: str, default: str) -> str:
    value = os.environ.get(name, default)
    if not value:
        raise ValueError(f"{name} must not be empty")
    return value


def checkpoint_connection() -> DatabaseConnection:
    """Return the isolated Checkpoint DB connection selected for this slice."""

    explicit = os.environ.get("TS03_CHECKPOINT_DATABASE_URL")
    database = _component("MVP0_CHECKPOINT_DB", DEFAULT_CHECKPOINT_DATABASE)
    role = _component("MVP0_CHECKPOINT_ROLE", DEFAULT_CHECKPOINT_ROLE)
    if explicit:
        return DatabaseConnection(uri=explicit, database=database, role=role)
    password = _component("MVP0_CHECKPOINT_PASSWORD", DEFAULT_CHECKPOINT_PASSWORD)
    host = _component("MVP0_POSTGRES_HOST", DEFAULT_HOST)
    port = _component("MVP0_POSTGRES_PORT", DEFAULT_PORT)
    return DatabaseConnection(
        uri=f"postgresql://{role}:{password}@{host}:{port}/{database}?sslmode=disable",
        database=database,
        role=role,
    )


def business_connection() -> DatabaseConnection:
    """Return the Business DB connection used only for role/database evidence."""

    explicit = os.environ.get("TS03_BUSINESS_DATABASE_URL")
    database = _component("MVP0_BUSINESS_DB", DEFAULT_BUSINESS_DATABASE)
    role = _component("MVP0_BUSINESS_ROLE", DEFAULT_BUSINESS_ROLE)
    if explicit:
        return DatabaseConnection(uri=explicit, database=database, role=role)
    password = _component("MVP0_BUSINESS_PASSWORD", DEFAULT_BUSINESS_PASSWORD)
    host = _component("MVP0_POSTGRES_HOST", DEFAULT_HOST)
    port = _component("MVP0_POSTGRES_PORT", DEFAULT_PORT)
    return DatabaseConnection(
        uri=f"postgresql://{role}:{password}@{host}:{port}/{database}?sslmode=disable",
        database=database,
        role=role,
    )
