"""Pure, validated configuration for the local fixed-workspace HTTP adapter."""

from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import urlsplit


def _validate_workspace_id(value: object) -> None:
    if type(value) is not str:
        raise TypeError("workspace_id must be an exact string")
    if not value.strip():
        raise ValueError("workspace_id must not be blank")


def _validate_workbench_origin(value: object) -> None:
    if type(value) is not str:
        raise TypeError("workbench_origin must be an exact string")
    if not value or not value.strip():
        raise ValueError("workbench_origin must not be blank")
    if not value.startswith("http://"):
        raise ValueError("workbench_origin must use http://")

    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("workbench_origin must have a valid origin") from exc

    if (
        parsed.scheme != "http"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or "?" in value
        or "#" in value
        or parsed.netloc.endswith(":")
    ):
        raise ValueError("workbench_origin must be a bare local http origin")
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("workbench_origin must have a valid port")

    hostname = parsed.hostname
    if hostname is None:
        raise ValueError("workbench_origin must have a local host")
    if hostname.lower() == "localhost":
        return
    try:
        address = ip_address(hostname)
    except ValueError as exc:
        raise ValueError("workbench_origin must use a loopback host") from exc
    if not address.is_loopback:
        raise ValueError("workbench_origin must use a loopback host")


@dataclass(frozen=True, slots=True)
class FixedWorkspaceHttpConfig:
    """Immutable server-owned workspace and local Workbench origin settings."""

    workspace_id: str
    workbench_origin: str

    def __post_init__(self) -> None:
        _validate_workspace_id(self.workspace_id)
        _validate_workbench_origin(self.workbench_origin)


__all__ = ("FixedWorkspaceHttpConfig",)
