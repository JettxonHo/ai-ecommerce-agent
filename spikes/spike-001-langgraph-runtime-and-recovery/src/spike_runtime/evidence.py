"""Evidence export utilities (DEC-035 S5).

Every scenario must be independently reproducible and every key ID joinable:
runtime events, JSONL trace, business snapshot, checkpoint summary, and a
scenario result with automated assertions. JUnit XML for CI-style reporting.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from xml.etree import ElementTree as ET


def export_runtime_events(runtime_db: Path, out_path: Path) -> list[dict]:
    """Dump the runtime store's events as JSON evidence (not a SQLite binary)."""
    conn = sqlite3.connect(runtime_db)
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(r) for r in conn.execute(
            "SELECT event_seq, trace_id, workflow_run_id, node_execution_id, event_type, payload_json"
            " FROM runtime_event ORDER BY event_seq"
        )]
    finally:
        conn.close()
    Path(out_path).write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows


def export_checkpoint_summary(checkpoints_db: Path, out_path: Path) -> dict:
    """Summarize LangGraph SqliteSaver checkpoints as JSON (count + threads)."""
    conn = sqlite3.connect(checkpoints_db)
    conn.row_factory = sqlite3.Row
    summary: dict = {"threads": [], "checkpoint_count": 0}
    try:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "checkpoints" in tables:
            rows = conn.execute(
                "SELECT thread_id, COUNT(*) AS n FROM checkpoints GROUP BY thread_id"
            ).fetchall()
            summary["threads"] = [{"thread_id": r["thread_id"], "checkpoints": r["n"]} for r in rows]
            summary["checkpoint_count"] = sum(r["n"] for r in rows)
    finally:
        conn.close()
    Path(out_path).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def write_junit(results: list[dict], out_path: Path) -> None:
    """Write a minimal JUnit XML report from scenario/test results.

    results: list of {"name": str, "status": "pass"|"fail", "message": str?}
    """
    suite = ET.Element(
        "testsuite",
        name="spike-001",
        tests=str(len(results)),
        failures=str(sum(1 for r in results if r["status"] == "fail")),
    )
    for r in results:
        case = ET.SubElement(suite, "testcase", name=r["name"])
        if r["status"] == "fail":
            fail = ET.SubElement(case, "failure", message=r.get("message", ""))
            fail.text = r.get("message", "")
    tree = ET.ElementTree(suite)
    ET.indent(tree, space="  ")
    tree.write(out_path, encoding="utf-8", xml_declaration=True)


def correlate_trace(trace_events: list[dict], business_snapshot: dict) -> dict:
    """Join check: every trace event's identifiers resolve against evidence.

    Returns a correlation report — all key IDs must be present and consistent.
    """
    trace_ids = {e.get("trace_id") for e in trace_events if e.get("trace_id")}
    run_ids = {e.get("workflow_run_id") for e in trace_events if e.get("workflow_run_id")}
    pointers = business_snapshot.get("current_truth_pointers", {})
    return {
        "trace_id_count": len(trace_ids),
        "workflow_run_ids": sorted(r for r in run_ids if r),
        "current_truth_domains": sorted(pointers.keys()),
        "approved_strategy_version_count": business_snapshot.get("metrics", {}).get("approved_strategy_version_count"),
        "partial_write_count": business_snapshot.get("metrics", {}).get("partial_write_count"),
    }
