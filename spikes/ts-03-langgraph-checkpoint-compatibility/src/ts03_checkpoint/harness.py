"""Bounded invocation/resume harness for the real PostgresSaver graph."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import cast
from uuid import uuid4

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command

from .compatibility import CHECKPOINT_STORE_SCHEMA_VERSION, CHECKPOINTER_PACKAGE_VERSION
from .graph import CheckpointState, build_graph
from .reconciliation import (
    CheckpointMetadata,
    CompatibilityTuple,
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
        self._checkpointer = checkpointer
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
        current: CurrentTruth,
        request: RecoveryRequest,
    ) -> tuple[RunOutcome, RecoveryDecision]:
        checkpoint = self._latest_checkpoint_metadata(previous)
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

    def _latest_checkpoint_metadata(self, previous: RunOutcome) -> CheckpointMetadata:
        """Read the latest vendor tuple, state channels, and config from Postgres."""

        latest = self._checkpointer.get_tuple(
            {"configurable": {"thread_id": previous.identity.thread_id}}
        )
        if latest is None:
            raise RuntimeError("cannot reconcile resume: no PostgresSaver checkpoint exists")
        configurable = cast(Mapping[str, object], latest.config.get("configurable", {}))
        if "thread_id" not in configurable:
            raise RuntimeError("cannot reconcile resume: checkpoint config has no thread_id")
        channels_value = latest.checkpoint.get("channel_values")
        if not hasattr(channels_value, "get"):
            raise RuntimeError("cannot reconcile resume: checkpoint state channels are missing")
        channels = cast(Mapping[str, object], channels_value)
        metadata = latest.metadata
        task_id = metadata.get("task_id")
        if not isinstance(task_id, str):
            raise RuntimeError("cannot reconcile resume: checkpoint metadata has no task_id")
        state_task_id = channels.get("task_id")
        if state_task_id != task_id:
            raise RuntimeError("cannot reconcile resume: checkpoint task identity disagrees")
        return CheckpointMetadata(
            task_id=task_id,
            thread_id=str(configurable["thread_id"]),
            input_version=self._required_channel(channels, "input_version"),
            source_set_version=self._required_channel(channels, "source_set_version"),
            stage=self._required_channel(channels, "stage"),
            review_package_version=self._optional_channel(channels, "review_package_version"),
            compatibility=CompatibilityTuple(
                workflow_definition_version=self._required_channel(
                    channels, "workflow_definition_version"
                ),
                graph_state_schema_version=self._required_channel(
                    channels, "graph_state_schema_version"
                ),
                serializer_profile_version=self._required_channel(
                    channels, "serializer_profile_version"
                ),
                checkpointer_package_version=CHECKPOINTER_PACKAGE_VERSION,
                store_schema_version=CHECKPOINT_STORE_SCHEMA_VERSION,
            ),
        )

    @staticmethod
    def _required_channel(channels: Mapping[str, object], name: str) -> str:
        value = channels.get(name)
        if not isinstance(value, str):
            raise RuntimeError(f"cannot reconcile resume: checkpoint channel {name!r} is missing")
        return value

    @staticmethod
    def _optional_channel(channels: Mapping[str, object], name: str) -> str | None:
        value = channels.get(name)
        if value is None:
            return None
        if not isinstance(value, str):
            raise RuntimeError(f"cannot reconcile resume: checkpoint channel {name!r} is invalid")
        return value
