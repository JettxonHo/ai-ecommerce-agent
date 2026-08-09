"""Unit evidence for the Source association application service."""

from __future__ import annotations

from types import TracebackType
from typing import NoReturn, Self, cast

import pytest

from ai_ecommerce_agent.application.ports import UnitOfWorkState
from ai_ecommerce_agent.modules.source_evidence.application import (
    association_services,
)
from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceConstraintError,
    SourceEvidenceOwnershipError,
    SourceEvidencePersistenceError,
    SourceEvidenceRevisionConflictError,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceEvidenceUnitOfWork,
    SourceEvidenceUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    SourceAssociationMembershipState,
    SourceVersion,
    TaskSourceAssociation,
)
from ai_ecommerce_agent.modules.source_evidence.public import (
    RemoveSourceAssociation,
    ReplaceSourceAssociation,
    SourceAssociationError,
    SourceAssociationReplacementSnapshot,
    SourceAssociationSnapshot,
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

TASK = TaskId("task-association")
FOREIGN_TASK = TaskId("task-foreign")
SOURCE = SourceId("source-association")
OTHER_SOURCE = SourceId("source-other")
VERSION_ID = SourceVersionId("source-version-association")
REPLACEMENT_VERSION_ID = SourceVersionId("source-version-replacement")
ASSOCIATION_ID = SourceAssociationId("association-old")
REPLACEMENT_ID = SourceAssociationId("association-new")
NOW_VERSION = VersionNumber(1)
INITIAL_REVISION = Revision.initial()


def _version(
    version_id: SourceVersionId = VERSION_ID,
    source_id: SourceId = SOURCE,
    version_number: int = 1,
) -> SourceVersion:
    return SourceVersion(
        source_version_id=version_id,
        source_id=source_id,
        version_number=VersionNumber(version_number),
    )


def _association(
    *,
    association_id: SourceAssociationId = ASSOCIATION_ID,
    task_id: TaskId = TASK,
    source_id: SourceId = SOURCE,
    source_version_id: SourceVersionId = VERSION_ID,
    state: SourceAssociationMembershipState = SourceAssociationMembershipState.ACTIVE,
    revision: Revision = INITIAL_REVISION,
    replaced_by: SourceAssociationId | None = None,
) -> TaskSourceAssociation:
    return TaskSourceAssociation(
        source_association_id=association_id,
        task_id=task_id,
        source_id=source_id,
        source_version_id=source_version_id,
        membership_state=state,
        revision=revision,
        replaced_by_association_id=replaced_by,
    )


class _AssociationRepository:
    def __init__(
        self, owner: _FakeUow, store: dict[SourceAssociationId, TaskSourceAssociation]
    ) -> None:
        self._owner = owner
        self._store = store

    def get(
        self, source_association_id: SourceAssociationId
    ) -> TaskSourceAssociation | None:
        self._owner.calls.append(("associations.get", source_association_id))
        if self._owner.get_error is not None:
            raise self._owner.get_error
        return self._store.get(source_association_id)

    def add(self, association: TaskSourceAssociation) -> None:
        self._owner.calls.append(
            ("associations.add", association.source_association_id)
        )
        if self._owner.add_error is not None:
            raise self._owner.add_error
        if association.source_association_id in self._store:
            raise AssertionError("successor identity already exists")
        self._store[association.source_association_id] = association

    def save(
        self,
        association: TaskSourceAssociation,
        *,
        expected_revision: Revision,
    ) -> None:
        self._owner.calls.append(("associations.save", expected_revision))
        if self._owner.save_error is not None:
            raise self._owner.save_error
        current = self._store.get(association.source_association_id)
        if current is None or current.revision != expected_revision:
            raise SourceEvidenceRevisionConflictError(
                resource="task_source_association",
                identity=str(association.source_association_id),
                expected_revision=expected_revision,
            )
        self._store[association.source_association_id] = association


class _VersionRepository:
    def __init__(
        self, owner: _FakeUow, store: dict[SourceVersionId, SourceVersion]
    ) -> None:
        self._owner = owner
        self._store = store

    def get(self, source_version_id: SourceVersionId) -> SourceVersion | None:
        self._owner.calls.append(("versions.get", source_version_id))
        if self._owner.version_get_error is not None:
            raise self._owner.version_get_error
        return self._store.get(source_version_id)

    def add(self, version: SourceVersion) -> None:
        del version
        raise AssertionError("association service must not add Source Versions")


class _ProcessingRepository:
    def get(self, source_version_id: SourceVersionId) -> NoReturn:
        del source_version_id
        raise AssertionError("association service must not load processing")

    def add(self, processing: object) -> NoReturn:
        del processing
        raise AssertionError("association service must not add processing")

    def save(self, processing: object, *, expected_revision: Revision) -> NoReturn:
        del processing, expected_revision
        raise AssertionError("association service must not save processing")


class _FakeUow:
    def __init__(
        self,
        associations: dict[SourceAssociationId, TaskSourceAssociation],
        versions: dict[SourceVersionId, SourceVersion],
        *,
        get_error: BaseException | None = None,
        version_get_error: BaseException | None = None,
        add_error: BaseException | None = None,
        save_error: BaseException | None = None,
        commit_error: BaseException | None = None,
    ) -> None:
        self._associations = associations
        self._versions = versions
        self._before_associations: dict[SourceAssociationId, TaskSourceAssociation] = {}
        self.get_error = get_error
        self.version_get_error = version_get_error
        self.add_error = add_error
        self.save_error = save_error
        self.commit_error = commit_error
        self.calls: list[tuple[str, object]] = []
        self.commits = 0
        self.commit_attempts = 0
        self.rollbacks = 0
        self.close_calls = 0
        self._state = UnitOfWorkState.NEW
        self.source_versions = _VersionRepository(self, versions)
        self.source_version_processing = _ProcessingRepository()
        self.source_associations = _AssociationRepository(self, associations)

    @property
    def state(self) -> UnitOfWorkState:
        return self._state

    def __enter__(self) -> Self:
        assert self._state is UnitOfWorkState.NEW
        self._before_associations = self._associations.copy()
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
        self._associations.clear()
        self._associations.update(self._before_associations)
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
        associations: dict[SourceAssociationId, TaskSourceAssociation] | None = None,
        versions: dict[SourceVersionId, SourceVersion] | None = None,
        get_error: BaseException | None = None,
        version_get_error: BaseException | None = None,
        add_error: BaseException | None = None,
        save_error: BaseException | None = None,
        commit_error: BaseException | None = None,
    ) -> None:
        self.associations = (
            associations
            if associations is not None
            else {ASSOCIATION_ID: _association()}
        )
        self.versions = (
            versions
            if versions is not None
            else {
                VERSION_ID: _version(),
                REPLACEMENT_VERSION_ID: _version(REPLACEMENT_VERSION_ID, SOURCE, 2),
            }
        )
        self.get_error = get_error
        self.version_get_error = version_get_error
        self.add_error = add_error
        self.save_error = save_error
        self.commit_error = commit_error
        self.uows: list[_FakeUow] = []

    def __call__(self) -> SourceEvidenceUnitOfWork:
        uow = _FakeUow(
            self.associations,
            self.versions,
            get_error=self.get_error,
            version_get_error=self.version_get_error,
            add_error=self.add_error,
            save_error=self.save_error,
            commit_error=self.commit_error,
        )
        self.uows.append(uow)
        return cast(SourceEvidenceUnitOfWork, uow)


