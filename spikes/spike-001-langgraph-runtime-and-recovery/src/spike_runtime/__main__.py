"""CLI Scenario Runner (DEC-035 execution-brief).

Unified entry point:

    python -m spike_runtime run --scenario spike-00-skeleton --workspace .spike-runs/spike-00

S0 scope: initialize the three separated stores, build the graph with a
SqliteSaver checkpointer, run an interrupt/resume cycle, emit a runtime
record + JSONL trace, and write a scenario-result.json. Full business
scenarios (spike-01..12) are added in later stages.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from langgraph.types import Command

from . import ids
from .graph import build_graph, make_checkpointer
from .stores import init_all
from .trace import LocalTraceRecorder


def run_skeleton(workspace: Path) -> dict:
    """S0 smoke: prove graph runs, checkpoints persist, runtime record generated."""
    workspace = Path(workspace)
    paths = init_all(workspace)
    trace = LocalTraceRecorder(workspace / "trace.jsonl", ids.trace_id())

    task_id = ids.task_id()
    thread_id = ids.new_id("thread")
    workflow_run_id = ids.workflow_run_id()

    saver, conn = make_checkpointer(str(paths.checkpoints))
    try:
        graph = build_graph(saver)
        config = {"configurable": {"thread_id": thread_id}}

        trace.record("run_start", task_id=task_id, workflow_run_id=workflow_run_id, thread_id=thread_id)

        initial = {
            "task_id": task_id,
            "thread_id": thread_id,
            "workflow_run_id": workflow_run_id,
        }
        # First invoke: runs create_review_package -> await_human_review -> interrupt.
        result = graph.invoke(initial, config=config)
        interrupted = "__interrupt__" in result
        review_id = result.get("review_id")
        trace.record("interrupted", review_id=review_id, interrupted=interrupted)

        # Resume with the same thread_id, a NEW run id, no package recreation.
        resume_run_id = ids.workflow_run_id()
        submission = {"approved_strategy_version_id": "strategy_v1", "action": "submit"}
        final = graph.invoke(Command(resume=submission), config=config)
        trace.record(
            "resumed",
            workflow_run_id=resume_run_id,
            approved_strategy_version_id=final.get("approved_strategy_version_id"),
        )

        # Verify a checkpoint exists for this thread.
        state = graph.get_state(config)
        checkpoint_present = state is not None and state.values.get("review_id") == review_id

        runtime_record = {
            "task_id": task_id,
            "thread_id": thread_id,
            "workflow_run_id": workflow_run_id,
            "resume_run_id": resume_run_id,
            "review_id": review_id,
            "interrupted": interrupted,
            "approved_strategy_version_id": final.get("approved_strategy_version_id"),
            "checkpoint_present": checkpoint_present,
        }
    finally:
        conn.close()

    result_doc = {
        "scenario": "spike-00-skeleton",
        "status": "pass" if (runtime_record["interrupted"] and checkpoint_present) else "fail",
        "runtime_record": runtime_record,
        "stores": {
            "business": str(paths.business),
            "runtime": str(paths.runtime),
            "checkpoints": str(paths.checkpoints),
        },
    }
    (workspace / "scenario-result.json").write_text(
        json.dumps(result_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    trace.record("run_end", status=result_doc["status"])
    return result_doc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spike_runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run", help="run a scenario")
    run_p.add_argument("--scenario", required=True)
    run_p.add_argument("--workspace", required=True)
    args = parser.parse_args(argv)

    if args.command == "run":
        if args.scenario in ("spike-00-skeleton", "skeleton"):
            doc = run_skeleton(Path(args.workspace))
            print(json.dumps({"scenario": doc["scenario"], "status": doc["status"]}, ensure_ascii=False))
            return 0 if doc["status"] == "pass" else 1
        print(json.dumps({"error": f"unknown scenario: {args.scenario}"}))
        return 2
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
