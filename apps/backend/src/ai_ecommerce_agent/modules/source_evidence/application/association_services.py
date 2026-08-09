"""Concrete Source-owned association application use cases."""

from __future__ import annotations

from typing import NoReturn

from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceConstraintError,
    SourceEvidenceOwnershipError,
    SourceEvidencePersistenceError,
    SourceEvidenceRevisionConflictError,
)
from ai_ecommerce_agent.modules.source_evidence.application.mappers import (
    source_association_replacement_to_snapshot,
    task_source_association_to_snapshot,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceEvidenceUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    AssociationReplacementError,
    InvalidTransitionError,
    OwnershipError,
    RevisionConflictError,
    SourceAssociationMembershipState,
)
from ai_ecommerce_agent.modules.source_evidence.domain.snapshots import (
    SourceAssociationSnapshot,
)
from ai_ecommerce_agent.shared_kernel import (
    ProjectError,
    Revision,
    SourceAssociationId,
)

from .association_commands import RemoveSourceAssociation, ReplaceSourceAssociation
from .association_errors import SourceAssociationError
from .association_protocols import SourceAssociationApplication
from .association_results import SourceAssociationReplacementSnapshot


def _public_error(
    source_association_id: SourceAssociationId,
    *,
    error_code: str,
    message: str,
    retryability: bool = False,
    expected_revision: Revision | None = None,
    actual_revision: Revision | None = None,
    conflicting_state: SourceAssociationMembershipState | None = None,
    recovery_hint: str | None = None,
) -> SourceAssociationError:
    return SourceAssociationError(
        error_code=error_code,
        category="source_association",
        message=message,
        retryability=retryability,
        relevant_reference=source_association_id,
        expected_revision=expected_revision,
        actual_revision=actual_revision,
        conflicting_state=conflicting_state,
        recovery_hint=recovery_hint,
    )


def _not_found(source_association_id: SourceAssociationId) -> NoReturn:
    raise _public_error(
        source_association_id,
        error_code="not_found",
        message="Source association was not found",
        recovery_hint="refresh",
    )


def _replacement_not_found(source_association_id: SourceAssociationId) -> NoReturn:
    raise _public_error(
        source_association_id,
        error_code="replacement_source_not_found",
        message="Replacement Source Version was not found",
        recovery_hint="refresh",
    )


def _ownership_conflict(source_association_id: SourceAssociationId) -> NoReturn:
    raise _public_error(
        source_association_id,
        error_code="ownership_conflict",
        message="The Source association does not belong to the requested owner",
        recovery_hint="refresh",
    )


def _domain_revision_conflict(
    error: RevisionConflictError, source_association_id: SourceAssociationId
) -> SourceAssociationError:
    context = error.safe_context
    return _public_error(
        source_association_id,
        error_code="revision_conflict",
        message="The Source association changed; refresh before retrying",
        expected_revision=Revision(int(context["expected_revision"])),
        actual_revision=Revision(int(context["current_revision"])),
        recovery_hint="refresh_and_compare",
    )


def _adapter_revision_conflict(
    error: SourceEvidenceRevisionConflictError,
    source_association_id: SourceAssociationId,
) -> SourceAssociationError:
    return _public_error(
        source_association_id,
        error_code="revision_conflict",
        message="The Source association changed; refresh before retrying",
        expected_revision=Revision(int(error.safe_context["expected_revision"])),
        recovery_hint="refresh_and_compare",
    )


def _invalid_transition(
    error: InvalidTransitionError, source_association_id: SourceAssociationId
) -> SourceAssociationError:
    return _public_error(
        source_association_id,
        error_code="invalid_transition",
        message="The requested Source association transition is not available",
        conflicting_state=SourceAssociationMembershipState(
            error.safe_context["status"]
        ),
        recovery_hint="refresh",
    )


def _invalid_replacement(
    source_association_id: SourceAssociationId,
) -> SourceAssociationError:
    return _public_error(
        source_association_id,
        error_code="invalid_replacement",
        message="The replacement violates Source association invariants",
        recovery_hint="refresh",
    )


def _translate_project_error(
    error: ProjectError, source_association_id: SourceAssociationId
) -> SourceAssociationError | None:
    if isinstance(error, RevisionConflictError):
        return _domain_revision_conflict(error, source_association_id)
    if isinstance(error, InvalidTransitionError):
        return _invalid_transition(error, source_association_id)
    if isinstance(error, OwnershipError):
        return _public_error(
            source_association_id,
            error_code="ownership_conflict",
            message="The Source association violates an ownership boundary",
            recovery_hint="refresh",
        )
    if isinstance(error, AssociationReplacementError):
        return _invalid_replacement(source_association_id)
    if isinstance(error, SourceEvidenceRevisionConflictError):
        return _adapter_revision_conflict(error, source_association_id)
    if isinstance(error, SourceEvidenceOwnershipError):
        return _public_error(
            source_association_id,
            error_code="ownership_conflict",
            message="The Source association violates an ownership boundary",
            recovery_hint="refresh",
        )
    if isinstance(error, SourceEvidenceConstraintError):
        return _public_error(
            source_association_id,
            error_code="constraint_violation",
            message="The Source association change violates a persistence constraint",
            recovery_hint="refresh",
        )
    if isinstance(error, SourceEvidencePersistenceError):
        return _public_error(
            source_association_id,
            error_code="persistence_error",
            message="Source association persistence is unavailable",
            retryability=True,
            recovery_hint="retry_later",
        )
    return None


class SourceAssociationApplicationService(SourceAssociationApplication):
    """Execute one association mutation in one short Source transaction."""

    def __init__(self, uow_factory: SourceEvidenceUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def remove_source_association(
        self, command: RemoveSourceAssociation
    ) -> SourceAssociationSnapshot:
        try:
            with self._uow_factory() as uow:
                association = uow.source_associations.get(command.source_association_id)
                if association is None:
                    _not_found(command.source_association_id)
                if association.task_id != command.task_id:
                    _ownership_conflict(command.source_association_id)

                removed = association.remove(
                    expected_revision=command.expected_revision
                )
                uow.source_associations.save(
                    removed, expected_revision=command.expected_revision
                )
                snapshot = task_source_association_to_snapshot(removed)
                uow.commit()
                return snapshot
        except SourceAssociationError:
            raise
        except ProjectError as error:
            translated = _translate_project_error(error, command.source_association_id)
            if translated is None:
                raise
            raise translated from error

    def replace_source_association(
        self, command: ReplaceSourceAssociation
    ) -> SourceAssociationReplacementSnapshot:
        try:
            with self._uow_factory() as uow:
                association = uow.source_associations.get(command.source_association_id)
                if association is None:
                    _not_found(command.source_association_id)
                if association.task_id != command.task_id:
                    _ownership_conflict(command.source_association_id)

                replacement_version = uow.source_versions.get(
                    command.replacement_source_version_id
                )
                if replacement_version is None:
                    _replacement_not_found(command.source_association_id)

                replacement = association.replace(
                    command.replacement_association_id,
                    replacement_version,
                    expected_revision=command.expected_revision,
                )
                uow.source_associations.add(replacement.active_association)
                uow.source_associations.save(
                    replacement.replaced_association,
                    expected_revision=command.expected_revision,
                )
                snapshot = source_association_replacement_to_snapshot(replacement)
                uow.commit()
                return snapshot
        except SourceAssociationError:
            raise
        except ProjectError as error:
            translated = _translate_project_error(error, command.source_association_id)
            if translated is None:
                raise
            raise translated from error


__all__ = ["SourceAssociationApplicationService"]
