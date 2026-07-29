"""S0 smoke tests: environment + skeleton sanity (DEC-035 S0 exit criteria).

Exit = Minimal Graph runs + Runtime Record is generated.
"""

from __future__ import annotations

import sqlite3

import pytest

from spike_runtime import ids
from spike_runtime.commit import BusinessCommitError, BusinessCommitService
from spike_runtime.graph import build_graph, make_checkpointer
from spike_runtime.stores import init_all
from spike_runtime.trace import LocalTraceRecorder

pytestmark = pytest.mark.unit


def test_ids_have_prefixes():
    assert ids.task_id().startswith("task_")
    assert ids.workflow_run_id().startswith("run_")
    assert ids.trace_id().startswith("trace_")
    assert ids.version_id("facts").startswith("facts_")


def test_three_stores_are_separate(tmp_path):
    paths = init_all(tmp_path)
    assert paths.business.name == "business.sqlite"
    assert paths.runtime.name == "runtime.sqlite"
    assert paths.checkpoints.name == "checkpoints.sqlite"
    assert paths.business.exists() and paths.runtime.exists()
    # business has its schema
    conn = sqlite3.connect(paths.business)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"task", "domain_version", "current_truth_pointer", "review_package"} <= tables


def test_graph_compile_and_invoke(tmp_path):
    init_all(tmp_path)
    saver, conn = make_checkpointer(str(tmp_path / "checkpoints.sqlite"))
    try:
        graph = build_graph(saver)
        assert graph is not None
    finally:
        conn.close()


def test_trace_recorder_appends_jsonl(tmp_path):
    rec = LocalTraceRecorder(tmp_path / "trace.jsonl", "trace_test")
    rec.record("a", x=1)
    rec.record("b", y=2)
    events = rec.read_all()
    assert [e["event_type"] for e in events] == ["a", "b"]
    assert all(e["trace_id"] == "trace_test" for e in events)
    assert [e["seq"] for e in events] == [1, 2]


def test_business_commit_atomic_and_idempotent(tmp_path):
    paths = init_all(tmp_path)
    conn = sqlite3.connect(paths.business)
    conn.row_factory = sqlite3.Row
    svc = BusinessCommitService(conn)

    key = "k-1"
    r1 = svc.commit_domain_version(domain="facts", payload={"a": 1}, idempotency_key=key)
    assert r1.committed is True
    assert svc.current_truth("facts") == r1.version_id
    assert svc.valid_version_count("facts") == 1

    # Idempotent replay: no duplicate business version.
    r2 = svc.commit_domain_version(domain="facts", payload={"a": 1}, idempotency_key=key)
    assert r2.committed is False
    assert svc.valid_version_count("facts") == 1

    # A second distinct commit supersedes the first.
    r3 = svc.commit_domain_version(domain="facts", payload={"a": 2}, idempotency_key="k-2")
    assert svc.current_truth("facts") == r3.version_id
    assert svc.valid_version_count("facts") == 1

    # Rollback: injected failure leaves no partial write.
    with pytest.raises(BusinessCommitError):
        svc.commit_domain_version(
            domain="insights", payload={"b": 1}, idempotency_key="k-3", fail_after_version=True
        )
    assert svc.current_truth("insights") is None
    assert svc.partial_write_count() == 0
    conn.close()
