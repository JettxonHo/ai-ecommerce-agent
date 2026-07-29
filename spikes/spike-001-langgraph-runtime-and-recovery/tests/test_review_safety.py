"""S2 tests: Human Review and Version Safety (DEC-035 S2 exit criteria).

Exit = stale review cannot be submitted + stale checkpoint cannot advance +
resume is idempotent + positioning is NOT regenerated.
"""

from __future__ import annotations

import pytest

from spike_runtime.harness import WorkflowHarness
from spike_runtime.review import StaleReviewError

CANDIDATE = {
    "value_proposition": "the easy default choice",
    "target_segment": "beginners",
    "differentiation": "lowest setup friction",
    "proof_points": ["frag_1"],
}


def _start_to_review(h: WorkflowHarness) -> str:
    start = h.start({"name": "Acme Bottle", "category": "drinkware"})
    assert start["interrupted"] is True
    return start["state"]["review_id"]


@pytest.mark.integration
def test_spike05_resume_idempotent_no_positioning_regen(tmp_path):
    """spike-05: interrupt + resume; resume keeps thread_id, new run id, and
    does NOT recreate the review package or regenerate positioning."""
    h = WorkflowHarness(tmp_path)
    try:
        review_id = _start_to_review(h)
        submit = h.submit_review(review_id, CANDIDATE, idempotency_key=f"rs:{h.task_id}")
        final = h.resume(submit["approved_strategy_version_id"])

        # Capture version ids, then resume AGAIN (idempotent replay).
        first = h.business_snapshot()
        pos_v1 = first["current_truth_pointers"]["positioning"]
        pkg_v1 = first["current_truth_pointers"].get("review_package")

        final2 = h.resume(submit["approved_strategy_version_id"])
        second = h.business_snapshot()

        # Positioning NOT regenerated; review package NOT recreated.
        assert second["current_truth_pointers"]["positioning"] == pos_v1
        assert second["metrics"]["approved_strategy_version_count"] == 1
        # One positioning version only.
        pos_count = sum(1 for v in second["domain_versions"] if v["domain"] == "positioning")
        assert pos_count == 1
    finally:
        h.close()


@pytest.mark.integration
def test_spike06_duplicate_review_submit_idempotent(tmp_path):
    """spike-06: duplicate review submit with the same idempotency key creates
    NO duplicate Approved Strategy Version."""
    h = WorkflowHarness(tmp_path)
    try:
        review_id = _start_to_review(h)
        key = f"rs:{h.task_id}"
        s1 = h.submit_review(review_id, CANDIDATE, idempotency_key=key)
        assert s1["committed"] is True

        # Duplicate submit (same key) — no new version, no error.
        s2 = h.submit_review(review_id, CANDIDATE, idempotency_key=key)
        assert s2["committed"] is False
        assert s2["approved_strategy_version_id"] == s1["approved_strategy_version_id"]

        snap = h.business_snapshot()
        assert snap["metrics"]["approved_strategy_version_count"] == 1
        assert snap["metrics"]["partial_write_count"] == 0
    finally:
        h.close()


@pytest.mark.integration
def test_spike07_stale_review_rejected(tmp_path):
    """spike-07: a stale review package cannot be submitted."""
    h = WorkflowHarness(tmp_path)
    try:
        review_id = _start_to_review(h)
        # First submit succeeds and supersedes the package.
        h.submit_review(review_id, CANDIDATE, idempotency_key=f"rs:{h.task_id}")

        # A NEW submit (different idempotency key) against the now-stale package
        # must be rejected.
        with pytest.raises(StaleReviewError):
            h.submit_review(review_id, CANDIDATE, idempotency_key=f"rs2:{h.task_id}")

        snap = h.business_snapshot()
        assert snap["metrics"]["approved_strategy_version_count"] == 1
    finally:
        h.close()


@pytest.mark.integration
def test_spike08_stale_checkpoint_cannot_advance(tmp_path):
    """spike-08: a stale / foreign resume must NOT advance business state.

    A Command(resume=...) against a thread with no matching checkpoint runs the
    graph from START with an EMPTY state (no runtime identity). The graph must
    fail fast (StaleResumeError) BEFORE any business write, leaving Current
    Truth untouched."""
    from langgraph.types import Command

    from spike_runtime.graph import StaleResumeError

    h = WorkflowHarness(tmp_path)
    try:
        review_id = _start_to_review(h)
        submit = h.submit_review(review_id, CANDIDATE, idempotency_key=f"rs:{h.task_id}")
        before = h.business_snapshot()

        foreign_config = {"configurable": {"thread_id": "thread_FOREIGN_stale"}}
        with pytest.raises(StaleResumeError):
            h.graph.invoke(
                Command(resume={"approved_strategy_version_id": submit["approved_strategy_version_id"]}),
                config=foreign_config,
            )

        after = h.business_snapshot()
        # Business Current Truth unchanged; no partial writes leaked.
        assert after["current_truth_pointers"] == before["current_truth_pointers"]
        assert after["metrics"]["approved_strategy_version_count"] == 1
        assert after["metrics"]["partial_write_count"] == 0
    finally:
        h.close()
