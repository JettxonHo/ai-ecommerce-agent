"""Workflow orchestrator: run the business-flow graph end to end.

Drives: graph invoke (to interrupt) -> Review Submit (separate business
transaction) -> graph resume (same thread_id, new run id) -> evidence export.

This is the harness used by the CLI runner and by scenario tests.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from langgraph.types import Command

from . import ids
from .commit import BusinessCommitService
from .graph import build_business_graph, make_checkpointer
from .providers import MockRetrievalRuntime, ScriptedModelProvider
from .review import ReviewService
from .stores import init_all
from .trace import LocalTraceRecorder


class WorkflowHarness:
    def __init__(self, workspace: Path, *, degraded_retrieval: bool = False):
        self.workspace = Path(workspace)
        self.paths = init_all(self.workspace)
        self.trace = LocalTraceRecorder(self.workspace / "trace.jsonl", ids.trace_id())
        self.business_conn = sqlite3.connect(self.paths.business)
        self.business_conn.row_factory = sqlite3.Row
        self.commit = BusinessCommitService(self.business_conn)
        self.review = ReviewService(self.business_conn)
        self.model = ScriptedModelProvider()
        self.retrieval = MockRetrievalRuntime(degraded=degraded_retrieval)
        self.saver, self._cp_conn = make_checkpointer(str(self.paths.checkpoints))
        self.graph = build_business_graph(
            self.saver, commit=self.commit, model=self.model, retrieval=self.retrieval
        )

        self.task_id = ids.task_id()
        self.thread_id = ids.new_id("thread")
        self.workflow_run_id = ids.workflow_run_id()
        self.config = {"configurable": {"thread_id": self.thread_id}}

    def close(self) -> None:
        self._cp_conn.close()
        self.business_conn.close()

    # -- run to interrupt ---------------------------------------------------
    def start(self, product_input: dict) -> dict:
        self.trace.record(
            "run_start", task_id=self.task_id, workflow_run_id=self.workflow_run_id, thread_id=self.thread_id
        )
        initial = {
            "task_id": self.task_id,
            "thread_id": self.thread_id,
            "workflow_run_id": self.workflow_run_id,
            "product_input": product_input,
        }
        result = self.graph.invoke(initial, config=self.config)
        interrupted = "__interrupt__" in result
        self.trace.record(
            "interrupted",
            interrupted=interrupted,
            review_id=result.get("review_id"),
            facts_version_id=result.get("facts_version_id"),
            positioning_version_id=result.get("positioning_version_id"),
        )
        return {"interrupted": interrupted, "state": result}

    # -- review submit (separate business transaction) ----------------------
    def submit_review(self, review_id: str, chosen_candidate: dict, *, idempotency_key: str) -> dict:
        out = self.review.submit(
            task_id=self.task_id,
            review_id=review_id,
            chosen_candidate=chosen_candidate,
            idempotency_key=idempotency_key,
        )
        self.trace.record(
            "review_submit",
            review_id=review_id,
            approved_strategy_version_id=out["approved_strategy_version_id"],
            committed=out["committed"],
        )
        return out

    # -- resume -------------------------------------------------------------
    def resume(self, approved_strategy_version_id: str) -> dict:
        resume_run_id = ids.workflow_run_id()
        final = self.graph.invoke(
            Command(resume={"approved_strategy_version_id": approved_strategy_version_id, "action": "submit"}),
            config=self.config,
        )
        self.trace.record(
            "resumed",
            workflow_run_id=resume_run_id,
            marketing_brief_version_id=final.get("marketing_brief_version_id"),
        )
        return {"state": final, "resume_run_id": resume_run_id}

    # -- evidence export ------------------------------------------------------
    def business_snapshot(self) -> dict:
        cur = self.business_conn
        pointers = {r["domain"]: r["version_id"] for r in cur.execute("SELECT * FROM current_truth_pointer")}
        versions = [
            dict(r)
            for r in cur.execute(
                "SELECT version_id, domain, seq, status FROM domain_version ORDER BY seq"
            )
        ]
        audit = [dict(r) for r in cur.execute("SELECT action, ref_id, seq FROM business_audit ORDER BY seq")]
        idem = [dict(r) for r in cur.execute("SELECT idempotency_key, ref_id FROM idempotency_record")]
        return {
            "current_truth_pointers": pointers,
            "domain_versions": versions,
            "business_audit": audit,
            "idempotency_records": idem,
            "metrics": {
                "approved_strategy_version_count": self.commit.valid_version_count("approved_strategy"),
                "partial_write_count": self.commit.partial_write_count(),
            },
        }

    def export_evidence(self, scenario: str, status: str, extra: dict | None = None) -> dict:
        snapshot = self.business_snapshot()
        doc = {
            "scenario": scenario,
            "status": status,
            "task_id": self.task_id,
            "thread_id": self.thread_id,
            "workflow_run_id": self.workflow_run_id,
            "business_snapshot": snapshot,
            **(extra or {}),
        }
        (self.workspace / "scenario-result.json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (self.workspace / "business-snapshot.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self.trace.record("run_end", status=status)
        return doc
