"""Scenario-based Fault Injection + bounded retry (DEC-035).

FaultPlan is explicit, default-OFF, scenario-enabled, repeatable, and cleans
up after itself. Business code NEVER scatters `if test_mode: raise`; all
faults flow through this module. No fault reaches production modules and no
fault changes an Accepted Business Contract.

Bounded retry: a transient failure is retried up to `max_attempts`; on
exhaustion the operation raises RetryBudgetExhausted (no infinite retry) and
the failure is recorded as a structured runtime error.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class TransientInfrastructureError(Exception):
    """A retryable, transient infrastructure failure (injected)."""


class InvalidStructuredOutputError(Exception):
    """The model returned output that failed deterministic structural validation."""


class RetryBudgetExhausted(Exception):
    """Raised when an operation exhausts its bounded retry budget."""

    def __init__(self, operation: str, attempts: int):
        self.operation = operation
        self.attempts = attempts
        super().__init__(f"retry budget exhausted for {operation} after {attempts} attempts")


@dataclass
class Fault:
    target_operation: str
    fail_on_attempts: set[int]
    failure_type: str = "transient_infrastructure_error"


@dataclass
class FaultPlan:
    """Explicit fault plan for one scenario. Default: disabled (no faults)."""

    enabled: bool = False
    faults: list[Fault] = field(default_factory=list)
    _attempts: dict[str, int] = field(default_factory=dict)

    def _bump(self, operation: str) -> int:
        self._attempts[operation] = self._attempts.get(operation, 0) + 1
        return self._attempts[operation]

    def call(self, operation: str, fn):
        """Invoke fn() for this attempt; inject the fault DURING the call.

        The work runs first (so the attempt is real), then the configured fault
        raises if this attempt is faulted — modeling a transient failure that
        occurs inside the operation.
        """
        attempt = self._bump(operation)
        result = fn()
        for fault in self.faults:
            if fault.target_operation == operation and attempt in fault.fail_on_attempts:
                if fault.failure_type == "transient_infrastructure_error":
                    raise TransientInfrastructureError(f"injected transient failure on {operation} attempt {attempt}")
                if fault.failure_type == "invalid_structured_output":
                    raise InvalidStructuredOutputError(f"injected invalid output on {operation} attempt {attempt}")
        return result


def run_with_retry(operation: str, fn, *, max_attempts: int = 3, fault_plan: FaultPlan | None = None):
    """Run fn() with bounded retry on TransientInfrastructureError.

    The work `fn` is invoked each attempt. If a fault_plan is enabled, the call
    is wrapped so the fault fires DURING the work attempt (not before it), which
    models a real transient infrastructure failure inside the operation.

    Retries ONLY transient errors; invalid-output and other errors are NOT
    retried (they are not transient). On exhaustion raises
    RetryBudgetExhausted. No infinite retry.
    """
    plan = fault_plan or FaultPlan(enabled=False)
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            if plan.enabled:
                return plan.call(operation, fn)
            return fn()
        except TransientInfrastructureError as exc:
            last_exc = exc
            continue
    raise RetryBudgetExhausted(operation, max_attempts) from last_exc
