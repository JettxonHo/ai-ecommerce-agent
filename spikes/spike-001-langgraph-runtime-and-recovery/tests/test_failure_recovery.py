"""S4 tests: Failure and Recovery (DEC-035 S4 exit criteria).

Exit = every handled failure has structured runtime evidence + no infinite
retry + recovery does NOT bypass the validator/commit path.
Covers spike-02 / spike-03 / spike-09 / spike-10 / spike-11 + recovery case.
"""

from __future__ import annotations

import pytest

from spike_runtime.commit import BusinessCommitService
from spike_runtime.faults import (
    Fault,
    FaultPlan,
    InvalidStructuredOutputError,
    RetryBudgetExhausted,
    TransientInfrastructureError,
    run_with_retry,
)
from spike_runtime.harness import WorkflowHarness
from spike_runtime.providers import MockRetrievalRuntime


# --- spike-02: transient failure + bounded retry ----------------------------
@pytest.mark.failure_injection
def test_spike02_transient_failure_recovers_with_bounded_retry():
    calls = {"n": 0}

    def work():
        calls["n"] += 1
        return "ok"

    # Fail on attempts 1 and 2, succeed on 3.
    plan = FaultPlan(enabled=True, faults=[Fault("op", {1, 2})])
    result = run_with_retry("op", work, max_attempts=3, fault_plan=plan)
    assert result == "ok"
    assert calls["n"] == 3


# --- spike-11: retry budget exhaustion --------------------------------------
@pytest.mark.failure_injection
def test_spike11_retry_budget_exhaustion_no_infinite_retry():
    calls = {"n": 0}

    def work():
        calls["n"] += 1
        return "never"

    # Fail every attempt.
    plan = FaultPlan(enabled=True, faults=[Fault("op", {1, 2, 3, 4, 5})])
    with pytest.raises(RetryBudgetExhausted):
        run_with_retry("op", work, max_attempts=3, fault_plan=plan)
    # Bounded: exactly max_attempts, not infinite.
    assert calls["n"] == 3


# --- spike-03: invalid structured output is NOT retried ---------------------
@pytest.mark.failure_injection
def test_spike03_invalid_structured_output_not_retried():
    calls = {"n": 0}

    def work():
        calls["n"] += 1
        raise InvalidStructuredOutputError("schema violation")

    # Invalid output is a non-transient error: run_with_retry must not retry it.
    with pytest.raises(InvalidStructuredOutputError):
        run_with_retry("op", work, max_attempts=3, fault_plan=FaultPlan(enabled=False))
    assert calls["n"] == 1  # no retry on non-transient


# --- fault plan default OFF + cleanup ---------------------------------------
@pytest.mark.failure_injection
def test_fault_plan_default_off_no_injection():
    def work():
        return "clean"

    # Default plan is disabled: no fault even if a fault matches.
    assert run_with_retry("op", work, max_attempts=2) == "clean"


# --- spike-09: retrieval degraded -> fallback, no fabrication ----------------
@pytest.mark.integration
def test_spike09_retrieval_degraded_fallback_no_fabrication(tmp_path):
    degraded = MockRetrievalRuntime(degraded=True)
    out = degraded.retrieve("customer reviews")
    assert out["degraded"] is True
    assert out["candidates"] == []
    assert out["coverage"] == "none"
    # Caller must surface insufficiency, NOT fabricate fragments.
    h = WorkflowHarness(tmp_path, degraded_retrieval=True)
    try:
        start = h.start({"name": "Acme Bottle", "category": "drinkware"})
        assert start["interrupted"] is True
        snap = h.business_snapshot()
        # Insights version recorded the degraded flag instead of fabricating.
        insights = [v for v in snap["domain_versions"] if v["domain"] == "insights"]
        assert insights, "insights version must exist"
        assert snap["metrics"]["partial_write_count"] == 0
    finally:
        h.close()


# --- spike-10: cancellation leaves no partial business write ------------------
@pytest.mark.integration
def test_spike10_cancellation_no_partial_write(tmp_path):
    """Cancelling before review submit leaves NO approved strategy and no
    partial business state; interrupt state is recoverable, not committed."""
    h = WorkflowHarness(tmp_path)
    try:
        start = h.start({"name": "Acme Bottle", "category": "drinkware"})
        assert start["interrupted"] is True
        # Simulate cancellation: do NOT submit review, do NOT resume.
        snap = h.business_snapshot()
        # No approved strategy committed; no partial writes.
        assert "approved_strategy" not in snap["current_truth_pointers"]
        assert snap["metrics"]["approved_strategy_version_count"] == 0
        assert snap["metrics"]["partial_write_count"] == 0
    finally:
        h.close()


# --- recovery case: retry a failed commit via same idempotency key -----------
@pytest.mark.integration
def test_recovery_case_failed_commit_retry_via_same_idempotency_key(tmp_path):
    """After a rolled-back commit (transient), retrying with the SAME idempotency
    key succeeds cleanly and produces exactly ONE version (recovery does not
    duplicate, does not bypass the commit service)."""
    import sqlite3

    from spike_runtime.commit import BusinessCommitError
    from spike_runtime.stores import init_all

    paths = init_all(tmp_path)
    conn = sqlite3.connect(paths.business)
    conn.row_factory = sqlite3.Row
    svc = BusinessCommitService(conn)

    key = "recovery-facts"
    # First attempt fails transiently (rolled back).
    with pytest.raises(BusinessCommitError):
        svc.commit_domain_version(domain="facts", payload={"v": 1}, idempotency_key=key, fail_after_version=True)
    assert svc.current_truth("facts") is None
    assert svc.partial_write_count() == 0

    # Recovery: retry same logical operation with the SAME idempotency key.
    res = svc.commit_domain_version(domain="facts", payload={"v": 1}, idempotency_key=key)
    assert res.committed is True
    assert svc.current_truth("facts") == res.version_id
    assert svc.valid_version_count("facts") == 1
    assert svc.partial_write_count() == 0
    conn.close()
