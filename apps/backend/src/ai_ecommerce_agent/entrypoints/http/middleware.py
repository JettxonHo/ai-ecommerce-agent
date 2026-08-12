"""ASGI middleware for server-owned workspace scope and write Origin checks."""

from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from ai_ecommerce_agent.entrypoints.http.problems import malformed_origin_problem

_STATE_CHANGING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class FixedWorkspaceMiddleware:
    """Inject one configured workspace and guard browser-originated writes."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        workspace_id: str,
        workbench_origin: str,
    ) -> None:
        self._app = app
        self._workspace_id = workspace_id
        self._workbench_origin = workbench_origin

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        state = scope.setdefault("state", {})
        state["workspace_id"] = self._workspace_id

        if scope.get("method") in _STATE_CHANGING_METHODS:
            origins = Headers(scope=scope).getlist("origin")
            if origins and (len(origins) != 1 or origins[0] != self._workbench_origin):
                response = malformed_origin_problem(Request(scope, receive=receive))
                await response(scope, receive, send)
                return

        await self._app(scope, receive, send)


def fixed_workspace_id(request: Request) -> str:
    """Read the server-injected workspace identity from one HTTP request."""

    workspace_id = getattr(request.state, "workspace_id", None)
    if type(workspace_id) is not str or not workspace_id:
        raise RuntimeError("server workspace identity is unavailable")
    return workspace_id


__all__ = ("FixedWorkspaceMiddleware", "fixed_workspace_id")
