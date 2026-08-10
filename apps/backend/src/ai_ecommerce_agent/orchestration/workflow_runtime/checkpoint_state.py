"""Primitive, framework-neutral Workflow Checkpoint header contracts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TypedDict

from ai_ecommerce_agent.shared_kernel import RunId, TaskId


def _require_exact(value: object, expected: type[object], field_name: str) -> None:
    if type(value) is not expected:
        raise TypeError(f"{field_name} must be an exact {expected.__name__}")


def _require_text(value: object, field_name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be an exact built-in string")
    if not value.strip():
        raise ValueError(f"{field_name} must be non-blank")
    return value


@dataclass(frozen=True, slots=True, order=True)
class ThreadId:
    """Stable workflow thread identity without generation or format policy."""

    value: str

    def __post_init__(self) -> None:
        _require_text(self.value, "value")


@dataclass(frozen=True, slots=True)
class WorkflowRuntimeCompatibility:
    """Readable versions required to assess a checkpoint's compatibility."""

    workflow_definition_version: str
    graph_state_schema_version: str
    serializer_profile_version: str
    checkpointer_package_version: str
    checkpoint_store_schema_version: str

    def __post_init__(self) -> None:
        for field_name in (
            "workflow_definition_version",
            "graph_state_schema_version",
            "serializer_profile_version",
            "checkpointer_package_version",
            "checkpoint_store_schema_version",
        ):
            _require_text(getattr(self, field_name), field_name)


@dataclass(frozen=True, slots=True)
class WorkflowCheckpointHeader:
    """Stable identities and compatibility metadata for one checkpoint."""

    task_id: TaskId
    thread_id: ThreadId
    run_id: RunId
    compatibility: WorkflowRuntimeCompatibility

    def __post_init__(self) -> None:
        _require_exact(self.task_id, TaskId, "task_id")
        _require_exact(self.thread_id, ThreadId, "thread_id")
        _require_exact(self.run_id, RunId, "run_id")
        _require_exact(
            self.compatibility, WorkflowRuntimeCompatibility, "compatibility"
        )


class WorkflowCheckpointStateHeader(TypedDict):
    """Primitive ordered header keys retained by a later serializer."""

    task_id: str
    thread_id: str
    run_id: str
    workflow_definition_version: str
    graph_state_schema_version: str
    serializer_profile_version: str
    checkpointer_package_version: str
    checkpoint_store_schema_version: str


def checkpoint_header_to_state(
    header: WorkflowCheckpointHeader,
) -> WorkflowCheckpointStateHeader:
    """Project a validated header into its exact primitive state mapping."""

    _require_exact(header, WorkflowCheckpointHeader, "header")
    return {
        "task_id": header.task_id.value,
        "thread_id": header.thread_id.value,
        "run_id": header.run_id.value,
        "workflow_definition_version": header.compatibility.workflow_definition_version,
        "graph_state_schema_version": header.compatibility.graph_state_schema_version,
        "serializer_profile_version": header.compatibility.serializer_profile_version,
        "checkpointer_package_version": (
            header.compatibility.checkpointer_package_version
        ),
        "checkpoint_store_schema_version": (
            header.compatibility.checkpoint_store_schema_version
        ),
    }


def _state_text(state: Mapping[str, object], key: str) -> str:
    try:
        value = state[key]
    except KeyError as error:
        raise ValueError(f"state is missing required key {key!r}") from error
    return _require_text(value, key)


def checkpoint_header_from_state(
    state: Mapping[str, object],
) -> WorkflowCheckpointHeader:
    """Rehydrate a header from required primitive keys and ignore future keys."""

    return WorkflowCheckpointHeader(
        TaskId(_state_text(state, "task_id")),
        ThreadId(_state_text(state, "thread_id")),
        RunId(_state_text(state, "run_id")),
        WorkflowRuntimeCompatibility(
            _state_text(state, "workflow_definition_version"),
            _state_text(state, "graph_state_schema_version"),
            _state_text(state, "serializer_profile_version"),
            _state_text(state, "checkpointer_package_version"),
            _state_text(state, "checkpoint_store_schema_version"),
        ),
    )
