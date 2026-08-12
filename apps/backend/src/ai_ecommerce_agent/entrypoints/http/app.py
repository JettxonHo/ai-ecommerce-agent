"""FastAPI application factory for the transport-only HTTP foundation."""

from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from ai_ecommerce_agent.entrypoints.http.config import FixedWorkspaceHttpConfig
from ai_ecommerce_agent.entrypoints.http.middleware import FixedWorkspaceMiddleware
from ai_ecommerce_agent.entrypoints.http.problems import (
    not_found_problem,
    request_validation_problem,
    unhandled_problem,
)
from ai_ecommerce_agent.entrypoints.http.task_routes import register_task_routes


def create_http_application(*, config: FixedWorkspaceHttpConfig) -> FastAPI:
    """Build a side-effect-free FastAPI application for one fixed workspace."""

    if type(config) is not FixedWorkspaceHttpConfig:
        raise TypeError("config must be a FixedWorkspaceHttpConfig")

    application = FastAPI(
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    application.add_middleware(
        FixedWorkspaceMiddleware,
        workspace_id=config.workspace_id,
        workbench_origin=config.workbench_origin,
    )
    application.add_exception_handler(
        RequestValidationError,
        request_validation_problem,
    )
    application.add_exception_handler(
        404,
        not_found_problem,
    )
    application.add_exception_handler(Exception, unhandled_problem)
    return application


def create_task_http_application(
    *,
    config: FixedWorkspaceHttpConfig,
    task_application: Any,
    primary_input_application: Any,
    result_application: Any | None = None,
    pipeline_coordinator: Any | None = None,
) -> FastAPI:
    """Build the foundation and register the consumed Task/input routes."""

    application = create_http_application(config=config)
    register_task_routes(
        application,
        task_application=task_application,
        primary_input_application=primary_input_application,
        result_application=result_application,
        pipeline_coordinator=pipeline_coordinator,
    )
    return application


__all__ = ("create_http_application", "create_task_http_application")
