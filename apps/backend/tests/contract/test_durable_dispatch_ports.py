"""Contract tests for the private Durable Dispatch persistence ports."""

from __future__ import annotations

from inspect import getattr_static, getmro, signature
from types import TracebackType
from typing import cast, get_type_hints

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWork, UnitOfWorkState
from ai_ecommerce_agent.modules.durable_dispatch import public
from ai_ecommerce_agent.modules.durable_dispatch.application import (
    DurableDispatchUnitOfWork,
    DurableDispatchUnitOfWorkFactory,
    WorkIntentRepositoryPort,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.lease_commands import (
    ClaimNextWorkIntent,
    HeartbeatWorkIntentLease,
)
from ai_ecommerce_agent.modules.durable_dispatch.application.ports import (
    WorkIntentLeaseRepositoryPort,
)
from ai_ecommerce_agent.modules.durable_dispatch.domain.identity import DispatchId
from ai_ecommerce_agent.modules.durable_dispatch.domain.snapshots import (
    WorkIntentSnapshot,
)
from ai_ecommerce_agent.shared_kernel import Revision

pytestmark = pytest.mark.contract


class _RepositoryDouble:
    def get(self, dispatch_id: DispatchId) -> WorkIntentSnapshot | None:
        del dispatch_id
        return None

    def add(self, snapshot: WorkIntentSnapshot) -> None:
        del snapshot

    def save(
        self,
        snapshot: WorkIntentSnapshot,
        *,
        expected_revision: Revision,
    ) -> None:
        del snapshot, expected_revision

    def claim_next(self, command: ClaimNextWorkIntent) -> WorkIntentSnapshot | None:
        del command
        return None

    def heartbeat(self, command: HeartbeatWorkIntentLease) -> WorkIntentSnapshot | None:
        del command
        return None


class _UnitOfWorkDouble:
    @property
    def state(self) -> UnitOfWorkState:
        return UnitOfWorkState.NEW

    def __enter__(self) -> _UnitOfWorkDouble:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc_value, traceback

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def close(self) -> None:
        pass

    @property
    def work_intents(self) -> WorkIntentRepositoryPort:
        return _RepositoryDouble()

    @property
    def work_intent_leases(self) -> WorkIntentLeaseRepositoryPort:
        return _RepositoryDouble()


class _FactoryDouble:
    def __call__(self) -> DurableDispatchUnitOfWork:
        return cast(DurableDispatchUnitOfWork, _UnitOfWorkDouble())


def test_application_package_exports_only_the_three_private_ports() -> None:
    from ai_ecommerce_agent.modules.durable_dispatch import application

    assert application.__all__ == [
        "DurableDispatchUnitOfWork",
        "DurableDispatchUnitOfWorkFactory",
        "WorkIntentRepositoryPort",
    ]
    assert application.DurableDispatchUnitOfWork is DurableDispatchUnitOfWork
    assert (
        application.DurableDispatchUnitOfWorkFactory is DurableDispatchUnitOfWorkFactory
    )
    assert application.WorkIntentRepositoryPort is WorkIntentRepositoryPort


def test_repository_port_has_exact_typed_cas_methods() -> None:
    assert all(
        callable(getattr(WorkIntentRepositoryPort, name))
        for name in ("get", "add", "save")
    )
    assert not any(
        hasattr(WorkIntentRepositoryPort, name)
        for name in (
            "commit",
            "rollback",
            "close",
            "begin",
            "flush",
            "execute_sql",
            "get_repository",
        )
    )

    get_method = WorkIntentRepositoryPort.get
    assert list(signature(get_method).parameters) == ["self", "dispatch_id"]
    assert get_type_hints(get_method) == {
        "dispatch_id": DispatchId,
        "return": WorkIntentSnapshot | None,
    }

    add_method = WorkIntentRepositoryPort.add
    assert list(signature(add_method).parameters) == ["self", "snapshot"]
    assert get_type_hints(add_method) == {
        "snapshot": WorkIntentSnapshot,
        "return": type(None),
    }

    save_method = WorkIntentRepositoryPort.save
    save_signature = signature(save_method)
    assert list(save_signature.parameters) == [
        "self",
        "snapshot",
        "expected_revision",
    ]
    assert (
        save_signature.parameters["expected_revision"].kind
        is save_signature.parameters["expected_revision"].kind.KEYWORD_ONLY
    )
    assert get_type_hints(save_method) == {
        "snapshot": WorkIntentSnapshot,
        "expected_revision": Revision,
        "return": type(None),
    }

    assert all(
        callable(getattr(WorkIntentLeaseRepositoryPort, name))
        for name in ("claim_next", "heartbeat")
    )
    claim_method = WorkIntentLeaseRepositoryPort.claim_next
    assert list(signature(claim_method).parameters) == ["self", "command"]
    assert get_type_hints(claim_method) == {
        "command": ClaimNextWorkIntent,
        "return": WorkIntentSnapshot | None,
    }
    heartbeat_method = WorkIntentLeaseRepositoryPort.heartbeat
    assert list(signature(heartbeat_method).parameters) == ["self", "command"]
    assert get_type_hints(heartbeat_method) == {
        "command": HeartbeatWorkIntentLease,
        "return": WorkIntentSnapshot | None,
    }
    assert not any(
        hasattr(WorkIntentLeaseRepositoryPort, name)
        for name in ("commit", "rollback", "close", "session", "execute_sql")
    )


def test_specialized_uow_reuses_shared_lifecycle_and_one_typed_repository() -> None:
    assert UnitOfWork in getmro(DurableDispatchUnitOfWork)
    work_intents = getattr_static(DurableDispatchUnitOfWork, "work_intents")
    assert isinstance(work_intents, property)
    assert work_intents.fget is not None
    assert get_type_hints(work_intents.fget)["return"] is WorkIntentRepositoryPort
    work_intent_leases = getattr_static(DurableDispatchUnitOfWork, "work_intent_leases")
    assert isinstance(work_intent_leases, property)
    assert work_intent_leases.fget is not None
    assert (
        get_type_hints(work_intent_leases.fget)["return"]
        is WorkIntentLeaseRepositoryPort
    )
    assert not any(
        hasattr(DurableDispatchUnitOfWork, name)
        for name in (
            "session",
            "engine",
            "registry",
            "get_repository",
            "execute_sql",
        )
    )


def test_factory_is_runtime_checkable_and_returns_fresh_typed_uow() -> None:
    factory_signature = signature(DurableDispatchUnitOfWorkFactory.__call__)
    assert list(factory_signature.parameters) == ["self"]
    assert get_type_hints(DurableDispatchUnitOfWorkFactory.__call__) == {
        "return": DurableDispatchUnitOfWork,
    }
    assert isinstance(_RepositoryDouble(), WorkIntentRepositoryPort)
    assert isinstance(_UnitOfWorkDouble(), DurableDispatchUnitOfWork)
    factory = _FactoryDouble()
    assert isinstance(factory, DurableDispatchUnitOfWorkFactory)
    first, second = factory(), factory()
    assert first is not second
    assert isinstance(first, DurableDispatchUnitOfWork)
    assert isinstance(second, DurableDispatchUnitOfWork)


def test_private_ports_do_not_leak_through_stable_public_facade() -> None:
    for name in (
        "DurableDispatchUnitOfWork",
        "DurableDispatchUnitOfWorkFactory",
        "WorkIntentRepositoryPort",
        "WorkIntentLeaseRepositoryPort",
    ):
        assert not hasattr(public, name)
