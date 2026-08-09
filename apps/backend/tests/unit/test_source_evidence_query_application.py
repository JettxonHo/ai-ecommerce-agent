"""Unit evidence for the Source immutable-read application service."""

from __future__ import annotations

from datetime import UTC, datetime
from types import TracebackType
from typing import Any, Self, cast

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWorkState
from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceConstraintError,
    SourceEvidenceError,
    SourceEvidenceOwnershipError,
    SourceEvidencePersistenceError,
    SourceEvidenceRevisionConflictError,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceEvidenceUnitOfWork,
    SourceEvidenceUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.source_evidence.application.query_services import (
    SourceEvidenceQueryApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceAssociationMembershipState,
    SourceProcessingStatus,
    SourceVersion,
    SourceVersionProcessing,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.modules.source_evidence.public import (
    GetSourceAssociation,
    GetSourceVersion,
    SourceAssociationError,
    SourceAssociationSnapshot,
    SourceVersionSnapshot,
)
from ai_ecommerce_agent.shared_kernel import (
    ProjectError,
    Revision,
    SourceAssociationId,
    SourceId,
    SourceVersionId,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit

NOW = datetime(2026, 8, 9, 1, 0, tzinfo=UTC)
TASK = TaskId("task-query")
FOREIGN_TASK = TaskId("task-foreign")
SOURCE = SourceId("source-query")
VERSION_ID = SourceVersionId("source-version-query")
ASSOCIATION_ID = SourceAssociationId("association-query")


def _version() -> SourceVersion:
    return SourceVersion.create(VERSION_ID, SOURCE, VersionNumber(2))


def _processing() -> SourceVersionProcessing:
    return SourceVersionProcessing(
        source_version_id=VERSION_ID,
        status=SourceProcessingStatus.READY,
        revision=Revision(3),
        failure_summary=None,
        updated_at=NOW,
    )


def _association(
    state: SourceAssociationMembershipState = SourceAssociationMembershipState.ACTIVE,
) -> TaskSourceAssociation:
    return TaskSourceAssociation(
        source_association_id=ASSOCIATION_ID,
        task_id=TASK,
        source_id=SOURCE,
        source_version_id=VERSION_ID,
        membership_state=state,
        revision=Revision(4),
        replaced_by_association_id=(
            SourceAssociationId("association-replacement")
            if state is SourceAssociationMembershipState.REPLACED
            else None
        ),
    )


class _VersionRepository:
    def __init__(
        self,
        owner: _FakeUow,
        value: SourceVersion | None,
        error: BaseException | None,
    ) -> None:
        self._owner = owner
        self._value = value
        self._error = error

    def get(self, source_version_id: SourceVersionId) -> SourceVersion | None:
        self._owner.calls.append(("source_versions.get", source_version_id))
        if self._error is not None:
            raise self._error
        return self._value

    def add(self, version: SourceVersion) -> None:
        del version
        raise AssertionError("query must not add Source Versions")


class _ProcessingRepository:
    def __init__(
        self,
        owner: _FakeUow,
        value: SourceVersionProcessing | None,
        error: BaseException | None,
    ) -> None:
        self._owner = owner
        self._value = value
        self._error = error

    def get(self, source_version_id: SourceVersionId) -> SourceVersionProcessing | None:
        self._owner.calls.append(("processing.get", source_version_id))
        if self._error is not None:
            raise self._error
        return self._value

    def add(self, processing: SourceVersionProcessing) -> None:
        del processing
        raise AssertionError("query must not add processing rows")

    def save(
        self,
        processing: SourceVersionProcessing,
        *,
        expected_revision: Revision,
    ) -> None:
        del processing, expected_revision
        raise AssertionError("query must not save processing rows")


class _AssociationRepository:
    def __init__(
        self,
        owner: _FakeUow,
        value: TaskSourceAssociation | None,
        error: BaseException | None,
    ) -> None:
        self._owner = owner
        self._value = value
        self._error = error

    def get(
        self, source_association_id: SourceAssociationId
    ) -> TaskSourceAssociation | None:
        self._owner.calls.append(("associations.get", source_association_id))
        if self._error is not None:
            raise self._error
        return self._value

    def add(self, association: TaskSourceAssociation) -> None:
        del association
        raise AssertionError("query must not add associations")

    def save(
        self,
        association: TaskSourceAssociation,
        *,
        expected_revision: Revision,
    ) -> None:
        del association, expected_revision
        raise AssertionError("query must not save associations")


class _FakeUow:
    def __init__(
        self,
        *,
        source_version: SourceVersion | None = None,
        processing: SourceVersionProcessing | None = None,
        association: TaskSourceAssociation | None = None,
        version_error: BaseException | None = None,
        processing_error: BaseException | None = None,
        association_error: BaseException | None = None,
        enter_error: BaseException | None = None,
    ) -> None:
        self.calls: list[tuple[str, object]] = []
        self.commits = 0
        self.rollbacks = 0
        self.close_calls = 0
        self._state = UnitOfWorkState.NEW
        self._enter_error = enter_error
        self.source_versions = _VersionRepository(self, source_version, version_error)
        self.source_version_processing = _ProcessingRepository(
            self, processing, processing_error
        )
        self.source_associations = _AssociationRepository(
            self, association, association_error
        )

    @property
    def state(self) -> UnitOfWorkState:
        return self._state

    def __enter__(self) -> Self:
        if self._enter_error is not None:
            raise self._enter_error
        assert self._state is UnitOfWorkState.NEW
        self._state = UnitOfWorkState.ACTIVE
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc_value, traceback
        if self._state is UnitOfWorkState.ACTIVE:
            self.rollback()
        self.close()

    def commit(self) -> None:
        self.commits += 1
        raise AssertionError("query must not commit")

    def rollback(self) -> None:
        self.rollbacks += 1
        self._state = UnitOfWorkState.ROLLED_BACK

    def close(self) -> None:
        self.close_calls += 1
        self._state = UnitOfWorkState.CLOSED


class _Factory:
    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.uows: list[_FakeUow] = []

    def __call__(self) -> SourceEvidenceUnitOfWork:
        uow = _FakeUow(**self.kwargs)
        self.uows.append(uow)
        return cast(SourceEvidenceUnitOfWork, uow)


def _service(factory: _Factory) -> SourceEvidenceQueryApplicationService:
    return SourceEvidenceQueryApplicationService(
        cast(SourceEvidenceUnitOfWorkFactory, factory)
    )


def test_source_version_query_composes_identity_and_processing_without_commit() -> None:
    factory = _Factory(source_version=_version(), processing=_processing())

    result = _service(factory).get_source_version(GetSourceVersion(VERSION_ID))

    assert isinstance(result, SourceVersionSnapshot)
    assert result.source_id is SOURCE
    assert result.source_version_id is VERSION_ID
    assert result.version_number == VersionNumber(2)
    assert result.processing_status.value == "ready"
    assert result.processing_revision == Revision(3)
    assert result.updated_at == NOW
    uow = factory.uows[0]
    assert [name for name, _ in uow.calls] == [
        "source_versions.get",
        "processing.get",
    ]
    assert uow.commits == 0
    assert uow.rollbacks == 1
    assert uow.close_calls == 1


@pytest.mark.parametrize("missing", ["version", "processing"])
def test_source_version_query_missing_composite_member_is_typed_not_found(
    missing: str,
) -> None:
    factory = _Factory(
        source_version=None if missing == "version" else _version(),
        processing=None if missing == "processing" else _processing(),
    )

    with pytest.raises(SourceEvidenceError) as raised:
        _service(factory).get_source_version(GetSourceVersion(VERSION_ID))

    error = raised.value
    assert error.error_code == "not_found"
    assert error.category == "source_evidence"
    assert error.retryability is False
    assert error.relevant_reference is VERSION_ID
    assert error.recovery_hint == "refresh"
    assert factory.uows[0].commits == 0


@pytest.mark.parametrize(
    "state",
    list(SourceAssociationMembershipState),
)
def test_association_query_returns_each_accepted_membership_state_without_commit(
    state: SourceAssociationMembershipState,
) -> None:
    factory = _Factory(association=_association(state))

    result = _service(factory).get_source_association(
        GetSourceAssociation(TASK, ASSOCIATION_ID)
    )

    assert isinstance(result, SourceAssociationSnapshot)
    assert result.source_association_id is ASSOCIATION_ID
    assert result.task_id is TASK
    assert result.membership_state is state
    uow = factory.uows[0]
    assert [name for name, _ in uow.calls] == ["associations.get"]
    assert uow.commits == 0
    assert uow.rollbacks == 1
    assert uow.close_calls == 1


def test_association_query_missing_is_typed_not_found() -> None:
    factory = _Factory(association=None)

    with pytest.raises(SourceAssociationError) as raised:
        _service(factory).get_source_association(
            GetSourceAssociation(TASK, ASSOCIATION_ID)
        )

    error = raised.value
    assert error.error_code == "not_found"
    assert error.category == "source_association"
    assert error.retryability is False
    assert error.relevant_reference is ASSOCIATION_ID
    assert error.recovery_hint == "refresh"
    assert factory.uows[0].commits == 0


def test_association_query_foreign_task_is_typed_ownership_conflict() -> None:
    factory = _Factory(association=_association())

    with pytest.raises(SourceAssociationError) as raised:
        _service(factory).get_source_association(
            GetSourceAssociation(FOREIGN_TASK, ASSOCIATION_ID)
        )

    error = raised.value
    assert error.error_code == "ownership_conflict"
    assert error.category == "source_association"
    assert error.retryability is False
    assert error.relevant_reference is ASSOCIATION_ID
    assert error.recovery_hint == "refresh"
    assert factory.uows[0].commits == 0


def test_association_root_persistence_error_maps_to_retryable_public_error() -> None:
    error = SourceEvidencePersistenceError()
    factory = _Factory(association_error=error)

    with pytest.raises(SourceAssociationError) as raised:
        _service(factory).get_source_association(
            GetSourceAssociation(TASK, ASSOCIATION_ID)
        )

    mapped = raised.value
    assert mapped.error_code == "persistence_error"
    assert mapped.category == "source_association"
    assert mapped.retryability is True
    assert mapped.relevant_reference is ASSOCIATION_ID
    assert mapped.recovery_hint == "retry_later"
    assert mapped.__cause__ is error
    assert factory.uows[0].commits == 0


@pytest.mark.parametrize(
    "error",
    [
        SourceEvidenceRevisionConflictError(
            resource="source_version",
            identity="source-version-query",
            expected_revision=Revision(2),
        ),
        SourceEvidenceOwnershipError(
            resource="source_version", constraint_name="owner_constraint"
        ),
        SourceEvidenceConstraintError(constraint_name="other_constraint"),
    ],
)
def test_semantic_source_persistence_errors_propagate_unchanged(
    error: BaseException,
) -> None:
    factory = _Factory(version_error=error)

    with pytest.raises(type(error)) as raised:
        _service(factory).get_source_version(GetSourceVersion(VERSION_ID))

    assert raised.value is error
    assert factory.uows[0].commits == 0


def test_root_source_persistence_error_maps_to_retryable_public_error() -> None:
    error = SourceEvidencePersistenceError()
    factory = _Factory(version_error=error)

    with pytest.raises(SourceEvidenceError) as raised:
        _service(factory).get_source_version(GetSourceVersion(VERSION_ID))

    mapped = raised.value
    assert mapped.error_code == "persistence_error"
    assert mapped.category == "source_evidence"
    assert mapped.retryability is True
    assert mapped.relevant_reference is VERSION_ID
    assert mapped.recovery_hint == "retry_later"
    assert mapped.__cause__ is error


@pytest.mark.parametrize(
    "error", [ProjectError.from_context("other", "failure"), RuntimeError("boom")]
)
def test_unrelated_errors_propagate_unchanged(error: BaseException) -> None:
    factory = _Factory(version_error=error)

    with pytest.raises(type(error)) as raised:
        _service(factory).get_source_version(GetSourceVersion(VERSION_ID))

    assert raised.value is error


def test_uow_root_persistence_error_maps_and_does_not_commit() -> None:
    error = SourceEvidencePersistenceError()
    factory = _Factory(enter_error=error)

    with pytest.raises(SourceEvidenceError) as raised:
        _service(factory).get_source_version(GetSourceVersion(VERSION_ID))

    assert raised.value.error_code == "persistence_error"
    assert raised.value.__cause__ is error
    assert factory.uows[0].commits == 0


def test_uow_unrelated_error_propagates_and_does_not_commit() -> None:
    error = RuntimeError("enter failed")
    factory = _Factory(enter_error=error)

    with pytest.raises(RuntimeError) as raised:
        _service(factory).get_source_version(GetSourceVersion(VERSION_ID))

    assert raised.value is error
    assert factory.uows[0].commits == 0


def test_association_query_uses_one_fresh_uow_per_call() -> None:
    factory = _Factory(association=_association())
    service = _service(factory)

    service.get_source_association(GetSourceAssociation(TASK, ASSOCIATION_ID))
    service.get_source_association(GetSourceAssociation(TASK, ASSOCIATION_ID))

    assert len(factory.uows) == 2
    assert factory.uows[0] is not factory.uows[1]
    assert all(uow.commits == 0 for uow in factory.uows)
