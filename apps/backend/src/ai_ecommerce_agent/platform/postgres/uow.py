"""Concrete one-shot Unit of Work backed by a private SQLAlchemy Session."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Final

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from ai_ecommerce_agent.application.errors import UnitOfWorkStateError
from ai_ecommerce_agent.application.ports import UnitOfWorkState

SessionFactory = Callable[[], Session]


def _session_factory_from_engine(engine: Engine) -> SessionFactory:
    """Create the adapter-private long-lived Session factory."""

    factory: sessionmaker[Session] = sessionmaker(
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )
    return factory


class PostgresUnitOfWork:
    """A short, explicit SQLAlchemy transaction with disposable lifecycle.

    ``_session`` is deliberately private to this platform adapter.  Future
    typed repositories owned by a business module may be composed inside this
    package, but no application-facing object receives a raw Session or gets
    transaction-control methods from a repository.
    """

    _NEW: Final[UnitOfWorkState] = UnitOfWorkState.NEW

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session = session_factory()
        self._state = self._NEW

    @property
    def state(self) -> UnitOfWorkState:
        """Return the current one-shot lifecycle state."""

        return self._state

    def __enter__(self) -> PostgresUnitOfWork:
        self._require_state(UnitOfWorkState.NEW, operation="enter")
        try:
            self._session.begin()
        except BaseException:
            self._discard_after_failure()
            raise
        self._state = UnitOfWorkState.ACTIVE
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, traceback
        rollback_error: BaseException | None = None
        close_error: BaseException | None = None
        if self._state is UnitOfWorkState.ACTIVE:
            try:
                self._rollback_active()
            except BaseException as error:
                rollback_error = error
        if self._state is not UnitOfWorkState.CLOSED:
            try:
                self.close()
            except BaseException as error:
                close_error = error
        # Preserve a failure raised by the application body. When the body
        # completed normally, expose the first cleanup failure and ensure a
        # close failure cannot hide an earlier rollback failure.
        if exc_value is None:
            if rollback_error is not None:
                if close_error is not None:
                    raise rollback_error from close_error
                raise rollback_error
            if close_error is not None:
                raise close_error

    def commit(self) -> None:
        """Commit exactly once, disposing the UoW if the commit fails."""

        self._require_state(UnitOfWorkState.ACTIVE, operation="commit")
        try:
            self._session.commit()
        except BaseException as commit_error:
            # SQLAlchemy requires a rollback after a failed flush/commit before
            # the Session can be closed.  The failed UoW is never reusable.
            rollback_error: BaseException | None = None
            try:
                self._rollback_active()
            except BaseException as error:
                rollback_error = error
            try:
                self.close()
            except BaseException as close_error:
                raise commit_error from close_error
            if rollback_error is not None:
                raise commit_error from rollback_error
            raise commit_error
        self._state = UnitOfWorkState.COMMITTED

    def rollback(self) -> None:
        """Explicitly roll back the active transaction without auto-closing."""

        self._require_state(UnitOfWorkState.ACTIVE, operation="rollback")
        self._rollback_active()

    def close(self) -> None:
        """Close the private Session and release any checked-out connection."""

        if self._state is UnitOfWorkState.CLOSED:
            return
        rollback_error: BaseException | None = None
        if self._state is UnitOfWorkState.ACTIVE:
            try:
                self._rollback_active()
            except BaseException as error:
                rollback_error = error
        try:
            self._session.close()
        finally:
            self._state = UnitOfWorkState.CLOSED
        if rollback_error is not None:
            raise rollback_error

    def _rollback_active(self) -> None:
        """Rollback an active transaction and move to ROLLED_BACK."""

        if self._state is not UnitOfWorkState.ACTIVE:
            return
        try:
            self._session.rollback()
        except BaseException:
            self._state = UnitOfWorkState.ROLLED_BACK
            raise
        self._state = UnitOfWorkState.ROLLED_BACK

    def _discard_after_failure(self) -> None:
        """Close a Session when transaction setup itself fails."""

        try:
            self._session.close()
        finally:
            self._state = UnitOfWorkState.CLOSED

    def _require_state(self, expected: UnitOfWorkState, *, operation: str) -> None:
        """Raise a project-owned error for an invalid lifecycle operation."""

        if self._state is expected:
            return
        context = {"operation": operation, "state": self._state.value}
        if self._state is UnitOfWorkState.CLOSED:
            raise UnitOfWorkStateError("uow_closed", context)
        if operation == "commit" and self._state is UnitOfWorkState.COMMITTED:
            raise UnitOfWorkStateError("uow_already_committed", context)
        if operation == "rollback" and self._state is UnitOfWorkState.COMMITTED:
            raise UnitOfWorkStateError("uow_already_committed", context)
        if (
            operation in {"commit", "rollback"}
            and self._state is UnitOfWorkState.ROLLED_BACK
        ):
            raise UnitOfWorkStateError("uow_already_rolled_back", context)
        if expected is UnitOfWorkState.ACTIVE:
            raise UnitOfWorkStateError("uow_not_active", context)
        raise UnitOfWorkStateError("uow_invalid_state", context)


class PostgresUnitOfWorkFactory:
    """Long-lived composition dependency producing fresh UoW instances."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    @classmethod
    def from_engine(cls, engine: Engine) -> PostgresUnitOfWorkFactory:
        """Compose a factory while keeping the Session factory platform-private."""

        return cls(_session_factory_from_engine(engine))

    def __call__(self) -> PostgresUnitOfWork:
        """Create a new UoW with a fresh private Session."""

        return PostgresUnitOfWork(self._session_factory)


__all__ = ["PostgresUnitOfWork", "PostgresUnitOfWorkFactory"]