def _service(factory: _Factory) -> object:
    return association_services.SourceAssociationApplicationService(
        cast(SourceEvidenceUnitOfWorkFactory, factory)
    )


def _remove(
    service: object, command: RemoveSourceAssociation
) -> SourceAssociationSnapshot:
    return cast(
        association_services.SourceAssociationApplicationService, service
    ).remove_source_association(command)


def _replace(
    service: object, command: ReplaceSourceAssociation
) -> SourceAssociationReplacementSnapshot:
    return cast(
        association_services.SourceAssociationApplicationService, service
    ).replace_source_association(command)


def test_remove_loads_owns_transitions_saves_maps_and_commits_once() -> None:
    factory = _Factory()
    result = _remove(
        _service(factory),
        RemoveSourceAssociation(TASK, ASSOCIATION_ID, Revision.initial()),
    )

    assert result.source_association_id is ASSOCIATION_ID
    assert result.task_id is TASK
    assert result.membership_state is SourceAssociationMembershipState.REMOVED
    assert result.revision == Revision(1)
    assert [name for name, _ in factory.uows[0].calls] == [
        "associations.get",
        "associations.save",
    ]
    assert factory.uows[0].calls[-1][1] == Revision.initial()
    assert factory.uows[0].commits == 1
    assert factory.uows[0].commit_attempts == 1
    assert factory.uows[0].rollbacks == 0
    assert factory.uows[0].close_calls == 1
    assert factory.associations[ASSOCIATION_ID].membership_state is (
        SourceAssociationMembershipState.REMOVED
    )


