"""Application Unit of Work lifecycle and port-contract tests."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pytest
from sqlalchemy.orm import Session

from ai_ecommerce_agent.application.errors import UnitOfWorkStateError
from ai_ecommerce_agent.application.ports import UnitOfWork, UnitOfWorkState
from ai_ecommerce_agent.platform import postgres as postgres_facade
from ai_ecommerce_agent.platform.postgres.uow import PostgresUnitOfWork

pytestmark = [pytest.mark.unit, pytest.mark.contract]


def test_postgres_facade_exposes_only_engine_and_uow_factory() -> None:
    """The public adapter facade never leaks the concrete UoW/Session seam."""

    assert postgres_facade.__all__ == [
        "PostgresEngineConfig",
        "PostgresUnitOfWorkFactory",
        "create_postgres_engine",
    ]
    assert not hasattr(postgres_facade, "PostgresUnitOfWork")


class _RecordingSession:
    """Small session double for lifecycle tests; it does not model SQL."""

    def __init__(self) -> None:
        self.begin_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    def begin(self) -> None:
        self.begin_calls += 1

    def commit(self) -> None:
        self.commit_calls += 1

    def rollback(self) -> None:
        self.rollback_calls += 1

    def close(self) -> None:
        self.close_calls += 1


def _factory() -> tuple[Callable[[], Session], list[_RecordingSession]]:
    sessions: list[_RecordingSession] = []

    def create() -> Session:
        session = _RecordingSession()
        sessions.append(session)
        return cast(Session, session)

    return create, sessions


def _uow() -> tuple[PostgresUnitOfWork, _RecordingSession]:
    factory, sessions = _factory()
    uow = PostgresUnitOfWork(factory)
    return uow, sessions[0]


def test_uow_port_is_framework_neutral_and_enters_active() -> None:
    """The concrete adapter satisfies the application-owned port contract."""

    uow, session = _uow()

    assert isinstance(uow, UnitOfWork)
    assert uow.state is UnitOfWorkState.NEW
    with uow as entered:
        assert entered is uow
        assert uow.state is UnitOfWorkState.ACTIVE

    assert session.begin_calls == 1
    assert session.rollback_calls == 1
    assert session.close_calls == 1
    assert uow.state is UnitOfWorkState.CLOSED


def test_context_exit_never_auto_commits() -> None:
    """Leaving an uncommitted scope rolls back and closes resources."""

    uow, session = _uow()

    with uow:
        pass

    assert session.commit_calls == 0
    assert session.rollback_calls == 1
    assert uow.state is UnitOfWorkState.CLOSED


def test_explicit_commit_is_single_successful_final_result() -> None:
    """Commit is explicit and a one-shot UoW rejects reuse."""

    uow, session = _uow()
    with uow:
        uow.commit()
        assert uow.state is UnitOfWorkState.COMMITTED
        assert session.commit_calls == 1

        with pytest.raises(UnitOfWorkStateError):
            uow.commit()
        with pytest.raises(UnitOfWorkStateError):
            uow.rollback()

    assert session.close_calls == 1
    assert uow.state is UnitOfWorkState.CLOSED


def test_explicit_rollback_rejects_follow_up_transaction_operations() -> None:
    """Rollback makes the UoW unusable for a second business transaction."""

    uow, session = _uow()
    with uow:
        uow.rollback()
        assert uow.state is UnitOfWorkState.ROLLED_BACK
        with pytest.raises(UnitOfWorkStateError):
            uow.commit()
        with pytest.raises(UnitOfWorkStateError):
            uow.rollback()

    assert session.rollback_calls == 1
    assert uow.state is UnitOfWorkState.CLOSED


def test_exception_exit_rolls_back_and_preserves_exception() -> None:
    """Application failures never turn into an accidental commit."""

    uow, session = _uow()

    with pytest.raises(RuntimeError, match="boom"):
        with uow:
            raise RuntimeError("boom")

    assert session.commit_calls == 0
    assert session.rollback_calls == 1
    assert session.close_calls == 1
    assert uow.state is UnitOfWorkState.CLOSED


def test_closed_uow_cannot_be_entered_or_manually_reused() -> None:
    """Close is terminal for a one-shot lifecycle object."""

    uow, session = _uow()
    uow.close()
    assert session.close_calls == 1
    assert uow.state is UnitOfWorkState.CLOSED

    with pytest.raises(UnitOfWorkStateError):
        uow.__enter__()
    with pytest.raises(UnitOfWorkStateError):
        uow.commit()
    with pytest.raises(UnitOfWorkStateError):
        uow.rollback()


def test_rollback_failure_still_closes_session() -> None:
    """Cleanup closes a Session even when rollback itself fails."""

    uow, session = _uow()
    original_rollback = session.rollback

    def fail_rollback() -> None:
        original_rollback()
        raise RuntimeError("rollback failed")

    session.rollback = fail_rollback
    with pytest.raises(RuntimeError, match="rollback failed"):
        with uow:
            pass

    assert session.close_calls == 1
    assert uow.state is UnitOfWorkState.CLOSED


def test_commit_failure_rolls_back_and_closes_session() -> None:
    """A failed final commit cannot leave a reusable Session behind."""

    uow, session = _uow()

    def fail_commit() -> None:
        raise RuntimeError("commit failed")

    session.commit = fail_commit
    with pytest.raises(RuntimeError, match="commit failed"):
        with uow:
            uow.commit()

    assert session.rollback_calls == 1
    assert session.close_calls == 1
    assert uow.state is UnitOfWorkState.CLOSED


def test_factory_returns_fresh_uow_instances() -> None:
    """Every command receives a distinct UoW and private Session object."""

    factory, sessions = _factory()

    def make_uow() -> PostgresUnitOfWork:
        return PostgresUnitOfWork(factory)

    first = make_uow()
    second = make_uow()

    assert first is not second
    assert sessions[0] is not sessions[1]
    first.close()
    second.close()
