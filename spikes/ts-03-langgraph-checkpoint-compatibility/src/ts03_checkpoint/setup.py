"""Explicit, operator-invoked PostgresSaver setup action."""

from __future__ import annotations

from dataclasses import dataclass

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver


@dataclass(frozen=True, slots=True)
class SetupEvidence:
    database: str
    role: str
    migration_version: int


def setup_checkpoint_store(database_url: str) -> SetupEvidence:
    """Run the vendor setup exactly when this explicit action is called."""

    # ``from_conn_string`` is the documented synchronous constructor.  The
    # graph builder never calls this function; setup is a deployment/test step.
    with PostgresSaver.from_conn_string(database_url) as checkpointer:
        checkpointer.setup()
    with psycopg.connect(database_url) as connection:
        row = connection.execute(
            """
            SELECT current_database(),
                   current_user,
                   COALESCE(MAX(v), -1)::int
            FROM checkpoint_migrations
            """
        ).fetchone()
    if row is None:
        raise RuntimeError("PostgresSaver setup did not expose checkpoint migration evidence")
    return SetupEvidence(
        database=str(row[0]),
        role=str(row[1]),
        migration_version=int(row[2]),
    )
