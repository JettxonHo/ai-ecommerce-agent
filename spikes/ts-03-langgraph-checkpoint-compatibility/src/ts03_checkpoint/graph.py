"""Minimal synchronous StateGraph used only by TS-03 tests."""

from __future__ import annotations

from typing import TypedDict

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class CheckpointState(TypedDict, total=False):
    task_id: str
    thread_id: str
    input_version: str
    source_set_version: str
    stage: str
    review_package_version: str | None
    workflow_definition_version: str
    graph_state_schema_version: str
    serializer_profile_version: str
    prepared: bool
    review_approved: bool
    runtime_result: str


def _prepare(state: CheckpointState) -> dict[str, object]:
    del state
    return {"prepared": True}


def _await_review(state: CheckpointState) -> dict[str, object]:
    response = interrupt(
        {
            "kind": "ts03-review",
            "task_id": state["task_id"],
            "message": "approve the disposable runtime checkpoint",
        }
    )
    if not isinstance(response, dict) or response.get("approved") is not True:
        raise ValueError("TS-03 review response must be {'approved': True}")
    return {"review_approved": True}


def _runtime_finish(state: CheckpointState) -> dict[str, object]:
    if state.get("review_approved") is not True:
        raise RuntimeError("runtime finish reached without review approval")
    return {"runtime_result": "completed"}


def build_graph(checkpointer: PostgresSaver):
    """Build the graph without performing setup or connecting to Business DB."""

    builder = StateGraph(CheckpointState)
    builder.add_node("prepare", _prepare)
    builder.add_node("await_review", _await_review)
    builder.add_node("runtime_finish", _runtime_finish)
    builder.add_edge(START, "prepare")
    builder.add_edge("prepare", "await_review")
    builder.add_edge("await_review", "runtime_finish")
    builder.add_edge("runtime_finish", END)
    return builder.compile(checkpointer=checkpointer)
