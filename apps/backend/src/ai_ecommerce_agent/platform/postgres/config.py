"""Validated PostgreSQL adapter configuration values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True, slots=True)
class PostgresEngineConfig:
    """Immutable, adapter-scoped settings for a sync PostgreSQL engine.

    Configuration is supplied by the composition root.  This value never
    reads environment variables or opens a connection during import.
    """

    database_url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: float = 30.0
    pool_recycle: int = -1
    pool_pre_ping: bool = True
    echo: bool = False

    def __post_init__(self) -> None:
        database_url = cast(object, self.database_url)
        if not isinstance(database_url, str) or not database_url.strip():
            raise ValueError("database_url must be a non-empty string")
        pool_size = cast(object, self.pool_size)
        if not isinstance(pool_size, int) or isinstance(pool_size, bool):
            raise TypeError("pool_size must be an integer")
        if self.pool_size < 1:
            raise ValueError("pool_size must be positive")
        max_overflow = cast(object, self.max_overflow)
        if not isinstance(max_overflow, int) or isinstance(max_overflow, bool):
            raise TypeError("max_overflow must be an integer")
        if self.max_overflow < 0:
            raise ValueError("max_overflow must be non-negative")
        pool_timeout = cast(object, self.pool_timeout)
        if not isinstance(pool_timeout, (int, float)) or isinstance(pool_timeout, bool):
            raise TypeError("pool_timeout must be numeric")
        if self.pool_timeout <= 0:
            raise ValueError("pool_timeout must be positive")
        pool_recycle = cast(object, self.pool_recycle)
        if not isinstance(pool_recycle, int) or isinstance(pool_recycle, bool):
            raise TypeError("pool_recycle must be an integer")
        pool_pre_ping = cast(object, self.pool_pre_ping)
        if not isinstance(pool_pre_ping, bool):
            raise TypeError("pool_pre_ping must be a boolean")
        echo = cast(object, self.echo)
        if not isinstance(echo, bool):
            raise TypeError("echo must be a boolean")


__all__ = ["PostgresEngineConfig"]