def test_replace_adds_successor_before_old_cas_saves_and_commits_once() -> None:
    factory = _Factory()
    result = _replace(
        _service(factory),
        ReplaceSourceAssociation(
            TASK,
            ASSOCIATION_ID,
            REPLACEMENT_ID,
            REPLACEMENT_VERSION_ID,
            Revision.initial(),
        ),
    )

    assert result.replaced_association.source_association_id is ASSOCIATION_ID
    assert result.replaced_association.membership_state is (
        SourceAssociationMembershipState.REPLACED
    )
    assert result.replaced_association.replaced_by_association_id is REPLACEMENT_ID
    assert result.active_association.source_association_id is REPLACEMENT_ID
    assert result.active_association.source_version_id is REPLACEMENT_VERSION_ID
    assert result.active_association.membership_state is (
        SourceAssociationMembershipState.ACTIVE
    )
    assert [name for name, _ in factory.uows[0].calls] == [
        "associations.get",
        "versions.get",
        "associations.add",
        "associations.save",
    ]
    assert factory.uows[0].commits == 1
    assert factory.associations[ASSOCIATION_ID].membership_state is (
        SourceAssociationMembershipState.REPLACED
    )
    assert factory.associations[REPLACEMENT_ID].membership_state is (
        SourceAssociationMembershipState.ACTIVE
    )


def test_each_command_uses_a_fresh_uow() -> None:
    factory = _Factory()
    service = _service(factory)
    _remove(service, RemoveSourceAssociation(TASK, ASSOCIATION_ID, Revision.initial()))

    second_association = _association(
        association_id=SourceAssociationId("association-second"),
    )
    factory.associations[second_association.source_association_id] = second_association
    _remove(
        service,
        RemoveSourceAssociation(
            TASK, second_association.source_association_id, Revision.initial()
        ),
    )

    assert len(factory.uows) == 2
    assert factory.uows[0] is not factory.uows[1]
    assert all(uow.commits == 1 for uow in factory.uows)


@pytest.mark.parametrize("operation", ["remove", "replace"])
def test_missing_old_association_is_typed_not_found_without_write_or_commit(
    operation: str,
) -> None:
    factory = _Factory(associations={})
    service = _service(factory)

    with pytest.raises(SourceAssociationError) as raised:
        if operation == "remove":
            _remove(
                service,
                RemoveSourceAssociation(TASK, ASSOCIATION_ID, Revision.initial()),
            )
        else:
            _replace(
                service,
                ReplaceSourceAssociation(
                    TASK,
                    ASSOCIATION_ID,
                    REPLACEMENT_ID,
                    REPLACEMENT_VERSION_ID,
                    Revision.initial(),
                ),
            )

    error = raised.value
    assert error.error_code == "not_found"
    assert error.category == "source_association"
    assert error.retryability is False
    assert error.relevant_reference is ASSOCIATION_ID
    assert error.recovery_hint == "refresh"
    assert [name for name, _ in factory.uows[0].calls] == ["associations.get"]
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert factory.uows[0].close_calls == 1


def test_foreign_task_is_typed_ownership_conflict_before_replacement_load() -> None:
    factory = _Factory(
        associations={ASSOCIATION_ID: _association(task_id=FOREIGN_TASK)}
    )
    service = _service(factory)

    with pytest.raises(SourceAssociationError) as raised:
        _replace(
            service,
            ReplaceSourceAssociation(
                TASK,
                ASSOCIATION_ID,
                REPLACEMENT_ID,
                REPLACEMENT_VERSION_ID,
                Revision.initial(),
            ),
        )

    assert raised.value.error_code == "ownership_conflict"
    assert raised.value.retryability is False
    assert [name for name, _ in factory.uows[0].calls] == ["associations.get"]
    assert factory.uows[0].commits == 0
    assert factory.associations[ASSOCIATION_ID].membership_state is (
        SourceAssociationMembershipState.ACTIVE
    )


