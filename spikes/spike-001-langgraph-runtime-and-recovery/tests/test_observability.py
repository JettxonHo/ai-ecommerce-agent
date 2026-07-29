"""S5 tests: Observability and Evidence Export (DEC-035 S5 exit criteria).

Exit = each scenario independently reproducible + all key IDs correlatable +
automated assertions runnable (incl. JUnit XML + checkpoint summary).
"""

from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from spike_runtime.evidence import (
    correlate_trace,
    export_checkpoint_summary,
    export_runtime_events,
    write_junit,
)
from spike_runtime.harness import WorkflowHarness


def _run_full(h: WorkflowHarness) -> None:
    start = h.start({"name": "Acme Bottle", "category": "drinkware"})
    h.submit_review(
        start["state"]["review_id"],
        {"value_proposition": "x", "target_segment": "y", "differentiation": "z", "proof_points": []},
        idempotency_key=f"rs:{h.task_id}",
    )
    h.resume(h.business_snapshot()["current_truth_pointers"]["approved_strategy"])


@pytest.mark.integration
def test_checkpoint_summary_and_correlation(tmp_path):
    h = WorkflowHarness(tmp_path)
    try:
        _run_full(h)
        snap = h.business_snapshot()

        # Checkpoint summary: this thread persisted checkpoints.
        summary = export_checkpoint_summary(h.paths.checkpoints, tmp_path / "checkpoint-summary.json")
        assert summary["checkpoint_count"] >= 1
        assert any(t["thread_id"] == h.thread_id for t in summary["threads"])

        # Correlation: all key IDs joinable.
        trace_events = h.trace.read_all()
        report = correlate_trace(trace_events, snap)
        assert report["trace_id_count"] == 1  # single trace across the run
        assert report["approved_strategy_version_count"] == 1
        assert report["partial_write_count"] == 0
        assert "marketing_brief" in report["current_truth_domains"]
        assert (tmp_path / "checkpoint-summary.json").exists()
    finally:
        h.close()


@pytest.mark.integration
def test_scenario_independently_reproducible(tmp_path):
    """Two isolated workspaces running the same scenario produce structurally
    equivalent evidence (same domains, same metrics) — independent reproducibility."""
    results = []
    for i in (1, 2):
        ws = tmp_path / f"run{i}"
        h = WorkflowHarness(ws)
        try:
            _run_full(h)
            snap = h.business_snapshot()
            results.append(
                {
                    "domains": sorted(snap["current_truth_pointers"].keys()),
                    "approved": snap["metrics"]["approved_strategy_version_count"],
                    "partial": snap["metrics"]["partial_write_count"],
                }
            )
        finally:
            h.close()
    assert results[0] == results[1]
    assert results[0]["approved"] == 1 and results[0]["partial"] == 0


@pytest.mark.unit
def test_runtime_events_export(tmp_path):
    rt = tmp_path / "runtime.sqlite"
    import sqlite3

    from spike_runtime.stores import init_runtime_store

    init_runtime_store(tmp_path).close()
    conn = sqlite3.connect(rt)
    conn.execute(
        "INSERT INTO runtime_event(trace_id, workflow_run_id, node_execution_id, event_type, payload_json)"
        " VALUES ('t1', 'r1', NULL, 'test', '{}')"
    )
    conn.commit()
    conn.close()

    rows = export_runtime_events(rt, tmp_path / "runtime-events.json")
    assert rows and rows[0]["trace_id"] == "t1"
    assert (tmp_path / "runtime-events.json").exists()


@pytest.mark.unit
def test_junit_xml_written(tmp_path):
    out = tmp_path / "junit.xml"
    write_junit(
        [
            {"name": "spike-01", "status": "pass"},
            {"name": "spike-02", "status": "fail", "message": "boom"},
        ],
        out,
    )
    root = ET.parse(out).getroot()
    assert root.tag == "testsuite"
    assert root.attrib["tests"] == "2"
    assert root.attrib["failures"] == "1"
    cases = root.findall("testcase")
    assert len(cases) == 2
    assert cases[1].find("failure") is not None
