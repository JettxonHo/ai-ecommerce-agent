"""Explicit composition root for the Durable Dispatch PostgreSQL adapter."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine

from ai_ecommerce_agent.modules.durable_dispatch.application.control_protocols import (
    DurableDispatchControlApplication,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.control_services import (
    DurableDispatchControlApplicationService,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_protocols import (
    DurableDispatchLeaseApplication,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_services import (
    DurableDispatchLeaseApplicationService,
)
from ai_ecommerce_agent.modules.durable_dispatch.infrastructure.uow import (
    DurableDispatchPostgresUnitOfWorkFactory,
)
from ai_ecommerce_agent.platform.postgres import (
    PostgresEngineConfig,
    create_postgres_engine,
)


@dataclass(frozen=True, slots=True)
class DurableDispatchPostgresComposition:
    """Process-lifetime engine and per-command lease application graph."""

    engine: Engine
    uow_factory: DurableDispatchPostgresUnitOfWorkFactory
    lease_application: DurableDispatchLeaseApplication
    control_application: DurableDispatchControlApplication

    def close(self) -> None:
        """Dispose the process-lifetime engine at application shutdown."""

        self.engine.dispose()


def compose_durable_dispatch_postgres(
    config: PostgresEngineConfig, *, schema: str = "public"
) -> DurableDispatchPostgresComposition:
    """Build the Durable Dispatch graph without environment or database I/O."""

    engine = create_postgres_engine(config)
    uow_factory = DurableDispatchPostgresUnitOfWorkFactory.from_engine(
        engine, schema=schema
    )
    return DurableDispatchPostgresComposition(
        engine=engine,
        uow_factory=uow_factory,
        lease_application=DurableDispatchLeaseApplicationService(uow_factory),
        control_application=DurableDispatchControlApplicationService(uow_factory),
    )


__all__ = [
    "DurableDispatchPostgresComposition",
    "compose_durable_dispatch_postgres",
]
