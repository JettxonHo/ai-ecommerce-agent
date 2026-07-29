"""Minimal business-flow StateGraph (DEC-035 Human Review Node Boundary).

    extract_facts -> analyze_insights -> generate_positioning
      -> create_review_package -> await_human_review -> load_approved_strategy
      -> generate_marketing_brief

Rules honored:
  * Review-package creation and interrupt() are SEPARATE nodes.
  * Graph nodes never write Business Current Truth directly; they go through
    BusinessCommitService (atomic, idempotent).
  * Resume keeps the same thread_id, uses a new run id, does NOT recreate the
    Review Package and does NOT regenerate Positioning candidates.
"""

from __future__ import annotations

import sqlite3
from typing import Any, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from .commit import BusinessCommitService
from .providers import MockRetrievalRuntime, ScriptedModelProvider


class GraphState(TypedDict, total=False):
    task_id: str
    thread_id: str
    workflow_run_id: str
    product_input: dict
    facts_version_id: str
    insights_version_id: str
    positioning_version_id: str
    review_id: str
    approved_strategy_version_id: str
    marketing_brief_version_id: str
    review_submission: dict
    error: str


def build_business_graph(
    checkpointer: SqliteSaver,
    *,
    commit: BusinessCommitService,
    model: ScriptedModelProvider,
    retrieval: MockRetrievalRuntime,
):
    """Compile the minimal business-flow graph with injected services."""

    def extract_facts(state: GraphState) -> dict:
        out = model.generate_facts(state.get("product_input", {}))
        res = commit.commit_domain_version(
            domain="facts",
            payload=out,
            idempotency_key=f"facts:{state['task_id']}",
            stage_state="facts_extracted",
            evidence_links=[{"fragment_id": f["fragment_id"]} for f in out["facts"]],
        )
        return {"facts_version_id": res.version_id}

    def analyze_insights(state: GraphState) -> dict:
        retr = retrieval.retrieve("customer reviews")
        out = model.generate_insights({"id": state["facts_version_id"]}, retr["candidates"])
        res = commit.commit_domain_version(
            domain="insights",
            payload={**out, "retrieval_degraded": retr["degraded"]},
            idempotency_key=f"insights:{state['task_id']}",
            stage_state="insights_analyzed",
        )
        return {"insights_version_id": res.version_id}

    def generate_positioning(state: GraphState) -> dict:
        out = model.generate_positioning({"id": state["facts_version_id"]}, {"id": state["insights_version_id"]})
        res = commit.commit_domain_version(
            domain="positioning",
            payload=out,
            idempotency_key=f"positioning:{state['task_id']}",
            stage_state="positioning_generated",
        )
        return {"positioning_version_id": res.version_id}

    def create_review_package(state: GraphState) -> dict:
        """Node: build a FIXED-version review package. NO interrupt here. Idempotent."""
        package = {
            "facts_version_id": state["facts_version_id"],
            "insights_version_id": state["insights_version_id"],
            "positioning_version_id": state["positioning_version_id"],
        }
        res = commit.commit_domain_version(
            domain="review_package",
            payload=package,
            idempotency_key=f"review_package:{state['task_id']}",
            stage_state="review_package_created",
        )
        return {"review_id": res.version_id}

    def await_human_review(state: GraphState) -> dict:
        """Node: pause for human review. NO business writes here."""
        submission = interrupt({"awaiting": "human_review", "review_id": state["review_id"]})
        return {"review_submission": submission}

    def load_approved_strategy(state: GraphState) -> dict:
        """Node: load the Approved Strategy after review. Idempotent; does NOT
        recreate the review package or regenerate positioning."""
        submission = state.get("review_submission") or {}
        # The Approved Strategy is committed by the separate Review Submit
        # transaction (see review.py). Here we only surface the reference.
        return {"approved_strategy_version_id": submission.get("approved_strategy_version_id", "")}

    def generate_marketing_brief(state: GraphState) -> dict:
        brief = model.generate_marketing_brief({"value_proposition": "the easy default choice"})
        res = commit.commit_domain_version(
            domain="marketing_brief",
            payload={**brief, "approved_strategy_version_id": state["approved_strategy_version_id"]},
            idempotency_key=f"marketing_brief:{state['task_id']}",
            stage_state="brief_generated",
        )
        return {"marketing_brief_version_id": res.version_id}

    graph = StateGraph(GraphState)
    graph.add_node("extract_facts", extract_facts)
    graph.add_node("analyze_insights", analyze_insights)
    graph.add_node("generate_positioning", generate_positioning)
    graph.add_node("create_review_package", create_review_package)
    graph.add_node("await_human_review", await_human_review)
    graph.add_node("load_approved_strategy", load_approved_strategy)
    graph.add_node("generate_marketing_brief", generate_marketing_brief)

    graph.add_edge(START, "extract_facts")
    graph.add_edge("extract_facts", "analyze_insights")
    graph.add_edge("analyze_insights", "generate_positioning")
    graph.add_edge("generate_positioning", "create_review_package")
    graph.add_edge("create_review_package", "await_human_review")
    graph.add_edge("await_human_review", "load_approved_strategy")
    graph.add_edge("load_approved_strategy", "generate_marketing_brief")
    graph.add_edge("generate_marketing_brief", END)

    return graph.compile(checkpointer=checkpointer)


def make_checkpointer(db_path: str) -> tuple[SqliteSaver, sqlite3.Connection]:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()
    return saver, conn
