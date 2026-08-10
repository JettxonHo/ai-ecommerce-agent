"""Unit contracts for the primitive Workflow Checkpoint header seam."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import FrozenInstanceError, fields, is_dataclass
from inspect import signature
from types import MappingProxyType
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.orchestration.workflow_runtime.checkpoint_state import (
    ThreadId,
    WorkflowCheckpointHeader,
    WorkflowCheckpointStateHeader,
    WorkflowRuntimeCompatibility,
    checkpoint_header_from_state,
    checkpoint_header_to_state,
)
from ai_ecommerce_agent.shared_kernel import RunId, TaskId

pytestmark = pytest.mark.unit


class _StringSubclass(str):
    def strip(self, *args: object, **kwargs: object) -> str:
        del args, kwargs
        raise AssertionError("string subclass methods must not be invoked")


def _compatibility() -> WorkflowRuntimeCompatibility:
    return WorkflowRuntimeCompatibility(
        "workflow-v1",
        "state-v1",
        "serializer-v1",
        "checkpointer-v1",
        "store-v1",
    )


def _header(
    *,
    task_id: TaskId | None = None,
    thread_id: ThreadId | None = None,
    run_id: RunId | None = None,
    compatibility: WorkflowRuntimeCompatibility | None = None,
) -> WorkflowCheckpointHeader:
    return WorkflowCheckpointHeader(
        task_id or TaskId("task-header"),
        thread_id or ThreadId("thread-header"),
        run_id or RunId("run-header"),
        compatibility or _compatibility(),
    )


def _remove_task(state: dict[str, object]) -> object:
    return state.pop("task_id")


def _null_run(state: dict[str, object]) -> None:
    state["run_id"] = None


def _raw_thread(state: dict[str, object]) -> None:
    state["thread_id"] = 42


def _subclass_workflow(state: dict[str, object]) -> None:
    state["workflow_definition_version"] = _StringSubclass("subclass")


def _blank_graph(state: dict[str, object]) -> None:
    state["graph_state_schema_version"] = "   "


def test_thread_id_is_frozen_slotted_ordered_and_strict() -> None:
    value = "thread-preserved"
    thread_id = ThreadId(value)

    assert is_dataclass(ThreadId)
    assert tuple(field.name for field in fields(ThreadId)) == ("value",)
    assert ThreadId.__slots__ == ("value",)
    assert get_type_hints(ThreadId) == {"value": str}
    assert thread_id.value is value
    assert not hasattr(thread_id, "__dict__")
    assert ThreadId("a") < ThreadId("b")

    with pytest.raises(FrozenInstanceError):
        thread_id.value = "other"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del thread_id.value  # type: ignore[misc]

    with pytest.raises(ValueError):
        ThreadId("   ")
    with pytest.raises(TypeError):
        ThreadId(cast(str, _StringSubclass("thread-subclass")))
    with pytest.raises(TypeError):
        ThreadId(cast(str, 42))


def test_runtime_compatibility_has_exact_frozen_slotted_fields_and_identity() -> None:
    values = tuple(f"v-{index}" for index in range(5))
    compatibility = WorkflowRuntimeCompatibility(*values)
    expected_fields = (
        "workflow_definition_version",
        "graph_state_schema_version",
        "serializer_profile_version",
        "checkpointer_package_version",
        "checkpoint_store_schema_version",
    )

    assert is_dataclass(WorkflowRuntimeCompatibility)
    assert tuple(field.name for field in fields(compatibility)) == expected_fields
    assert WorkflowRuntimeCompatibility.__slots__ == expected_fields
    assert get_type_hints(WorkflowRuntimeCompatibility) == dict.fromkeys(
        expected_fields, str
    )
    assert (
        tuple(getattr(compatibility, field_name) for field_name in expected_fields)
        == values
    )
    for field_name, value in zip(expected_fields, values, strict=True):
        assert getattr(compatibility, field_name) is value
    assert not hasattr(compatibility, "__dict__")

    with pytest.raises(FrozenInstanceError):
        compatibility.workflow_definition_version = "other"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del compatibility.serializer_profile_version  # type: ignore[misc]


@pytest.mark.parametrize("field_index", range(5))
def test_runtime_compatibility_rejects_blank_and_string_subclasses(
    field_index: int,
) -> None:
    values = [f"v-{index}" for index in range(5)]
    values[field_index] = "   "
    with pytest.raises(ValueError):
        WorkflowRuntimeCompatibility(*values)

    values[field_index] = _StringSubclass("subclass")
    with pytest.raises(TypeError):
        WorkflowRuntimeCompatibility(*values)


def test_checkpoint_header_has_exact_fields_types_slots_and_identity() -> None:
    task_id = TaskId("task-preserved")
    thread_id = ThreadId("thread-preserved")
    run_id = RunId("run-preserved")
    compatibility = _compatibility()
    header = _header(
        task_id=task_id,
        thread_id=thread_id,
        run_id=run_id,
        compatibility=compatibility,
    )
    expected_fields = ("task_id", "thread_id", "run_id", "compatibility")

    assert is_dataclass(WorkflowCheckpointHeader)
    assert tuple(field.name for field in fields(header)) == expected_fields
    assert WorkflowCheckpointHeader.__slots__ == expected_fields
    assert get_type_hints(WorkflowCheckpointHeader) == {
        "task_id": TaskId,
        "thread_id": ThreadId,
        "run_id": RunId,
        "compatibility": WorkflowRuntimeCompatibility,
    }
    assert header.task_id is task_id
    assert header.thread_id is thread_id
    assert header.run_id is run_id
    assert header.compatibility is compatibility
    assert not hasattr(header, "__dict__")

    with pytest.raises(FrozenInstanceError):
        header.task_id = TaskId("other")  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        del header.compatibility  # type: ignore[misc]


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("task_id", cast(TaskId, "raw-task")),
        ("thread_id", cast(ThreadId, "raw-thread")),
        ("run_id", cast(RunId, "raw-run")),
        ("compatibility", cast(WorkflowRuntimeCompatibility, "raw-compatibility")),
    ],
)
def test_checkpoint_header_rejects_raw_typed_values(
    field_name: str,
    value: object,
) -> None:
    values: dict[str, object] = {
        "task_id": TaskId("task-header"),
        "thread_id": ThreadId("thread-header"),
        "run_id": RunId("run-header"),
        "compatibility": _compatibility(),
    }
    values[field_name] = value
    with pytest.raises(TypeError):
        WorkflowCheckpointHeader(**values)  # type: ignore[arg-type]


def test_state_header_is_exact_typed_dict_and_ordered() -> None:
    expected_keys = (
        "task_id",
        "thread_id",
        "run_id",
        "workflow_definition_version",
        "graph_state_schema_version",
        "serializer_profile_version",
        "checkpointer_package_version",
        "checkpoint_store_schema_version",
    )
    assert isinstance(WorkflowCheckpointStateHeader, type)
    assert issubclass(WorkflowCheckpointStateHeader, dict)
    assert WorkflowCheckpointStateHeader.__required_keys__ == set(expected_keys)
    assert tuple(WorkflowCheckpointStateHeader.__annotations__) == expected_keys
    assert get_type_hints(WorkflowCheckpointStateHeader) == dict.fromkeys(
        expected_keys, str
    )
    assert all(
        value is str for value in get_type_hints(WorkflowCheckpointStateHeader).values()
    )


def test_header_to_state_is_exact_ordered_primitive_projection() -> None:
    header = _header()
    state = checkpoint_header_to_state(header)
    expected_keys = (
        "task_id",
        "thread_id",
        "run_id",
        "workflow_definition_version",
        "graph_state_schema_version",
        "serializer_profile_version",
        "checkpointer_package_version",
        "checkpoint_store_schema_version",
    )
    assert type(state) is dict
    assert tuple(state) == expected_keys
    assert state == {
        "task_id": "task-header",
        "thread_id": "thread-header",
        "run_id": "run-header",
        "workflow_definition_version": "workflow-v1",
        "graph_state_schema_version": "state-v1",
        "serializer_profile_version": "serializer-v1",
        "checkpointer_package_version": "checkpointer-v1",
        "checkpoint_store_schema_version": "store-v1",
    }
    assert state["task_id"] is header.task_id.value
    assert state["thread_id"] is header.thread_id.value
    assert state["run_id"] is header.run_id.value
    assert (
        state["workflow_definition_version"]
        is header.compatibility.workflow_definition_version
    )
    assert (
        state["graph_state_schema_version"]
        is header.compatibility.graph_state_schema_version
    )
    assert (
        state["serializer_profile_version"]
        is header.compatibility.serializer_profile_version
    )
    assert (
        state["checkpointer_package_version"]
        is header.compatibility.checkpointer_package_version
    )
    assert (
        state["checkpoint_store_schema_version"]
        is header.compatibility.checkpoint_store_schema_version
    )


def test_header_from_state_round_trips_and_ignores_future_extra_keys() -> None:
    values = {
        "task_id": "task-state",
        "thread_id": "thread-state",
        "run_id": "run-state",
        "workflow_definition_version": "workflow-state",
        "graph_state_schema_version": "graph-state",
        "serializer_profile_version": "serializer-state",
        "checkpointer_package_version": "checkpointer-state",
        "checkpoint_store_schema_version": "store-state",
    }
    source = {**values, "future_state_key": {"ignored": True}}
    header = checkpoint_header_from_state(MappingProxyType(source))

    assert header.task_id.value is values["task_id"]
    assert header.thread_id.value is values["thread_id"]
    assert header.run_id.value is values["run_id"]
    assert (
        header.compatibility.workflow_definition_version
        is values["workflow_definition_version"]
    )
    assert checkpoint_header_to_state(header) == values


@pytest.mark.parametrize(
    "mutator",
    [
        _remove_task,
        _null_run,
        _raw_thread,
        _subclass_workflow,
        _blank_graph,
    ],
)
def test_header_from_state_rejects_missing_null_raw_subclass_and_blank(
    mutator: Callable[[dict[str, object]], object],
) -> None:
    state: dict[str, object] = {
        "task_id": "task-state",
        "thread_id": "thread-state",
        "run_id": "run-state",
        "workflow_definition_version": "workflow-state",
        "graph_state_schema_version": "graph-state",
        "serializer_profile_version": "serializer-state",
        "checkpointer_package_version": "checkpointer-state",
        "checkpoint_store_schema_version": "store-state",
    }
    mutator(state)
    with pytest.raises((TypeError, ValueError, KeyError)):
        checkpoint_header_from_state(state)


def test_header_mapping_does_not_infer_checkpoint_or_attempt_identity() -> None:
    header = checkpoint_header_from_state(
        {
            "task_id": "task-state",
            "thread_id": "thread-state",
            "run_id": "run-state",
            "workflow_definition_version": "workflow-state",
            "graph_state_schema_version": "graph-state",
            "serializer_profile_version": "serializer-state",
            "checkpointer_package_version": "checkpointer-state",
            "checkpoint_store_schema_version": "store-state",
            "checkpoint_id": "vendor-id",
            "attempt": "not-frozen",
        }
    )
    assert not hasattr(header, "checkpoint_id")
    assert not hasattr(header, "attempt")


def test_mapping_functions_have_exact_public_signatures() -> None:
    assert list(signature(checkpoint_header_to_state).parameters) == ["header"]
    assert list(signature(checkpoint_header_from_state).parameters) == ["state"]
    assert get_type_hints(checkpoint_header_to_state) == {
        "header": WorkflowCheckpointHeader,
        "return": WorkflowCheckpointStateHeader,
    }
    assert get_type_hints(checkpoint_header_from_state) == {
        "state": Mapping[str, object],
        "return": WorkflowCheckpointHeader,
    }


def test_mapping_to_state_rejects_raw_header() -> None:
    with pytest.raises(TypeError):
        checkpoint_header_to_state(cast(WorkflowCheckpointHeader, "raw"))
