"""CLI Scenario Runner (DEC-035 execution-brief).

    python -m spike_runtime run --scenario spike-01-normal-workflow --workspace .spike-runs/spike-01

Each scenario runs in an isolated workspace directory and produces
business/runtime/checkpoints stores, trace.jsonl, business-snapshot.json and
scenario-result.json. Scenarios are added stage by stage.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .harness import WorkflowHarness


def run_normal_workflow(workspace: Path) -> dict:
    """spike-01: full normal workflow (facts -> insights -> positioning ->
    review package -> interrupt -> review submit -> resume -> marketing brief).
    """
    h = WorkflowHarness(workspace)
    try:
        start = h.start({"name": "Acme Bottle", "category": "drinkware"})
        assert start["interrupted"], "graph must pause at await_human_review"
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
        assert submit["committed"], "review submit must commit an approved strategy"

        final = h.resume(submit["approved_strategy_version_id"])
        snap = h.business_snapshot()

        status = "pass"
        checks = {
            "current_truth_facts_present": "facts" in snap["current_truth_pointers"],
            "approved_strategy_version_count_is_1": snap["metrics"]["approved_strategy_version_count"] == 1,
            "partial_write_count_is_0": snap["metrics"]["partial_write_count"] == 0,
            "marketing_brief_present": "marketing_brief" in snap["current_truth_pointers"],
        }
        if not all(checks.values()):
            status = "fail"
        return h.export_evidence(
            "spike-01-normal-workflow",
            status,
            extra={
                "checks": checks,
                "final_marketing_brief_version_id": final["state"].get("marketing_brief_version_id"),
            },
        )
    finally:
        h.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spike_runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run", help="run a scenario")
    run_p.add_argument("--scenario", required=True)
    run_p.add_argument("--workspace", required=True)
    args = parser.parse_args(argv)

    if args.command == "run":
        if args.scenario in ("spike-01-normal-workflow", "spike-01"):
            doc = run_normal_workflow(Path(args.workspace))
            print(json.dumps({"scenario": doc["scenario"], "status": doc["status"]}, ensure_ascii=False))
            return 0 if doc["status"] == "pass" else 1
        print(json.dumps({"error": f"unknown scenario: {args.scenario}"}, ensure_ascii=False))
        return 2
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
