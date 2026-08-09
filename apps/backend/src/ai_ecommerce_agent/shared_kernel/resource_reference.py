"""Framework-neutral immutable references to exact resources."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceReference:
    """Immutable reference to one resource owned by any module."""

    resource_kind: str
    resource_id: str

    def __post_init__(self) -> None:
        for field_name in ("resource_kind", "resource_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")
            if not value.strip():
                raise ValueError(f"{field_name} must be non-empty")


__all__ = ["ResourceReference"]
