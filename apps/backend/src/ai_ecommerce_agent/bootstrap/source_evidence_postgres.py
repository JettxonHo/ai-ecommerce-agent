"""Explicit composition root for Source Evidence PostgreSQL processing."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from ai_ecommerce_agent.modules.source_evidence.application import (
    association_protocols,
    association_services,
)
from ai_ecommerce_agent.modules.source_evidence.application.protocols import (
    SourceEvidenceApplication,
)
from ai_ecommerce_agent.modules.source_evidence.application.query_protocols import (
    SourceEvidenceQueryApplication,
)
from ai_ecommerce_agent.modules.source_evidence.application.query_services import (
    SourceEvidenceQueryApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.application.services import (
    SourceEvidenceApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.infrastructure.uow import (
    SourceEvidencePostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)


@dataclass(frozen=True, slots=True)
class SourceEvidencePostgresComposition:
    """Process-lifetime engine and per-command Source Evidence factory."""

    engine: Engine
    uow_factory: SourceEvidencePostgresUnitOfWorkFactory
    application: SourceEvidenceApplication
    association_application: association_protocols.SourceAssociationApplication
    query_application: SourceEvidenceQueryApplication

    def close(self) -> None:
        """Dispose the process-lifetime engine at application shutdown."""

        self.engine.dispose()


def compose_source_evidence_postgres(
    config: PostgresEngineConfig, *, schema: str = "public"
) -> SourceEvidencePostgresComposition:
    """Build the Source adapter graph without environment or database I/O."""

    engine = create_postgres_engine(config)
    uow_factory = SourceEvidencePostgresUnitOfWorkFactory.from_engine(
        engine, schema=schema
    )
    return SourceEvidencePostgresComposition(
        engine=engine,
        uow_factory=uow_factory,
        application=SourceEvidenceApplicationService(uow_factory),
        association_application=association_services.SourceAssociationApplicationService(
            uow_factory
        ),
        query_application=SourceEvidenceQueryApplicationService(uow_factory),
    )


__all__ = [
    "SourceEvidencePostgresComposition",
    "compose_source_evidence_postgres",
]
