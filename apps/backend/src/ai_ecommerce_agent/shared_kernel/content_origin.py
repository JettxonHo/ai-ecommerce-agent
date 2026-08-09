"""Framework-neutral provenance values for structured content."""

from enum import StrEnum


class ContentOrigin(StrEnum):
    """The exact origins allowed for user-visible structured content."""

    MODEL = "model"
    USER = "user"


__all__ = ["ContentOrigin"]
