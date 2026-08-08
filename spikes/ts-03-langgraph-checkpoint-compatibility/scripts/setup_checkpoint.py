#!/usr/bin/env python3
"""Explicit TS-03 Checkpoint database setup; never imported by the graph."""

from __future__ import annotations

import argparse

from ts03_checkpoint.config import checkpoint_connection
from ts03_checkpoint.setup import setup_checkpoint_store


def main() -> int:
    parser = argparse.ArgumentParser(description="Run explicit PostgresSaver setup for TS-03")
    parser.add_argument(
        "--database-url",
        default=None,
        help="Checkpoint URI; defaults to TS03_CHECKPOINT_DATABASE_URL/compose values",
    )
    args = parser.parse_args()
    connection = checkpoint_connection()
    evidence = setup_checkpoint_store(args.database_url or connection.uri)
    print(
        "Checkpoint setup complete: "
        f"database={evidence.database} role={evidence.role} "
        f"migration_version={evidence.migration_version}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
