"""Representative TS-01 PostgreSQL transaction and fencing evidence."""

from __future__ import annotations

from datetime import UTC, datetime
from threading import Event, Thread

import pytest
from sqlalchemy import insert
from sqlalchemy.engine import Connection

from ts01_compatibility.harness import (
    CommitInjectedFailure,
    FencingRejected,
    PostgresCompatibilityHarness,
    database_url_from_environment,
)
from ts01_compatibility.migration import run_migration
from ts01_compatibility.schema import work_intents

pytestmark = pytest.mark.integration


def _seed_work_item(harness: PostgresCompatibilityHarness, work_item_id: str) -> None:
    with harness.engine.begin() as connection:
        connection.execute(
            insert(work_intents).values(
                id=work_item_id,
                status="available",
                fencing_token=0,
            )
        )


def _wait(event: Event, label: str) -> None:
    if not event.wait(timeout=10):
        raise AssertionError(f"timed out waiting for deterministic coordination point: {label}")


def test_fresh_migration_and_downgrade_leave_only_dedicated_schema(
    harness: PostgresCompatibilityHarness,
) -> None:
    assert harness.dedicated_schema_exists()
    assert harness.read_work_item("migration-probe") is None
    run_migration(database_url_from_environment(), "base")
    assert harness.dedicated_schema_exists()
    run_migration(database_url_from_environment(), "head")
    assert harness.dedicated_schema_exists()
    assert harness.checked_out_connections() == 0


def test_two_connections_poll_and_claim_without_double_claim(
    harness: PostgresCompatibilityHarness,
) -> None:
    _seed_work_item(harness, "claim-race")
    first_lock_acquired = Event()
    second_poll_completed = Event()
    results: dict[str, object] = {}
    errors: list[BaseException] = []

    def first_worker() -> None:
        def hold_lock(connection: Connection) -> None:
            del connection
            first_lock_acquired.set()
            _wait(second_poll_completed, "second worker poll")

        try:
            results["first"] = harness.claim("worker-a", before_commit=hold_lock)
        except BaseException as error:
            errors.append(error)
            first_lock_acquired.set()

    def second_worker() -> None:
        try:
            _wait(first_lock_acquired, "first worker row lock")
            results["second"] = harness.claim("worker-b")
        except BaseException as error:
            errors.append(error)
        finally:
            second_poll_completed.set()

    thread_a = Thread(target=first_worker)
    thread_b = Thread(target=second_worker)
    thread_a.start()
    thread_b.start()
    thread_a.join(timeout=15)
    thread_b.join(timeout=15)
    assert not thread_a.is_alive()
    assert not thread_b.is_alive()
    assert errors == []

    first = results["first"]
    second = results["second"]
    assert first is not None
    assert second is None
    assert harness.checked_out_connections() == 0


def test_lease_takeover_gets_higher_token_and_stale_commit_is_rejected(
    harness: PostgresCompatibilityHarness,
) -> None:
    _seed_work_item(harness, "fence-race")
    first = harness.claim("worker-a", lease_seconds=30)
    assert first is not None
    harness.expire_lease(first)

    second = harness.claim("worker-b", lease_seconds=30)
    assert second is not None
    assert second.fencing_token > first.fencing_token

    # The takeover owner is still active and has not committed yet. The first
    # holder's stale token must be rejected by fencing, not by a completed
    # status check, and must not create partial Current Truth.
    with pytest.raises(FencingRejected):
        harness.commit_current_truth(first, "stale-result")
    assert harness.read_current_truth(second.work_item_id) is None
    work_item_after_stale = harness.read_work_item(second.work_item_id)
    assert work_item_after_stale is not None
    assert work_item_after_stale["status"] == "claimed"
    assert work_item_after_stale["holder_id"] == "worker-b"
    assert work_item_after_stale["fencing_token"] == second.fencing_token

    harness.commit_current_truth(second, "current-result")
    truth = harness.read_current_truth(second.work_item_id)
    work_item = harness.read_work_item(second.work_item_id)
    assert truth is not None
    assert truth["value"] == "current-result"
    assert truth["committed_fencing_token"] == second.fencing_token
    assert work_item is not None
    assert work_item["status"] == "completed"
    assert work_item["holder_id"] == "worker-b"


def test_atomic_failure_rolls_back_then_forward_repair_has_zero_partial_truth(
    harness: PostgresCompatibilityHarness,
) -> None:
    _seed_work_item(harness, "repair-path")
    claim = harness.claim("worker-repair", lease_seconds=30)
    assert claim is not None

    with pytest.raises(CommitInjectedFailure):
        harness.commit_current_truth(
            claim,
            "value-written-before-fault",
            inject_failure_after_write=True,
        )

    work_item_after_failure = harness.read_work_item(claim.work_item_id)
    assert harness.read_current_truth(claim.work_item_id) is None
    assert work_item_after_failure is not None
    assert work_item_after_failure["status"] == "claimed"
    assert work_item_after_failure["fencing_token"] == claim.fencing_token

    harness.commit_current_truth(claim, "forward-repaired-value", revision=2)
    repaired_truth = harness.read_current_truth(claim.work_item_id)
    assert repaired_truth is not None
    assert repaired_truth["value"] == "forward-repaired-value"
    assert repaired_truth["revision"] == 2
    assert harness.checked_out_connections() == 0


def test_claim_and_commit_use_aware_utc_values(harness: PostgresCompatibilityHarness) -> None:
    _seed_work_item(harness, "timestamp-probe")
    claim = harness.claim("worker-time", lease_seconds=30)
    assert claim is not None
    assert claim.lease_expires_at.tzinfo is not None
    assert claim.lease_expires_at > datetime.now(UTC)
