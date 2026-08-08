"""Programmatic Alembic entry points used by the bounded tests."""

from pathlib import Path

from alembic import command
from alembic.config import Config

SPIKE_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = SPIKE_ROOT / "alembic.ini"


def run_migration(database_url: str, revision: str) -> None:
    """Run one Alembic revision against the caller-provided PostgreSQL URL."""

    config = Config(str(ALEMBIC_INI))
    # ConfigParser interpolation treats percent signs specially; doubling them
    # preserves valid URL-encoded credentials when Alembic reads the setting.
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    if revision == "head":
        command.upgrade(config, "head")
    elif revision == "base":
        command.downgrade(config, "base")
    else:
        raise ValueError(f"unsupported TS-01 migration target: {revision}")
