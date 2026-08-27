"""Safe application errors for the Needs Input boundary."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NeedsInputApplicationError(Exception):
    """Stable, technology-neutral error crossing the application seam."""

    error_code: str
    message: str
    retryability: bool = False

    def __post_init__(self) -> None:
        if not self.error_code.strip() or not self.message.strip():
            raise ValueError("Needs Input errors require safe code and message")
        Exception.__init__(self, self.message)


class NeedsInputPersistenceError(Exception):
    """Private adapter signal translated by the application service."""


class NeedsInputRevisionPersistenceError(NeedsInputPersistenceError):
    """A compare-and-swap update lost a concurrent revision race."""


class NeedsInputNotFoundError(NeedsInputApplicationError):
    """A requested action request is not present."""

    def __init__(self) -> None:
        super().__init__("not_found", "The Needs Input request was not found.")


class NeedsInputRevisionConflictError(NeedsInputApplicationError):
    """The caller's request revision is no longer current."""

    def __init__(self) -> None:
        super().__init__(
            "revision_conflict",
            "The Needs Input request changed; refresh before retrying.",
        )


class NeedsInputIdempotencyConflictError(NeedsInputApplicationError):
    """A retry key was reused with a different canonical resolution."""

    def __init__(self) -> None:
        super().__init__(
            "idempotency_conflict",
            "The retry key belongs to another Needs Input resolution.",
        )


class NeedsInputCapabilityConflictError(NeedsInputApplicationError):
    """The request is terminal or otherwise no longer resolvable."""

    def __init__(self) -> None:
        super().__init__(
            "capability_conflict",
            "The Needs Input request cannot be resolved in its current state.",
        )


__all__ = [
    "NeedsInputApplicationError",
    "NeedsInputCapabilityConflictError",
    "NeedsInputIdempotencyConflictError",
    "NeedsInputNotFoundError",
    "NeedsInputPersistenceError",
    "NeedsInputRevisionPersistenceError",
    "NeedsInputRevisionConflictError",
]
