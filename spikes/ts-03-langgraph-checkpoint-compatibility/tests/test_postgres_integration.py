from __future__ import annotations

import os
from collections.abc import Iterator
from typing import cast
from uuid import uuid4

import psycopg
import pytest
from langgraph.checkpoint.postgres import PostgresSaver

from ts03_checkpoint.business_probe import BusinessTruthProbe
from ts03_checkpoint.config import business_connection, checkpoint_connection
from ts03_checkpoint.graph import build_graph
from ts03_checkpoint.harness import CheckpointHarness, ResumeRejected, RunIdentity
from ts03_checkpoint.reconciliation import (
    CheckpointMetadata,
    CompatibilityTuple,
    CurrentTruth,
    RecoveryRequest,
)
from ts03_checkpoint.setup import setup_checkpoint_store

pytestmark = pytest.mark.integration

COMPATIBILITY = CompatibilityTuple(
    workflow_definition_version="ts03-workflow-v1",
    graph_state_schema_version="ts03-state-v1",
    serializer_profile_version="langgraph-default-v1",
    checkpointer_package_version="langgraph-checkpoint-postgres-3.1.0",
    store_schema_version="vendor-current",
)


def _require_integration() -> None:
    if os.environ.get("TS03_RUN_INTEGRATION") != "1":
        pytest.skip("set TS03_RUN_INTEGRATION=1 after scripts/mvp0/verify")


@pytest.fixture(scope="module")
def checkpoint_url() -> str:
    _require_integration()
    connection = checkpoint_connection()
    try:
        setup_checkpoint_store(connection.uri)
    except psycopg.OperationalError as exc:
        pytest.fail(
            "Checkpoint DB is not reachable; run scripts/mvp0/up and scripts/mvp0/verify "
            f"before this explicit integration suite ({exc})"
        )
    return connection.uri


@pytest.fixture
def saver(checkpoint_url: str) -> Iterator[PostgresSaver]:
    with PostgresSaver.from_conn_string(checkpoint_url) as checkpointer:
        yield checkpointer


def _identities(label: str) -> tuple[RunIdentity, str]:
    suffix = uuid4().hex
    task_id = f"ts03-{label}-task-{suffix}"
    return RunIdentity.create(task_id=task_id, thread_id=f"ts03-{label}-thread-{suffix}"), suffix


def _checkpoint_metadata(
    identity: RunIdentity, *, input_version: str = "input-v1"
) -> CheckpointMetadata:
    return CheckpointMetadata(
        task_id=identity.task_id,
        thread_id=identity.thread_id,
        input_version=input_version,
        source_set_version="sources-v1",
        stage="review",
        review_package_version="review-v1",
        compatibility=COMPATIBILITY,
    )


def _current(identity: RunIdentity, *, input_version: str = "input-v1") -> CurrentTruth:
    return CurrentTruth(
        task_id=identity.task_id,
        thread_id=identity.thread_id,
        input_version=input_version,
        source_set_version="sources-v1",
        valid_stage="review",
        review_package_version="review-v1",
        compatibility=COMPATIBILITY,
    )


def _run_to_interrupt(saver: PostgresSaver, identity: RunIdentity):
    harness = CheckpointHarness(saver)
    outcome = harness.start(
        identity,
        input_version="input-v1",
        source_set_version="sources-v1",
        stage="review",
        review_package_version="review-v1",
        workflow_definition_version="ts03-workflow-v1",
        graph_state_schema_version="ts03-state-v1",
        serializer_profile_version="langgraph-default-v1",
    )
    assert outcome.interrupted is True
    return harness, outcome


def _checkpoint_count(saver: PostgresSaver, thread_id: str) -> int:
    return len(list(saver.list({"configurable": {"thread_id": thread_id}})))


def _delete_thread(saver: PostgresSaver, identity: RunIdentity) -> None:
    saver.delete_thread(identity.thread_id)