def test_missing_replacement_version_is_typed_without_writes() -> None:
    factory = _Factory(versions={VERSION_ID: _version()})
    service = _service(factory)

    with pytest.raises(SourceAssociationError) as raised:
        _replace(
            service,
            ReplaceSourceAssociation(
                TASK,
                ASSOCIATION_ID,
                REPLACEMENT_ID,
                REPLACEMENT_VERSION_ID,
                Revision.initial(),
            ),
        )

    assert raised.value.error_code == "replacement_source_not_found"
    assert raised.value.relevant_reference is ASSOCIATION_ID
    assert raised.value.recovery_hint == "refresh"
    assert [name for name, _ in factory.uows[0].calls] == [
        "associations.get",
        "versions.get",
    ]
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert set(factory.associations) == {ASSOCIATION_ID}


def test_domain_stale_revision_has_expected_and_actual_and_no_write() -> None:
    factory = _Factory(
        associations={ASSOCIATION_ID: _association(revision=Revision(1))}
    )

    with pytest.raises(SourceAssociationError) as raised:
        _remove(
            _service(factory),
            RemoveSourceAssociation(TASK, ASSOCIATION_ID, Revision.initial()),
        )

    assert raised.value.error_code == "revision_conflict"
    assert raised.value.expected_revision == Revision.initial()
    assert raised.value.actual_revision == Revision(1)
    assert raised.value.recovery_hint == "refresh_and_compare"
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert factory.associations[ASSOCIATION_ID].membership_state is (
        SourceAssociationMembershipState.ACTIVE
    )


@pytest.mark.parametrize(
    ("state", "expected_code"),
    [
        (SourceAssociationMembershipState.REMOVED, "invalid_transition"),
        (SourceAssociationMembershipState.REPLACED, "invalid_transition"),
    ],
)
def test_inactive_remove_and_replace_report_state_without_write(
    state: SourceAssociationMembershipState,
    expected_code: str,
) -> None:
    factory = _Factory(
        associations={
            ASSOCIATION_ID: _association(
                state=state,
                revision=Revision(2),
                replaced_by=REPLACEMENT_ID
                if state is SourceAssociationMembershipState.REPLACED
                else None,
            )
        }
    )
    service = _service(factory)

    with pytest.raises(SourceAssociationError) as remove_error:
        _remove(service, RemoveSourceAssociation(TASK, ASSOCIATION_ID, Revision(2)))
    assert remove_error.value.error_code == expected_code
    assert remove_error.value.conflicting_state is state
    assert factory.uows[0].commits == 0

    factory = _Factory(
        associations={
            ASSOCIATION_ID: _association(
                state=state,
                revision=Revision(2),
                replaced_by=REPLACEMENT_ID
                if state is SourceAssociationMembershipState.REPLACED
                else None,
            )
        }
    )
    with pytest.raises(SourceAssociationError) as replace_error:
        _replace(
            _service(factory),
            ReplaceSourceAssociation(
                TASK,
                ASSOCIATION_ID,
                REPLACEMENT_ID,
                REPLACEMENT_VERSION_ID,
                Revision(2),
            ),
        )
    assert replace_error.value.error_code == expected_code
    assert replace_error.value.conflicting_state is state
    assert factory.uows[0].commits == 0


@pytest.mark.parametrize(
    ("replacement_id", "version", "expected_code"),
    [
        (
            ASSOCIATION_ID,
            _version(REPLACEMENT_VERSION_ID, SOURCE, 2),
            "invalid_replacement",
        ),
        (REPLACEMENT_ID, _version(VERSION_ID, SOURCE, 1), "invalid_replacement"),
        (
            REPLACEMENT_ID,
            _version(REPLACEMENT_VERSION_ID, OTHER_SOURCE, 2),
            "ownership_conflict",
        ),
    ],
)
def test_domain_replacement_invariants_have_bounded_errors(
    replacement_id: SourceAssociationId,
    version: SourceVersion,
    expected_code: str,
) -> None:
    factory = _Factory(
        versions={VERSION_ID: _version(), version.source_version_id: version}
    )

    with pytest.raises(SourceAssociationError) as raised:
        _replace(
            _service(factory),
            ReplaceSourceAssociation(
                TASK,
                ASSOCIATION_ID,
                replacement_id,
                version.source_version_id,
                Revision.initial(),
            ),
        )

    assert raised.value.error_code == expected_code
    assert raised.value.retryability is False
    assert raised.value.recovery_hint == "refresh"
    assert factory.uows[0].commits == 0
    assert set(factory.associations) == {ASSOCIATION_ID}


