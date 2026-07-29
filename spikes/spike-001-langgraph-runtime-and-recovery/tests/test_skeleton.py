"""S0/S1 tests: environment, skeleton, and normal workflow (DEC-035).

S0 exit = Minimal Graph runs + Runtime Record generated.
S1 exit = Current Truth correct + Graph pauses/resumes correctly + Trace complete.
"""

from __future__ import annotations

import sqlite3

import pytest

from spike_runtime import ids
from spike_runtime.commit import BusinessCommitError, BusinessCommitService
from spike_runtime.graph import build_business_graph, make_checkpointer
from spike_runtime.harness import WorkflowHarness
from spike_runtime.providers import MockRetrievalRuntime, ScriptedModelProvider
from spike_runtime.stores import init_all
from spike_runtime.trace import LocalTraceRecorder


# --- S0 ---------------------------------------------------------------------
@pytest.mark.unit
def test_ids_have_prefixes():
    assert ids.task_id().startswith("task_")
    assert ids.workflow_run_id().startswith("run_")
    assert ids.trace_id().startswith("trace_")
    assert ids.version_id("facts").startswith("facts_")


@pytest.mark.unit
def test_three_stores_are_separate(tmp_path):
    paths = init_all(tmp_path)
    assert paths.business.name == "business.sqlite"
    assert paths.runtime.name == "runtime.sqlite"
    assert paths.checkpoints.name == "checkpoints.sqlite"
    conn = sqlite3.connect(paths.business)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"task", "domain_version", "current_truth_pointer", "review_package"} <= tables


@pytest.mark.unit
def test_graph_compiles(tmp_path):
    init_all(tmp_path)
    saver, conn = make_checkpointer(str(tmp_path / "checkpoints.sqlite"))
    bconn = sqlite3.connect(tmp_path / "business.sqlite")
    try:
        graph = build_business_graph(
            saver,
            commit=BusinessCommitService(bconn),
            model=ScriptedModelProvider(),
            retrieval=MockRetrievalRuntime(),
        )
        assert graph is not None
    finally:
        conn.close()
        bconn.close()


@pytest.mark.unit
def test_trace_recorder_appends_jsonl(tmp_path):
    rec = LocalTraceRecorder(tmp_path / "trace.jsonl", "trace_test")
    rec.record("a", x=1)
    rec.record("b", y=2)
    events = rec.read_all()
    assert [e["event_type"] for e in events] == ["a", "b"]
    assert [e["seq"] for e in events] == [1, 2]


@pytest.mark.unit
def test_business_commit_atomic_and_idempotent(tmp_path):
    paths = init_all(tmp_path)
    conn = sqlite3.connect(paths.business)
    conn.row_factory = sqlite3.Row
    svc = BusinessCommitService(conn)

    r1 = svc.commit_domain_version(domain="facts", payload={"a": 1}, idempotency_key="k-1")
    assert r1.committed and svc.current_truth("facts") == r1.version_id
    assert svc.valid_version_count("facts") == 1

    r2 = svc.commit_domain_version(domain="facts", payload={"a": 1}, idempotency_key="k-1")
    assert r2.committed is False and svc.valid_version_count("facts") == 1

    r3 = svc.commit_domain_version(domain="facts", payload={"a": 2}, idempotency_key="k-2")
    assert svc.current_truth("facts") == r3.version_id and svc.valid_version_count("facts") == 1

    with pytest.raises(BusinessCommitError):
        svc.commit_domain_version(
            domain="insights", payload={"b": 1}, idempotency_key="k-3", fail_after_version=True
        )
    assert svc.current_truth("insights") is None
    assert svc.partial_write_count() == 0
    conn.close()


# --- S1 ---------------------------------------------------------------------
@pytest.mark.integration
def test_normal_workflow_end_to_end(tmp_path):
    h = WorkflowHarness(tmp_path)
    try:
        start = h.start({"name": "Acme Bottle", "category": "drinkware"})
        assert start["interrupted"] is True
        review_id = start["state"]["review_id"]

        submit = h.submit_review(
            review_id,
            {
                "value_proposition": "the easy default choice",
                "target_segment": "beginners",
                "differentiation": "lowest setup friction",
                "proof_points": ["frag_1"],
            },
            idempotency_key=f"review-submit:{h.task_id}",
        )
        assert submit["committed"] is True

        final = h.resume(submit["approved_strategy_version_id"])
        snap = h.business_snapshot()

        # Current Truth correct.
        assert "facts" in snap["current_truth_pointers"]
        assert "approved_strategy" in snap["current_truth_pointers"]
        assert "marketing_brief" in snap["current_truth_pointers"]
        assert snap["metrics"]["approved_strategy_version_count"] == 1
        assert snap["metrics"]["partial_write_count"] == 0
        assert final["state"]["marketing_brief_version_id"]

        # Trace complete: start -> interrupt -> submit -> resume -> end present.
        h.export_evidence("spike-01-normal-workflow", "pass")
        events = [e["event_type"] for e in h.trace.read_all()]
        for expected in ("run_start", "interrupted", "review_submit", "resumed", "run_end"):
            assert expected in events
    finally:
        h.close()
