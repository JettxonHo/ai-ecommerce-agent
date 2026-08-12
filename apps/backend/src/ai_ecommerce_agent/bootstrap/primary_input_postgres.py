"""Explicit composition root for Task primary-input PostgreSQL persistence."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from ai_ecommerce_agent.modules.source_evidence.application.primary_input_protocols import (  # noqa: E501
    PrimaryInputApplication,
)
from ai_ecommerce_agent.modules.source_evidence.application.primary_input_services import (  # noqa: E501
    PrimaryInputApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.primary_input_uow import (  # noqa: E501
    PrimaryInputPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)


@dataclass(frozen=True, slots=True)
class PrimaryInputPostgresComposition:
    """Process-lifetime engine and primary-input application service."""

    engine: Engine
    uow_factory: PrimaryInputPostgresUnitOfWorkFactory
    application: PrimaryInputApplication

    def close(self) -> None:
        """Dispose the process-lifetime engine."""

        self.engine.dispose()


def compose_primary_input_postgres(
    config: PostgresEngineConfig, *, schema: str = "public"
) -> PrimaryInputPostgresComposition:
    """Build the primary-input adapter graph without environment or I/O."""

    engine = create_postgres_engine(config)
    uow_factory = PrimaryInputPostgresUnitOfWorkFactory.from_engine(
        engine, schema=schema
    )
    return PrimaryInputPostgresComposition(
        engine=engine,
        uow_factory=uow_factory,
        application=PrimaryInputApplicationService(uow_factory),
    )


__all__ = [
    "PrimaryInputPostgresComposition",
    "compose_primary_input_postgres",
]
