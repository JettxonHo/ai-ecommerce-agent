"""Private composition and operator factory for the deterministic local demo.

The browser-facing HTTP contract remains owned by :mod:`entrypoints.http`.
This module only assembles the already-public PostgreSQL application seams for
the one local Fast Lane process.  Importing it does not inspect process
configuration or construct a database engine; the executable factory receives
its three fixed local values at runtime.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from ipaddress import ip_address
from typing import Any
from urllib.parse import urlsplit

from ai_ecommerce_agent.bootstrap.deterministic_result_postgres import (
    DeterministicResultPostgresComposition,
    compose_deterministic_result_postgres,
)
from ai_ecommerce_agent.bootstrap.primary_input_postgres import (
    PrimaryInputPostgresComposition,
    compose_primary_input_postgres,
)
from ai_ecommerce_agent.bootstrap.task_management_postgres import (
    TaskManagementPostgresComposition,
    compose_task_management_postgres,
)
from ai_ecommerce_agent.entrypoints.http import (
    FixedWorkspaceHttpConfig,
    create_task_http_application,
)
from ai_ecommerce_agent.platform.postgres import PostgresEngineConfig

_DATABASE_ENV = "MVP0_LOCAL_DEMO_DATABASE_URL"
_WORKSPACE_ENV = "MVP0_LOCAL_DEMO_WORKSPACE_ID"
_ORIGIN_ENV = "MVP0_LOCAL_DEMO_WORKBENCH_ORIGIN"


def _validate_local_database_url(value: object) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError("database_url must be a non-empty string")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as error:
        raise ValueError("database_url must be a valid local PostgreSQL URL") from error
    if parsed.scheme != "postgresql+psycopg":
        raise ValueError("database_url must use postgresql+psycopg")
    if (
        parsed.username is None
        or parsed.password is None
        or parsed.hostname is None
        or not parsed.path.strip("/")
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("database_url must include one local database and credentials")
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("database_url must have a valid port")
    if parsed.hostname.lower() == "localhost":
        return
    try:
        address = ip_address(parsed.hostname)
    except ValueError as error:
        raise ValueError("database_url must use a loopback host") from error
    if not address.is_loopback:
        raise ValueError("database_url must use a loopback host")


@dataclass(frozen=True, slots=True)
class LocalDemoConfig:
    """Explicit local-demo values accepted at the executable boundary."""

    database_url: str
    workspace_id: str
    workbench_origin: str

    def __post_init__(self) -> None:
        _validate_local_database_url(self.database_url)
        # Reuse the HTTP adapter's complete fixed-workspace and loopback-origin
        # validation rather than making a second, weaker boundary.
        FixedWorkspaceHttpConfig(self.workspace_id, self.workbench_origin)

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> LocalDemoConfig:
        """Load only the three operator-provided local-demo values.

        This method is intentionally the only environment-reading seam.  In
        particular, it does not inspect provider settings or load a dotenv
        file; the shell command supplies these fixed values explicitly.
        """

        values = os.environ if environment is None else environment
        missing = tuple(
            name
            for name in (_DATABASE_ENV, _WORKSPACE_ENV, _ORIGIN_ENV)
            if not values.get(name, "").strip()
        )
        if missing:
            raise ValueError(
                "local demo configuration is incomplete; provide " + ", ".join(missing)
            )
        return cls(
            database_url=values[_DATABASE_ENV],
            workspace_id=values[_WORKSPACE_ENV],
            workbench_origin=values[_ORIGIN_ENV],
        )


@dataclass(frozen=True, slots=True)
class LocalDemoComposition:
    """The local process graph and its single HTTP application.

    The three existing PostgreSQL compositions own their SQLAlchemy engines.
    Closing this object closes every participant, including after a partial
    construction failure.  ``close`` is idempotent so a server lifespan and an
    outer operator cleanup can safely converge on the same resource fence.
    """

    application: Any
    task: TaskManagementPostgresComposition
    primary_input: PrimaryInputPostgresComposition
    result: DeterministicResultPostgresComposition
    _closed: bool = field(default=False, init=False, compare=False, repr=False)

    def close(self) -> None:
        """Dispose all owned application resources exactly once."""

        if self._closed:
            return
        object.__setattr__(self, "_closed", True)
        first_error: BaseException | None = None
        # Close every participant even if one adapter unexpectedly raises.
        for participant in (self.result, self.primary_input, self.task):
            try:
                participant.close()
            except BaseException as error:  # pragma: no cover - defensive fence
                if first_error is None:
                    first_error = error
        if first_error is not None:
            raise first_error


def _attach_lifespan(application: Any, composition: LocalDemoComposition) -> Any:
    """Attach the composition fence to the host app without a public API edit."""

    @asynccontextmanager
    async def lifespan(_application: Any):
        try:
            yield
        finally:
            composition.close()

    # FastAPI exposes the router lifespan as the supported application
    # lifecycle hook; the HTTP factory itself remains unchanged/public.
    application.router.lifespan_context = lifespan
    return application


def compose_local_demo(config: LocalDemoConfig) -> LocalDemoComposition:
    """Compose the real local Task/input/result/export graph without I/O."""

    if type(config) is not LocalDemoConfig:
        raise TypeError("config must be a LocalDemoConfig")

    postgres_config = PostgresEngineConfig(config.database_url)
    task: TaskManagementPostgresComposition | None = None
    primary_input: PrimaryInputPostgresComposition | None = None
    result: DeterministicResultPostgresComposition | None = None
    try:
        task = compose_task_management_postgres(postgres_config)
        primary_input = compose_primary_input_postgres(postgres_config)
        result = compose_deterministic_result_postgres(postgres_config)
        application = create_task_http_application(
            config=FixedWorkspaceHttpConfig(
                workspace_id=config.workspace_id,
                workbench_origin=config.workbench_origin,
            ),
            task_application=task.application,
            primary_input_application=primary_input.application,
            result_application=result.application,
            pipeline_coordinator=result.coordinator,
            export_application=result.export_application,
        )
        composition = LocalDemoComposition(
            application=application,
            task=task,
            primary_input=primary_input,
            result=result,
        )
        _attach_lifespan(application, composition)
        return composition
    except BaseException:
        # A failed composition must not leak any engines that were already
        # created before a later participant or route failed.
        for participant in (result, primary_input, task):
            if participant is not None:
                participant.close()
        raise


def create_local_demo_application(config: LocalDemoConfig | None = None) -> Any:
    """Uvicorn factory for the fixed local demo.

    Uvicorn calls this function at process startup with no arguments.  Tests
    and other local callers may pass an explicit :class:`LocalDemoConfig`.
    The returned app owns a lifespan fence that closes the composition on
    shutdown; no provider runtime is selected here.
    """

    selected = config if config is not None else LocalDemoConfig.from_environment()
    return compose_local_demo(selected).application


__all__ = (
    "LocalDemoComposition",
    "LocalDemoConfig",
    "compose_local_demo",
    "create_local_demo_application",
)
