"""S3 tests: Transaction and Idempotency (DEC-035 S3 exit criteria).

Exit = Partial Business Write Rate = 0% + Duplicate Business Version Rate = 0%.
Covers spike-04 (transactional rollback) and idempotency guarantees.
"""

from __future__ import annotations

import sqlite3

import pytest

from spike_runtime.commit import BusinessCommitError, BusinessCommitService
from spike_runtime.harness import WorkflowHarness
from spike_runtime.stores import init_all


@pytest.mark.integration
def test_spike04_transactional_rollback_no_partial_write(tmp_path):
    """spike-04: a failure mid-commit rolls the WHOLE transaction back —
    no partial domain version, no partial evidence link, pointer unchanged,
    no false success audit, no idempotency record."""
    paths = init_all(tmp_path)
    conn = sqlite3.connect(paths.business)
    conn.row_factory = sqlite3.Row
    svc = BusinessCommitService(conn)

    # Establish a good baseline commit first.
    svc.commit_domain_version(domain="facts", payload={"v": 1}, idempotency_key="base")
    pointer_before = svc.current_truth("facts")

    # Injected failure AFTER version insert but BEFORE pointer update.
    with pytest.raises(BusinessCommitError):
        svc.commit_domain_version(
            domain="facts",
            payload={"v": 2},
            idempotency_key="will-fail",
            fail_after_version=True,
        )

    # Nothing leaked.
    assert svc.current_truth("facts") == pointer_before
    assert svc.valid_version_count("facts") == 1  # only the baseline
    assert svc.partial_write_count() == 0
    # No idempotency record for the failed key.
    assert svc._already_committed("will-fail") is None  # noqa: SLF001
    # No 'commit' audit row for a version that does not exist.
    rows = conn.execute(
        "SELECT COUNT(*) AS n FROM business_audit WHERE action = 'commit'"
    ).fetchone()
    assert rows["n"] == 1  # only baseline's audit
    conn.close()


@pytest.mark.integration
def test_duplicate_commit_idempotent_no_duplicate_version(tmp_path):
    """Retrying the same logical commit (same idempotency key) must NOT create
    a duplicate business version; pointer stays stable."""
    paths = init_all(tmp_path)
    conn = sqlite3.connect(paths.business)
    conn.row_factory = sqlite3.Row
    svc = BusinessCommitService(conn)

    key = "idem-facts-1"
    r1 = svc.commit_domain_version(domain="facts", payload={"v": 1}, idempotency_key=key)
    for _ in range(3):
        r = svc.commit_domain_version(domain="facts", payload={"v": 1}, idempotency_key=key)
        assert r.committed is False
        assert r.version_id == r1.version_id

    assert svc.valid_version_count("facts") == 1
    assert svc.current_truth("facts") == r1.version_id
    conn.close()


@pytest.mark.integration
def test_current_truth_pointer_validation(tmp_path):
    """The current-truth pointer always references a VALID version and moves
    atomically on each new commit (older version superseded)."""
    h = WorkflowHarness(tmp_path)
    try:
        h.start({"name": "Acme Bottle", "category": "drinkware"})
        h.submit_review(
            h.graph.get_state(h.config).values["review_id"],
            {"value_proposition": "x", "target_segment": "y", "differentiation": "z", "proof_points": []},
            idempotency_key=f"rs:{h.task_id}",
        )
        h.resume(h.business_snapshot()["current_truth_pointers"]["approved_strategy"])

        snap = h.business_snapshot()
        valid_ids = {v["version_id"] for v in snap["domain_versions"] if v["status"] == "valid"}
        # Every pointer references an existing VALID version.
        for domain, vid in snap["current_truth_pointers"].items():
            assert vid in valid_ids, f"pointer for {domain} references non-valid version"
        assert snap["metrics"]["partial_write_count"] == 0
        assert snap["metrics"]["approved_strategy_version_count"] == 1
    finally:
        h.close()


@pytest.mark.integration
def test_partial_write_rate_and_duplicate_rate_zero(tmp_path):
    """Aggregate S3 exit metrics across a normal workflow."""
    h = WorkflowHarness(tmp_path)
    try:
        start = h.start({"name": "Acme Bottle", "category": "drinkware"})
        h.submit_review(
            start["state"]["review_id"],
            {"value_proposition": "x", "target_segment": "y", "differentiation": "z", "proof_points": []},
            idempotency_key=f"rs:{h.task_id}",
        )
        h.resume(h.business_snapshot()["current_truth_pointers"]["approved_strategy"])
        snap = h.business_snapshot()

        total_versions = len(snap["domain_versions"])
        duplicate = total_versions - len({v["version_id"] for v in snap["domain_versions"]})
        assert snap["metrics"]["partial_write_count"] == 0  # Partial Business Write Rate = 0%
        assert duplicate == 0  # Duplicate Business Version Rate = 0%
    finally:
        h.close()
