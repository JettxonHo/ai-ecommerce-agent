"""Minimal StateGraph skeleton (DEC-035).

S0 goal: prove a LangGraph StateGraph can compile, invoke synchronously,
persist checkpoints via SqliteSaver, and honor the Human Review Node Boundary
(create_review_package -> await_human_review -> load_approved_strategy) as
THREE SEPARATE nodes. Review-package creation and interrupt() are never in
the same node.

This is a MINIMAL graph for architecture validation, NOT the business graph.
"""

from __future__ import annotations

import sqlite3
from typing import Any, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class GraphState(TypedDict, total=False):
    """Compact LangGraph state: references only, NOT business Current Truth."""

    task_id: str
    thread_id: str
    workflow_run_id: str
    facts_version_id: str
    insights_version_id: str
    positioning_version_id: str
    review_id: str
    approved_strategy_version_id: str
    marketing_brief_version_id: str
    # Result of the human review submit (delivered on resume via Command(resume=...)).
    review_submission: dict


def create_review_package(state: GraphState) -> dict:
    """Node 1: build a fixed-version review package reference. NO interrupt here."""
    return {"review_id": f"review_{state['task_id']}"}


def await_human_review(state: GraphState) -> dict:
    """Node 2: pause for human review via interrupt(). NO business writes here.

    On resume, the value passed via Command(resume=...) becomes the return
    value of interrupt().
    """
    submission = interrupt({"awaiting": "human_review", "review_id": state["review_id"]})
    return {"review_submission": submission}


def load_approved_strategy(state: GraphState) -> dict:
    """Node 3: load the approved strategy reference after review. Idempotent."""
    submission = state.get("review_submission") or {}
    return {"approved_strategy_version_id": submission.get("approved_strategy_version_id", "")}


def build_graph(checkpointer: SqliteSaver):
    graph = StateGraph(GraphState)
    graph.add_node("create_review_package", create_review_package)
    graph.add_node("await_human_review", await_human_review)
    graph.add_node("load_approved_strategy", load_approved_strategy)

    graph.add_edge(START, "create_review_package")
    graph.add_edge("create_review_package", "await_human_review")
    graph.add_edge("await_human_review", "load_approved_strategy")
    graph.add_edge("load_approved_strategy", END)

    return graph.compile(checkpointer=checkpointer)


def make_checkpointer(db_path: str) -> tuple[SqliteSaver, sqlite3.Connection]:
    """Create a SqliteSaver over a dedicated checkpoints.sqlite connection.

    Uses an owned connection so the checkpointer works synchronously.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    saver = SqliteSaver(conn)
    saver.setup()
    return saver, conn
