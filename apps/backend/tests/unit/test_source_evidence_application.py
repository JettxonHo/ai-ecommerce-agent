"""Unit evidence for the Source processing application service."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from types import TracebackType
from typing import Self, cast

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
from ai_ecommerce_agent.modules.source_evidence.application.services import (
    SourceEvidenceApplicationService,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    InvalidTransitionError,
    SourceProcessingStatus,
    SourceVersion,
    SourceVersionProcessing,
    SourceVersionSnapshot,
)
from ai_ecommerce_agent.modules.source_evidence.public import (
    MarkSourceProcessingFailed,
    MarkSourceReady,
    MarkSourceReadyWithRejections,
    StartSourceProcessing,
    SupersedeSourceVersion,
)
from ai_ecommerce_agent.shared_kernel import (
    ProjectError,
    Revision,
    SourceId,
    SourceVersionId,
    VersionNumber,
)

pytestmark = pytest.mark.unit

NOW = datetime(2026, 8, 9, 1, 0, tzinfo=UTC)
VERSION = SourceVersion.create(
    SourceVersionId("source-version-app"), SourceId("source-app"), VersionNumber(1)
)


def _processing(
    *,
    status: SourceProcessingStatus = SourceProcessingStatus.REGISTERED,
    revision: Revision | None = None,
    failure_summary: str | None = None,
    source_version_id: SourceVersionId = VERSION.source_version_id,
) -> SourceVersionProcessing:
    return SourceVersionProcessing(
        source_version_id=source_version_id,
        status=status,
        revision=revision or Revision.initial(),
        failure_summary=failure_summary,
        updated_at=NOW,
    )


class _VersionRepository:
    def __init__(self, owner: _FakeUow, value: SourceVersion | None) -> None:
        self._owner = owner
        self._value = value

    def get(self, source_version_id: SourceVersionId) -> SourceVersion | None:
        self._owner.calls.append(("source_versions.get", source_version_id))
        if self._owner.version_get_error is not None:
            raise self._owner.version_get_error
        return self._value

    def add(self, source_version: SourceVersion) -> None:
        del source_version
        raise AssertionError("application processing must not add Source Versions")


class _ProcessingRepository:
    def __init__(
        self, owner: _FakeUow, store: dict[SourceVersionId, SourceVersionProcessing]
    ) -> None:
        self._owner = owner
        self._store = store

    def get(self, source_version_id: SourceVersionId) -> SourceVersionProcessing | None:
        self._owner.calls.append(("processing.get", source_version_id))
        if self._owner.processing_get_error is not None:
            raise self._owner.processing_get_error
        return self._store.get(source_version_id)

    def add(self, processing: SourceVersionProcessing) -> None:
        del processing
        raise AssertionError("application processing must not add processing rows")

    def save(
        self,
        processing: SourceVersionProcessing,
        *,
        expected_revision: Revision,
    ) -> None:
        self._owner.calls.append(("processing.save", expected_revision))
        if self._owner.save_error is not None:
            raise self._owner.save_error
        current = self._store.get(processing.source_version_id)
        if current is None and self._owner.allow_mismatched_save:
            self._store[next(iter(self._store))] = processing
            return
        if current is None or current.revision != expected_revision:
            raise SourceEvidenceRevisionConflictError(
                resource="source_version_processing",
                identity=str(processing.source_version_id),
                expected_revision=expected_revision,
            )
        self._store[processing.source_version_id] = processing


class _FakeUow:
    def __init__(
        self,
        source_version: SourceVersion | None,
        processing_store: dict[SourceVersionId, SourceVersionProcessing],
        *,
        version_get_error: BaseException | None = None,
        processing_get_error: BaseException | None = None,
        save_error: BaseException | None = None,
        commit_error: BaseException | None = None,
        allow_mismatched_save: bool = False,
    ) -> None:
        self._source_version = source_version
        self._processing_store = processing_store
        self.version_get_error = version_get_error
        self.processing_get_error = processing_get_error
        self.save_error = save_error
        self.commit_error = commit_error
        self.allow_mismatched_save = allow_mismatched_save
        self.calls: list[tuple[str, object]] = []
        self.commits = 0
        self.commit_attempts = 0
        self.rollbacks = 0
        self.close_calls = 0
        self._state = UnitOfWorkState.NEW
        self._before_store: dict[SourceVersionId, SourceVersionProcessing] = {}
        self.source_versions = _VersionRepository(self, source_version)
        self.source_version_processing = _ProcessingRepository(self, processing_store)
        self.source_associations = cast(object, None)

    @property
    def state(self) -> UnitOfWorkState:
        return self._state

    def __enter__(self) -> Self:
        assert self._state is UnitOfWorkState.NEW
        self._before_store = self._processing_store.copy()
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
        assert self._state is UnitOfWorkState.ACTIVE
        self.commit_attempts += 1
        if self.commit_error is not None:
            self.rollback()
            self.close()
            raise self.commit_error
        self.commits += 1
        self._state = UnitOfWorkState.COMMITTED

    def rollback(self) -> None:
        assert self._state is UnitOfWorkState.ACTIVE
        self._processing_store.clear()
        self._processing_store.update(self._before_store)
        self.rollbacks += 1
        self._state = UnitOfWorkState.ROLLED_BACK

    def close(self) -> None:
        if self._state is UnitOfWorkState.CLOSED:
            return
        self.close_calls += 1
        self._state = UnitOfWorkState.CLOSED


class _Factory:
    def __init__(
        self,
        *,
        source_version: SourceVersion | None = VERSION,
        processing: SourceVersionProcessing | None = None,
        version_get_error: BaseException | None = None,
        processing_get_error: BaseException | None = None,
        save_error: BaseException | None = None,
        commit_error: BaseException | None = None,
        allow_mismatched_save: bool = False,
    ) -> None:
        self.source_version = source_version
        self.processing_store = {VERSION.source_version_id: processing or _processing()}
        self.version_get_error = version_get_error
        self.processing_get_error = processing_get_error
        self.save_error = save_error
        self.commit_error = commit_error
        self.allow_mismatched_save = allow_mismatched_save
        self.uows: list[_FakeUow] = []

    def __call__(self) -> SourceEvidenceUnitOfWork:
        uow = _FakeUow(
            self.source_version,
            self.processing_store,
            version_get_error=self.version_get_error,
            processing_get_error=self.processing_get_error,
            save_error=self.save_error,
            commit_error=self.commit_error,
            allow_mismatched_save=self.allow_mismatched_save,
        )
        self.uows.append(uow)
        return cast(SourceEvidenceUnitOfWork, uow)


def _service(factory: _Factory) -> SourceEvidenceApplicationService:
    return SourceEvidenceApplicationService(
        cast(SourceEvidenceUnitOfWorkFactory, factory)
    )


@pytest.mark.parametrize(
    ("method", "command", "initial", "status", "failure_summary"),
    [
        (
            "start_source_processing",
            StartSourceProcessing(VERSION.source_version_id, Revision.initial(), NOW),
            SourceProcessingStatus.REGISTERED,
            SourceProcessingStatus.PROCESSING,
            None,
        ),
        (
            "mark_source_ready",
            MarkSourceReady(VERSION.source_version_id, Revision.initial(), NOW),
            SourceProcessingStatus.PROCESSING,
            SourceProcessingStatus.READY,
            None,
        ),
        (
            "mark_source_ready_with_rejections",
            MarkSourceReadyWithRejections(
                VERSION.source_version_id, Revision.initial(), NOW
            ),
            SourceProcessingStatus.PROCESSING,
            SourceProcessingStatus.READY_WITH_REJECTIONS,
            None,
        ),
        (
            "mark_source_processing_failed",
            MarkSourceProcessingFailed(
                VERSION.source_version_id, Revision.initial(), NOW, "parser failed"
            ),
            SourceProcessingStatus.PROCESSING,
            SourceProcessingStatus.FAILED,
            "parser failed",
        ),
        (
            "supersede_source_version",
            SupersedeSourceVersion(VERSION.source_version_id, Revision.initial(), NOW),
            SourceProcessingStatus.READY,
            SourceProcessingStatus.SUPERSEDED,
            None,
        ),
    ],
)
def test_each_processing_intent_loads_maps_and_commits_once(
    method: str,
    command: object,
    initial: SourceProcessingStatus,
    status: SourceProcessingStatus,
    failure_summary: str | None,
) -> None:
    factory = _Factory(processing=_processing(status=initial))
    service = _service(factory)

    result = cast(
        SourceVersionSnapshot,
        cast(Callable[[object], object], getattr(service, method))(command),
    )

    assert result.processing_status is status
    assert result.processing_revision == Revision(1)
    assert result.failure_summary == failure_summary
    uow = factory.uows[0]
    assert [name for name, _ in uow.calls] == [
        "source_versions.get",
        "processing.get",
        "processing.save",
    ]
    assert uow.calls[-1][1] == Revision.initial()
    assert uow.commits == 1
    assert uow.commit_attempts == 1
    assert uow.rollbacks == 0
    assert uow.close_calls == 1
    assert len(factory.uows) == 1


@pytest.mark.parametrize("missing", ["version", "processing"])
def test_missing_source_or_processing_is_one_not_found_without_save_or_commit(
    missing: str,
) -> None:
    factory = _Factory(source_version=None if missing == "version" else VERSION)
    if missing == "processing":
        factory.processing_store.clear()
    service = _service(factory)

    with pytest.raises(SourceEvidenceError) as raised:
        service.start_source_processing(
            StartSourceProcessing(VERSION.source_version_id, Revision.initial(), NOW)
        )

    assert raised.value.error_code == "not_found"
    assert raised.value.relevant_reference == VERSION.source_version_id
    uow = factory.uows[0]
    assert [name for name, _ in uow.calls] == [
        "source_versions.get",
        "processing.get",
    ]
    assert uow.commits == 0
    assert uow.rollbacks == 1
    assert uow.close_calls == 1


def test_domain_stale_revision_has_typed_expected_and_actual_and_zero_write() -> None:
    factory = _Factory(
        processing=_processing(
            status=SourceProcessingStatus.PROCESSING, revision=Revision(1)
        )
    )
    service = _service(factory)

    with pytest.raises(SourceEvidenceError) as raised:
        service.mark_source_ready(
            MarkSourceReady(VERSION.source_version_id, Revision.initial(), NOW)
        )

    error = raised.value
    assert error.error_code == "revision_conflict"
    assert error.expected_revision == Revision.initial()
    assert error.actual_revision == Revision(1)
    assert error.retryability is False
    assert [name for name, _ in factory.uows[0].calls] == [
        "source_versions.get",
        "processing.get",
    ]
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert factory.processing_store[VERSION.source_version_id].revision == Revision(1)


def test_illegal_transition_reports_typed_current_status_and_zero_write() -> None:
    factory = _Factory(processing=_processing(status=SourceProcessingStatus.READY))
    service = _service(factory)

    with pytest.raises(SourceEvidenceError) as raised:
        service.mark_source_ready(
            MarkSourceReady(VERSION.source_version_id, Revision.initial(), NOW)
        )

    assert raised.value.error_code == "invalid_transition"
    assert raised.value.conflicting_state is SourceProcessingStatus.READY
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert "sqlalchemy" not in raised.value.message.lower()


@pytest.mark.parametrize(
    "adapter_error",
    [
        SourceEvidenceRevisionConflictError(
            resource="source_version_processing",
            identity=str(VERSION.source_version_id),
            expected_revision=Revision.initial(),
        ),
        SourceEvidenceOwnershipError(
            resource="source_evidence_relationship", constraint_name="owner_fk"
        ),
        SourceEvidenceConstraintError(constraint_name="check_status"),
        SourceEvidencePersistenceError(),
    ],
)
def test_known_adapter_errors_have_bounded_public_translation(
    adapter_error: BaseException,
) -> None:
    factory = _Factory(
        processing=_processing(status=SourceProcessingStatus.PROCESSING),
        save_error=adapter_error,
    )
    service = _service(factory)

    with pytest.raises(SourceEvidenceError) as raised:
        service.mark_source_ready(
            MarkSourceReady(VERSION.source_version_id, Revision.initial(), NOW)
        )

    error = raised.value
    if isinstance(adapter_error, SourceEvidenceRevisionConflictError):
        expected_code = "revision_conflict"
    elif isinstance(adapter_error, SourceEvidenceOwnershipError):
        expected_code = "ownership_conflict"
    elif isinstance(adapter_error, SourceEvidenceConstraintError):
        expected_code = "constraint_violation"
    else:
        assert isinstance(adapter_error, SourceEvidencePersistenceError)
        expected_code = "persistence_error"
    assert error.error_code == expected_code
    assert error.relevant_reference == VERSION.source_version_id
    assert error.actual_revision is None
    assert error.retryability is (expected_code == "persistence_error")
    assert all(
        secret not in error.message.lower()
        for secret in ("owner_fk", "check_status", "source_evidence_relationship")
    )
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert factory.processing_store[VERSION.source_version_id].status is (
        SourceProcessingStatus.PROCESSING
    )


def test_commit_persistence_failure_rolls_back_saved_processing() -> None:
    factory = _Factory(
        processing=_processing(status=SourceProcessingStatus.PROCESSING),
        commit_error=SourceEvidencePersistenceError(),
    )
    service = _service(factory)

    with pytest.raises(SourceEvidenceError) as raised:
        service.mark_source_ready(
            MarkSourceReady(VERSION.source_version_id, Revision.initial(), NOW)
        )

    assert raised.value.error_code == "persistence_error"
    assert raised.value.retryability is True
    assert factory.uows[0].commit_attempts == 1
    assert factory.uows[0].commits == 0
    assert factory.processing_store[VERSION.source_version_id].status is (
        SourceProcessingStatus.PROCESSING
    )


@pytest.mark.parametrize(
    "unknown_error",
    [
        RuntimeError("programming bug"),
        ValueError("invariant bug"),
        ProjectError("x", "unknown"),
    ],
)
def test_unknown_errors_propagate_unchanged_and_still_rollback(
    unknown_error: BaseException,
) -> None:
    factory = _Factory(
        processing=_processing(status=SourceProcessingStatus.PROCESSING),
        processing_get_error=unknown_error,
    )
    service = _service(factory)

    with pytest.raises(type(unknown_error)) as raised:
        service.mark_source_ready(
            MarkSourceReady(VERSION.source_version_id, Revision.initial(), NOW)
        )

    assert raised.value is unknown_error
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1


def test_mapper_invariant_propagates_and_does_not_commit() -> None:
    mismatched = _processing(
        status=SourceProcessingStatus.PROCESSING,
        source_version_id=SourceVersionId("other-version"),
    )
    factory = _Factory(processing=mismatched, allow_mismatched_save=True)
    service = _service(factory)

    with pytest.raises(ValueError, match="identities must match"):
        service.mark_source_ready(
            MarkSourceReady(VERSION.source_version_id, Revision.initial(), NOW)
        )

    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1


def test_domain_errors_are_not_retried_or_translated_from_unknown_project_errors() -> (
    None
):
    unknown = ProjectError("source_evidence", "unknown_transition")
    factory = _Factory(
        processing=_processing(status=SourceProcessingStatus.PROCESSING),
        save_error=unknown,
    )
    service = _service(factory)

    with pytest.raises(ProjectError) as raised:
        service.mark_source_ready(
            MarkSourceReady(VERSION.source_version_id, Revision.initial(), NOW)
        )

    assert raised.value is unknown
    assert len(factory.uows) == 1
    assert factory.uows[0].rollbacks == 1


def test_public_domain_invalid_transition_type_is_only_translated_for_known_error() -> (
    None
):
    # This guards the intentional narrow mapping boundary: an arbitrary
    # ProjectError is not converted into a retryable Source application error.
    assert isinstance(
        InvalidTransitionError(
            resource="source_version_processing",
            status=SourceProcessingStatus.READY.value,
            intent="mark_ready",
        ),
        ProjectError,
    )
