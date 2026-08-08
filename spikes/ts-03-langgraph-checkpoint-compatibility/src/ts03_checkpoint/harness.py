"""Bounded invocation/resume harness for the real PostgresSaver graph."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import cast
from uuid import uuid4

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command

from .graph import CheckpointState, build_graph
from .reconciliation import (
    CheckpointMetadata,
    CurrentTruth,
    RecoveryDecision,
    RecoveryRequest,
    classify_recovery,
)


@dataclass(frozen=True, slots=True)
class RunIdentity:
    task_id: str
    thread_id: str
    run_id: str
    attempt: int

    @classmethod
    def create(cls, *, task_id: str, thread_id: str, attempt: int = 1) -> RunIdentity:
        return cls(task_id=task_id, thread_id=thread_id, run_id=str(uuid4()), attempt=attempt)


@dataclass(frozen=True, slots=True)
class RunOutcome:
    identity: RunIdentity
    state: dict[str, object]

    @property
    def interrupted(self) -> bool:
        return "__interrupt__" in self.state


class ResumeRejected(RuntimeError):
    """Raised when reconciliation refuses to invoke the graph."""

    def __init__(self, decision: RecoveryDecision) -> None:
        super().__init__(f"TS-03 reconciliation rejected: {decision.action}: {decision.reason}")
        self.decision = decision


class CheckpointHarness:
    def __init__(self, checkpointer: PostgresSaver) -> None:
        self._graph = build_graph(checkpointer)

    @staticmethod
    def _config(identity: RunIdentity) -> RunnableConfig:
        return cast(
            RunnableConfig,
            {
                "configurable": {"thread_id": identity.thread_id},
                "metadata": {
                    "task_id": identity.task_id,
                    "run_id": identity.run_id,
                    "attempt": identity.attempt,
                },
            },
        )

    def start(
        self,
        identity: RunIdentity,
        *,
        input_version: str,
        source_set_version: str,
        stage: str,
        review_package_version: str,
        workflow_definition_version: str,
        graph_state_schema_version: str,
        serializer_profile_version: str,
    ) -> RunOutcome:
        initial: CheckpointState = {
            "task_id": identity.task_id,
            "thread_id": identity.thread_id,
            "input_version": input_version,
            "source_set_version": source_set_version,
            "stage": stage,
            "review_package_version": review_package_version,
            "workflow_definition_version": workflow_definition_version,
            "graph_state_schema_version": graph_state_schema_version,
            "serializer_profile_version": serializer_profile_version,
        }
        result = self._graph.invoke(initial, config=self._config(identity), durability="sync")
        return RunOutcome(identity=identity, state=cast(dict[str, object], result))

    def resume(
        self,
        previous: RunOutcome,
        *,
        checkpoint: CheckpointMetadata,
        current: CurrentTruth,
        request: RecoveryRequest,
    ) -> tuple[RunOutcome, RecoveryDecision]:
        decision = classify_recovery(checkpoint, current, request)
        if decision.action != "resume_same_thread" or not decision.checkpoint_reusable:
            raise ResumeRejected(decision)
        identity = replace(
            previous.identity, run_id=str(uuid4()), attempt=previous.identity.attempt + 1
        )
        result = self._graph.invoke(
            Command(resume={"approved": True}),
            config=self._config(identity),
            durability="sync",
        )
        return RunOutcome(identity=identity, state=cast(dict[str, object], result)), decision
