"""Tests-first Slice A contract for the private Needs Input application seam.

The module is loaded inside each test deliberately.  This keeps collection
successful while making a missing application boundary an executable RED
failure instead of a collection/import-only failure.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from importlib import import_module
from types import TracebackType
from typing import Any, Self, cast

import pytest

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

pytestmark = pytest.mark.unit


def _load_needs_input() -> tuple[Any, Any]:
    """Load the public contracts and application service at the test seam."""

    public = import_module("ai_ecommerce_agent.modules.needs_input.public")
    services = import_module(
        "ai_ecommerce_agent.modules.needs_input.application.services"
    )
    return public, services


class _Repository:
    """Small transactional repository double for the application port."""

    def __init__(self, owner: _UnitOfWork) -> None:
        self._owner = owner

    def get(self, action_request_id: str) -> object | None:
        return self._owner.working.get(action_request_id)

    def get_current(self, task_id: TaskId) -> object | None:
        for request in self._owner.working.values():
            if (
                getattr(request, "task_id", None) == task_id
                and getattr(getattr(request, "status", None), "value", None) == "open"
            ):
                return request
        return None

    def add(self, request: object) -> None:
        self._owner.operations.append("add")
        action_request_id = str(request.action_request_id)  # type: ignore[attr-defined]
        if action_request_id in self._owner.working:
            raise RuntimeError("duplicate action request")
        self._owner.working[action_request_id] = request

    def save(self, request: object, *, expected_revision: Revision) -> None:
        self._owner.operations.append("save")
        if self._owner.fail_save:
            from ai_ecommerce_agent.modules.needs_input.application.errors import (
                NeedsInputPersistenceError,
            )

            raise NeedsInputPersistenceError()
        action_request_id = str(request.action_request_id)  # type: ignore[attr-defined]
        current = self._owner.working.get(action_request_id)
        if (
            current is None or current.revision != expected_revision  # type: ignore[attr-defined]
        ):
            raise RuntimeError("stale action request")
        self._owner.working[action_request_id] = request


class _UnitOfWork:
    def __init__(
        self,
        store: dict[str, object],
        *,
        fail_save: bool = False,
    ) -> None:
        self.store = store
        self.working: dict[str, object] = {}
        self.fail_save = fail_save
        self.commits = 0
        self.rollbacks = 0
        self.operations: list[str] = []
        self._active = False
        self.requests = _Repository(self)
        # The longer name is intentionally exposed too: either spelling is a
        # valid private adapter choice, while both remain behind the facade.
        self.needs_input_requests = self.requests

    def __enter__(self) -> Self:
        self.working = dict(self.store)
        self._active = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc_value, traceback
        if self._active:
            self.rollback()
        self.close()

    def commit(self) -> None:
        assert self._active
        self.store.clear()
        self.store.update(self.working)
        self.commits += 1
        self._active = False

    def rollback(self) -> None:
        if not self._active:
            return
        self.rollbacks += 1
        self._active = False

    def close(self) -> None:
        self._active = False


class _Factory:
    def __init__(self, *, fail_save: bool = False) -> None:
        self.store: dict[str, object] = {}
        self.fail_save = fail_save
        self.uows: list[_UnitOfWork] = []

    def __call__(self) -> _UnitOfWork:
        uow = _UnitOfWork(self.store, fail_save=self.fail_save)
        self.uows.append(uow)
        return uow


def _evidence(
    public: Any, *, task_id: str, input_revision: int, result_revision: int
) -> Any:
    return public.InsufficientResultEvidence(
        task_id=TaskId(task_id),
        input_revision=Revision(input_revision),
        result_revision=Revision(result_revision),
        missing_information=("verified competitor evidence",),
        affected_stages=("product_positioning",),
        source_references=(),
        conflict_values=(),
    )


def _service(public: Any, services: Any, factory: _Factory) -> Any:
    # Keep the test at the application seam: the public immutable contracts
    # cross into the private service, while the repository remains injected.
    del public
    return services.NeedsInputApplicationService(factory)


def test_insufficient_result_derives_one_truthful_task_scoped_request() -> None:
    public, services = _load_needs_input()
    factory = _Factory()
    request = _service(public, services, factory).publish_from_result(
        _evidence(public, task_id="task-a", input_revision=4, result_revision=7)
    )

    assert request.task_id == TaskId("task-a")
    assert request.status.value == "open"
    assert request.revision == Revision.initial()
    assert request.reason_type == "missing_information"
    assert request.reason_summary == "verified competitor evidence"
    assert request.affected_stages == ("product_positioning",)
    assert request.source_references == ()
    assert request.conflict_values == ()
    assert "provide_source_reference" in request.allowed_resolution_types
    assert "cancel_path" in request.allowed_resolution_types
    assert request.expected_recovery == "rerun"
    assert request.action_request_id


def test_sufficient_result_supersedes_without_a_successor_request() -> None:
    """A newer sufficient result clears the blocker without synthetic state."""

    public, services = _load_needs_input()
    factory = _Factory()
    request = _service(public, services, factory).publish_from_result(
        _evidence(public, task_id="task-a", input_revision=1, result_revision=1)
    )

    superseded = request.supersede(None, now=datetime(2026, 8, 25, tzinfo=UTC))

    assert superseded.status.value == "superseded"
    assert superseded.superseded_by is None
    assert superseded.revision == Revision.initial().next()
    assert superseded.resolution_idempotency_key is None
    assert superseded.resolution_type is None
    assert superseded.resolution_payload is None
    assert superseded.resolved_at is None


def test_sufficient_result_supersession_clears_current_in_caller_transaction() -> None:
    """The caller-owned transaction retains history and clears the current view."""

    public, services = _load_needs_input()
    factory = _Factory()
    application = _service(public, services, factory)
    first = application.publish_from_result(
        _evidence(public, task_id="task-a", input_revision=1, result_revision=1)
    )

    with factory() as uow:
        superseded = application.supersede_current_for_result_in_transaction(
            uow.needs_input_requests,
            task_id=TaskId("task-a"),
            input_revision=Revision(2),
            result_revision=Revision(2),
        )
        assert superseded is not None
        uow.commit()

    assert superseded.revision == first.revision.next()
    assert superseded.status.value == "superseded"
    assert superseded.superseded_by is None
    assert application.get_current_request(TaskId("task-a")) is None
    assert application.get_action_request(first.action_request_id) == superseded


def test_resolution_replay_requires_the_original_expected_revision() -> None:
    """A matching replay key with a wrong revision must fail closed."""

    public, services = _load_needs_input()
    factory = _Factory()
    application = _service(public, services, factory)
    request = application.publish_from_result(
        _evidence(public, task_id="task-a", input_revision=1, result_revision=1)
    )
    command = public.ResolveNeedsInput(
        action_request_id=request.action_request_id,
        expected_revision=Revision.initial(),
        idempotency_key="resolve-1",
        resolution_type="submit_correction",
        resolution_payload={"correction": "verified competitor evidence"},
    )

    first = application.resolve_needs_input(command)
    replay = application.resolve_needs_input(command)

    assert first.replayed is False
    assert replay.replayed is True
    assert replay.action_request == first.action_request

    wrong_revision = public.ResolveNeedsInput(
        action_request_id=request.action_request_id,
        expected_revision=Revision(1),
        idempotency_key="resolve-1",
        resolution_type="submit_correction",
        resolution_payload={"correction": "verified competitor evidence"},
    )
    with pytest.raises(public.NeedsInputRevisionConflictError):
        application.resolve_needs_input(wrong_revision)

    assert (
        application.get_action_request(request.action_request_id)
        == first.action_request
    )
    assert factory.uows[-1].commits == 0


def test_evidence_retains_deep_canonical_copies_of_source_and_conflict_mappings() -> (
    None
):
    """Nested caller mutations must not rewrite retained evidence projections."""

    public, _services = _load_needs_input()
    source = {
        "resourceKind": "source_version",
        "resourceId": "source-1",
        "locator": {"fieldPath": "facts.price", "tags": ["verified"]},
    }
    conflict = {
        "fieldPath": "facts.price",
        "values": [{"value": "10", "source": "source-1"}],
    }
    evidence = public.InsufficientResultEvidence(
        task_id=TaskId("task-a"),
        input_revision=Revision(1),
        result_revision=Revision(1),
        missing_information=("verified competitor evidence",),
        affected_stages=("product_positioning",),
        source_references=(source,),
        conflict_values=(conflict,),
    )

    cast(dict[str, object], source["locator"])["tags"] = [
        "verified",
        "caller-mutated",
    ]
    cast(list[dict[str, str]], conflict["values"])[0]["value"] = "caller-mutated"

    assert evidence.source_references[0]["locator"] == {
        "fieldPath": "facts.price",
        "tags": ["verified"],
    }
    assert evidence.conflict_values[0]["values"] == [
        {"value": "10", "source": "source-1"}
    ]
    json.dumps(evidence.source_references, ensure_ascii=False, allow_nan=False)
    json.dumps(evidence.conflict_values, ensure_ascii=False, allow_nan=False)


def test_evidence_rejects_non_json_and_oversized_mapping_projections() -> None:
    """Invalid or over-bound evidence never crosses the domain boundary."""

    public, _services = _load_needs_input()
    invalid_projections: tuple[
        tuple[dict[str, object], dict[str, object] | None], ...
    ] = (
        ({"value": object()}, None),
        ({}, {"value": float("nan")}),
        ({"value": "x" * 20000}, None),
    )
    for source, conflict in invalid_projections:
        with pytest.raises(ValueError):
            public.InsufficientResultEvidence(
                task_id=TaskId("task-a"),
                input_revision=Revision(1),
                result_revision=Revision(1),
                missing_information=("verified competitor evidence",),
                affected_stages=("product_positioning",),
                source_references=(source,) if source else (),
                conflict_values=(conflict,) if conflict else (),
            )


def test_recomposed_request_supersedes_current_per_task() -> None:
    public, services = _load_needs_input()
    factory = _Factory()
    application = _service(public, services, factory)
    first = application.publish_from_result(
        _evidence(public, task_id="task-a", input_revision=1, result_revision=1)
    )

    reloaded = _service(public, services, factory)
    assert reloaded.get_current_request(TaskId("task-a")) == first

    second = reloaded.publish_from_result(
        _evidence(public, task_id="task-a", input_revision=2, result_revision=2)
    )
    publication_uow = factory.uows[-1]
    assert second.action_request_id != first.action_request_id
    assert second.status.value == "open"
    assert reloaded.get_current_request(TaskId("task-a")) == second
    assert reloaded.get_action_request(first.action_request_id).status.value == (
        "superseded"
    )
    assert (
        reloaded.get_action_request(first.action_request_id).superseded_by
        == second.action_request_id
    )
    assert publication_uow.operations == ["save", "add"]

    other_task = reloaded.publish_from_result(
        _evidence(public, task_id="task-b", input_revision=1, result_revision=1)
    )
    assert reloaded.get_current_request(TaskId("task-a")) == second
    assert reloaded.get_current_request(TaskId("task-b")) == other_task


def test_publication_failure_rolls_back_request_and_supersession_together() -> None:
    public, services = _load_needs_input()
    factory = _Factory()
    application = _service(public, services, factory)
    first = application.publish_from_result(
        _evidence(public, task_id="task-a", input_revision=1, result_revision=1)
    )
    failing_factory = _Factory(fail_save=True)
    failing_factory.store.update(factory.store)

    with pytest.raises(public.NeedsInputApplicationError):
        _service(public, services, failing_factory).publish_from_result(
            _evidence(public, task_id="task-a", input_revision=2, result_revision=2)
        )

    assert failing_factory.store[first.action_request_id] == first
    assert failing_factory.uows[-1].commits == 0
    assert failing_factory.uows[-1].rollbacks == 1
