"""Runtime identifier layer (DEC-033).

Every runtime entity carries an explicit, correlatable identity so that
runtime events, traces, business commits, and checkpoints can be joined.

These are runtime/execution identifiers, NOT business Current Truth.
"""

from __future__ import annotations

import uuid


def new_id(prefix: str) -> str:
    """Return a sortable-ish unique identifier with a readable prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def task_id() -> str:
    return new_id("task")


def workflow_run_id() -> str:
    return new_id("run")


def skill_run_id() -> str:
    return new_id("skillrun")


def node_execution_id() -> str:
    return new_id("nodeexec")


def attempt_id() -> str:
    return new_id("attempt")


def error_id() -> str:
    return new_id("err")


def trace_id() -> str:
    return new_id("trace")


def recovery_case_id() -> str:
    return new_id("recovery")


def review_id() -> str:
    return new_id("review")


def version_id(domain: str) -> str:
    """Domain version id, e.g. version_id('facts') -> 'facts_...'."""
    return new_id(domain)