def test_graph_build_does_not_implicitly_setup_or_migrate(
    checkpoint_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden_setup(_: PostgresSaver) -> None:
        raise AssertionError("graph construction must not call PostgresSaver.setup")

    monkeypatch.setattr(PostgresSaver, "setup", forbidden_setup)
    with PostgresSaver.from_conn_string(checkpoint_url) as saver:
        build_graph(saver)


def test_checkpoint_database_role_and_business_database_are_separate(checkpoint_url: str) -> None:
    checkpoint = checkpoint_connection()
    business = business_connection()
    with psycopg.connect(checkpoint_url) as checkpoint_db:
        checkpoint_identity = checkpoint_db.execute(
            "SELECT current_database(), current_user, to_regclass('public.checkpoints')"
        ).fetchone()
    with psycopg.connect(business.uri) as business_db:
        business_identity = business_db.execute(
            "SELECT current_database(), current_user, to_regclass('public.checkpoints')"
        ).fetchone()
    assert checkpoint_identity is not None
    assert business_identity is not None
    assert checkpoint_identity[0] == checkpoint.database
    assert checkpoint_identity[1] == checkpoint.role
    assert business_identity[0] == business.database
    assert business_identity[1] == business.role
    assert checkpoint_identity[0] != business_identity[0]
    assert checkpoint_identity[1] != business_identity[1]
    assert checkpoint_identity[2] is not None
    assert business_identity[2] is None


def test_sync_interrupt_resume_isolated_and_uses_new_run_identity(saver: PostgresSaver) -> None:
    identity, _ = _identities("resume")
    harness, interrupted = _run_to_interrupt(saver, identity)
    before = _checkpoint_count(saver, identity.thread_id)
    probe = BusinessTruthProbe()
    resumed, decision = harness.resume(
        interrupted,
        checkpoint=_checkpoint_metadata(identity),
        current=_current(identity),
        request=RecoveryRequest(task_id=identity.task_id, thread_id=identity.thread_id),
    )
    assert decision.action == "resume_same_thread"
    assert resumed.interrupted is False
    assert resumed.state["runtime_result"] == "completed"
    assert resumed.identity.task_id == identity.task_id
    assert resumed.identity.thread_id == identity.thread_id
    assert resumed.identity.run_id != identity.run_id
    assert resumed.identity.attempt == identity.attempt + 1
    assert _checkpoint_count(saver, identity.thread_id) > before
    # This is the only place a test-only probe is allowed to model a business
    # commit, and it happens after reconciliation; the checkpoint never writes it.
    probe.commit(idempotency_key=f"{identity.task_id}:commit", result="accepted")
    assert probe.current_result == "accepted"
    _delete_thread(saver, identity)


def test_two_task_threads_do_not_cross_and_foreign_resume_is_rejected(saver: PostgresSaver) -> None:
    identity_a, _ = _identities("isolation-a")
    identity_b, _ = _identities("isolation-b")
    _run_to_interrupt(saver, identity_a)
    _run_to_interrupt(saver, identity_b)
    tuple_a = saver.get_tuple({"configurable": {"thread_id": identity_a.thread_id}})
    tuple_b = saver.get_tuple({"configurable": {"thread_id": identity_b.thread_id}})
    assert tuple_a is not None
    assert tuple_b is not None
    thread_a = cast(dict[str, str], tuple_a.config.get("configurable", {}))["thread_id"]
    thread_b = cast(dict[str, str], tuple_b.config.get("configurable", {}))["thread_id"]
    assert thread_a == identity_a.thread_id
    assert thread_b == identity_b.thread_id
    assert thread_a != thread_b

    # Reconciliation sees the foreign task before the graph is called.
    harness_a = CheckpointHarness(saver)
    foreign_current = _current(identity_b)
    foreign_request = RecoveryRequest(task_id=identity_b.task_id, thread_id=identity_b.thread_id)
    foreign_checkpoint = _checkpoint_metadata(identity_a)
    probe = BusinessTruthProbe()
    before = probe.snapshot()
    with pytest.raises(ResumeRejected) as rejected:
        harness_a.resume(
            _run_to_interrupt(saver, identity_a)[1],
            checkpoint=foreign_checkpoint,
            current=foreign_current,
            request=foreign_request,
        )
    assert rejected.value.decision.action == "reject_request"
    assert probe.snapshot() == before
    _delete_thread(saver, identity_a)
    _delete_thread(saver, identity_b)


@pytest.mark.parametrize(
    ("label", "current_kwargs", "expected_action"),
    [
        ("stale-input", {"input_version": "input-v2"}, "rerun_from_earliest_invalid_stage"),
        ("stale-review", {"review_package_version": "review-v2"}, "reject_request"),
    ],
)
def test_stale_checkpoint_is_refused_without_new_checkpoint_or_business_pollution(
    saver: PostgresSaver,
    label: str,
    current_kwargs: dict[str, str],
    expected_action: str,
) -> None:
    identity, _ = _identities(label)
    harness, interrupted = _run_to_interrupt(saver, identity)
    before_count = _checkpoint_count(saver, identity.thread_id)
    probe = BusinessTruthProbe()
    before_probe = probe.snapshot()
    with pytest.raises(ResumeRejected) as rejected:
        harness.resume(
            interrupted,
            checkpoint=_checkpoint_metadata(identity),
            current=CurrentTruth(
                task_id=identity.task_id,
                thread_id=identity.thread_id,
                input_version=current_kwargs.get("input_version", "input-v1"),
                source_set_version="sources-v1",
                valid_stage="review",
                review_package_version=current_kwargs.get("review_package_version", "review-v1"),
                compatibility=COMPATIBILITY,
            ),
            request=RecoveryRequest(task_id=identity.task_id, thread_id=identity.thread_id),
        )
    assert rejected.value.decision.action == expected_action
    assert _checkpoint_count(saver, identity.thread_id) == before_count
    assert probe.snapshot() == before_probe
    _delete_thread(saver, identity)


def test_incompatible_tuple_is_manual_recovery_before_graph(saver: PostgresSaver) -> None:
    identity, _ = _identities("incompatible")
    harness, interrupted = _run_to_interrupt(saver, identity)
    before_count = _checkpoint_count(saver, identity.thread_id)
    incompatible = CompatibilityTuple(
        workflow_definition_version="ts03-workflow-v0",
        graph_state_schema_version="ts03-state-v0",
        serializer_profile_version="langgraph-default-v0",
        checkpointer_package_version="langgraph-checkpoint-postgres-3.0.0",
        store_schema_version="vendor-old",
    )
    with pytest.raises(ResumeRejected) as rejected:
        harness.resume(
            interrupted,
            checkpoint=CheckpointMetadata(
                task_id=identity.task_id,
                thread_id=identity.thread_id,
                input_version="input-v1",
                source_set_version="sources-v1",
                stage="review",
                review_package_version="review-v1",
                compatibility=incompatible,
            ),
            current=_current(identity),
            request=RecoveryRequest(task_id=identity.task_id, thread_id=identity.thread_id),
        )
    assert rejected.value.decision.action == "manual_recovery_required"
    assert _checkpoint_count(saver, identity.thread_id) == before_count
    _delete_thread(saver, identity)
