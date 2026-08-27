"""Stable framework-neutral facade for the private Needs Input module."""

from .application.commands import ResolveNeedsInput
from .application.errors import (
    NeedsInputApplicationError,
    NeedsInputCapabilityConflictError,
    NeedsInputIdempotencyConflictError,
    NeedsInputNotFoundError,
    NeedsInputRevisionConflictError,
)
from .application.protocols import NeedsInputApplication
from .application.results import ResolveNeedsInputResult
from .domain.evidence import InsufficientResultEvidence
from .domain.snapshots import (
    NeedsInputActionRequestSnapshot,
    NeedsInputExpectedRecovery,
    NeedsInputStatus,
)

__all__ = [
    "InsufficientResultEvidence",
    "NeedsInputActionRequestSnapshot",
    "NeedsInputApplication",
    "NeedsInputApplicationError",
    "NeedsInputCapabilityConflictError",
    "NeedsInputExpectedRecovery",
    "NeedsInputIdempotencyConflictError",
    "NeedsInputNotFoundError",
    "NeedsInputRevisionConflictError",
    "ResolveNeedsInput",
    "ResolveNeedsInputResult",
    "NeedsInputStatus",
]
