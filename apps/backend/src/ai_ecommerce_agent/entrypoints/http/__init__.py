"""HTTP adapter facade for the fixed-workspace local transport."""

from ai_ecommerce_agent.entrypoints.http.app import create_http_application
from ai_ecommerce_agent.entrypoints.http.config import FixedWorkspaceHttpConfig
from ai_ecommerce_agent.entrypoints.http.middleware import fixed_workspace_id

__all__ = (
    "FixedWorkspaceHttpConfig",
    "create_http_application",
    "fixed_workspace_id",
)
