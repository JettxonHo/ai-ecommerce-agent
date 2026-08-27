"""Explicit composition root for Task-owned Needs Input persistence."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from ai_ecommerce_agent.modules.needs_input.application.protocols import (
    NeedsInputApplication,
)
from ai_ecommerce_agent.modules.needs_input.application.services import (
    NeedsInputApplicationService,
)
from ai_ecommerce_agent.modules.needs_input.infrastructure.uow import (
    NeedsInputPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)


@dataclass(frozen=True, slots=True)
class NeedsInputPostgresComposition:
    """Process-lifetime engine and Needs Input application service."""

    engine: Engine
    uow_factory: NeedsInputPostgresUnitOfWorkFactory
    application: NeedsInputApplication

    def close(self) -> None:
        self.engine.dispose()


def compose_needs_input_postgres(
    config: PostgresEngineConfig, *, schema: str = "public"
) -> NeedsInputPostgresComposition:
    """Build the adapter graph without reading process configuration."""

    engine = create_postgres_engine(config)
    uow_factory = NeedsInputPostgresUnitOfWorkFactory.from_engine(engine, schema=schema)
    return NeedsInputPostgresComposition(
        engine=engine,
        uow_factory=uow_factory,
        application=NeedsInputApplicationService(uow_factory),
    )


__all__ = [
    "NeedsInputPostgresComposition",
    "compose_needs_input_postgres",
]