@pytest.mark.parametrize(
    ("adapter_error", "expected_code", "retryable"),
    [
        (
            SourceEvidenceRevisionConflictError(
                resource="task_source_association",
                identity=str(ASSOCIATION_ID),
                expected_revision=Revision.initial(),
            ),
            "revision_conflict",
            False,
        ),
        (
            SourceEvidenceOwnershipError(
                resource="source_evidence_relationship", constraint_name="owner_fk"
            ),
            "ownership_conflict",
            False,
        ),
        (
            SourceEvidenceConstraintError(constraint_name="check_state"),
            "constraint_violation",
            False,
        ),
        (SourceEvidencePersistenceError(), "persistence_error", True),
    ],
)
def test_known_adapter_save_errors_translate_without_leaking_technical_details(
    adapter_error: BaseException,
    expected_code: str,
    retryable: bool,
) -> None:
    factory = _Factory(save_error=adapter_error)

    with pytest.raises(SourceAssociationError) as raised:
        _remove(
            _service(factory),
            RemoveSourceAssociation(TASK, ASSOCIATION_ID, Revision.initial()),
        )

    assert raised.value.error_code == expected_code
    assert raised.value.retryability is retryable
    assert raised.value.relevant_reference is ASSOCIATION_ID
    assert raised.value.expected_revision == (
        Revision.initial() if expected_code == "revision_conflict" else None
    )
    assert raised.value.actual_revision is None
    assert all(
        secret not in raised.value.message.lower()
        for secret in ("owner_fk", "check_state", "source_evidence_relationship")
    )
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert factory.associations[ASSOCIATION_ID].membership_state is (
        SourceAssociationMembershipState.ACTIVE
    )


def test_replace_add_failure_rolls_back_without_successor() -> None:
    factory = _Factory(add_error=SourceEvidenceConstraintError(constraint_name="fk"))

    with pytest.raises(SourceAssociationError) as raised:
        _replace(
            _service(factory),
            ReplaceSourceAssociation(
                TASK,
                ASSOCIATION_ID,
                REPLACEMENT_ID,
                REPLACEMENT_VERSION_ID,
                Revision.initial(),
            ),
        )

    assert raised.value.error_code == "constraint_violation"
    assert factory.uows[0].calls[-1][0] == "associations.add"
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert set(factory.associations) == {ASSOCIATION_ID}


def test_replace_save_failure_rolls_back_successor_and_old_state() -> None:
    factory = _Factory(save_error=SourceEvidencePersistenceError())

    with pytest.raises(SourceAssociationError) as raised:
        _replace(
            _service(factory),
            ReplaceSourceAssociation(
                TASK,
                ASSOCIATION_ID,
                REPLACEMENT_ID,
                REPLACEMENT_VERSION_ID,
                Revision.initial(),
            ),
        )

    assert raised.value.error_code == "persistence_error"
    assert factory.uows[0].calls[-2:][0][0] == "associations.add"
    assert factory.uows[0].calls[-1][0] == "associations.save"
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
    assert set(factory.associations) == {ASSOCIATION_ID}
    assert factory.associations[ASSOCIATION_ID].membership_state is (
        SourceAssociationMembershipState.ACTIVE
    )


def test_commit_failure_translates_and_rolls_back_both_replacement_rows() -> None:
    factory = _Factory(commit_error=SourceEvidencePersistenceError())

    with pytest.raises(SourceAssociationError) as raised:
        _replace(
            _service(factory),
            ReplaceSourceAssociation(
                TASK,
                ASSOCIATION_ID,
                REPLACEMENT_ID,
                REPLACEMENT_VERSION_ID,
                Revision.initial(),
            ),
        )

    assert raised.value.error_code == "persistence_error"
    assert raised.value.retryability is True
    assert factory.uows[0].commit_attempts == 1
    assert factory.uows[0].commits == 0
    assert set(factory.associations) == {ASSOCIATION_ID}


@pytest.mark.parametrize(
    "unknown_error",
    [
        RuntimeError("programming bug"),
        ValueError("invariant bug"),
        ProjectError("x", "unknown"),
    ],
)
def test_unknown_and_unrelated_project_errors_propagate_unchanged(
    unknown_error: BaseException,
) -> None:
    factory = _Factory(get_error=unknown_error)

    with pytest.raises(type(unknown_error)) as raised:
        _remove(
            _service(factory),
            RemoveSourceAssociation(TASK, ASSOCIATION_ID, Revision.initial()),
        )

    assert raised.value is unknown_error
    assert factory.uows[0].commits == 0
    assert factory.uows[0].rollbacks == 1
