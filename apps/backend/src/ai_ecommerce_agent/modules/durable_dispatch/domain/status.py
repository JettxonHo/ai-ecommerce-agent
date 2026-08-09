"""Durable Dispatch Work Intent lifecycle catalog."""

from __future__ import annotations

from enum import StrEnum


class WorkIntentStatus(StrEnum):
    """The exact persisted lifecycle vocabulary for a Work Intent."""

    PENDING = "pending"
    AVAILABLE = "available"
    LEASED = "leased"
    IN_PROGRESS = "in_progress"
    SUCCEEDED = "succeeded"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_TERMINAL = "failed_terminal"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"
