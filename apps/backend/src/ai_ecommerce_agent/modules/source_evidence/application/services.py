"""Concrete Source processing application use cases."""

from __future__ import annotations

from collections.abc import Callable
from typing import NoReturn

from ai_ecommerce_agent.modules.source_evidence.application.errors import (
    SourceEvidenceConstraintError,
    SourceEvidenceError,
    SourceEvidenceOwnershipError,
    SourceEvidencePersistenceError,
    SourceEvidenceRevisionConflictError,
)
from ai_ecommerce_agent.modules.source_evidence.application.mappers import (
    source_version_to_snapshot,
)
from ai_ecommerce_agent.modules.source_evidence.application.ports import (
    SourceEvidenceUnitOfWorkFactory,
)
from ai_ecommerce_agent.modules.source_evidence.application.protocols import (
    SourceEvidenceApplication,
)
from ai_ecommerce_agent.modules.source_evidence.domain import (
    InvalidTransitionError,
    RevisionConflictError,
    SourceProcessingStatus,
    SourceVersionProcessing,
    SourceVersionSnapshot,
)
from ai_ecommerce_agent.shared_kernel import ProjectError, Revision, SourceVersionId

from .commands import (
    MarkSourceProcessingFailed,
    MarkSourceReady,
    MarkSourceReadyWithRejections,
    StartSourceProcessing,
    SupersedeSourceVersion,
)

_Transition = Callable[[SourceVersionProcessing], SourceVersionProcessing]
_ProcessingCommand = (
    StartSourceProcessing
    | MarkSourceReady
    | MarkSourceReadyWithRejections
    | MarkSourceProcessingFailed
    | SupersedeSourceVersion
)


def _public_error(
    source_version_id: SourceVersionId,
    *,
    error_code: str,
    message: str,
    retryability: bool = False,
    expected_revision: Revision | None = None,
    actual_revision: Revision | None = None,
    conflicting_state: SourceProcessingStatus | None = None,
    recovery_hint: str | None = None,
) -> SourceEvidenceError:
    return SourceEvidenceError(
        error_code=error_code,
        category="source_evidence",
        message=message,
        retryability=retryability,
        relevant_reference=source_version_id,
        expected_revision=expected_revision,
        actual_revision=actual_revision,
        conflicting_state=conflicting_state,
        recovery_hint=recovery_hint,
    )


def _not_found(source_version_id: SourceVersionId) -> NoReturn:
    raise _public_error(
        source_version_id,
        error_code="not_found",
        message="Source Version was not found",
        recovery_hint="refresh",
    )


def _domain_revision_conflict(
    error: RevisionConflictError, source_version_id: SourceVersionId
) -> SourceEvidenceError:
    context = error.safe_context
    return _public_error(
        source_version_id,
        error_code="revision_conflict",
        message="The Source Version changed; refresh before retrying",
        expected_revision=Revision(int(context["expected_revision"])),
        actual_revision=Revision(int(context["current_revision"])),
        recovery_hint="refresh_and_compare",
    )


def _adapter_revision_conflict(
    error: SourceEvidenceRevisionConflictError, source_version_id: SourceVersionId
) -> SourceEvidenceError:
    context = error.safe_context
    return _public_error(
        source_version_id,
        error_code="revision_conflict",
        message="The Source Version changed; refresh before retrying",
        expected_revision=Revision(int(context["expected_revision"])),
        recovery_hint="refresh_and_compare",
    )


def _invalid_transition(
    error: InvalidTransitionError, source_version_id: SourceVersionId
) -> SourceEvidenceError:
    context = error.safe_context
    return _public_error(
        source_version_id,
        error_code="invalid_transition",
        message="The requested Source Version processing transition is not available",
        conflicting_state=SourceProcessingStatus(context["status"]),
        recovery_hint="refresh",
    )


def _translate_adapter_error(
    error: Exception, source_version_id: SourceVersionId
) -> SourceEvidenceError:
    if isinstance(error, SourceEvidenceRevisionConflictError):
        return _adapter_revision_conflict(error, source_version_id)
    if isinstance(error, SourceEvidenceOwnershipError):
        return _public_error(
            source_version_id,
            error_code="ownership_conflict",
            message="The related Source Evidence resource belongs to a different owner",
            recovery_hint="refresh",
        )
    if isinstance(error, SourceEvidenceConstraintError):
        return _public_error(
            source_version_id,
            error_code="constraint_violation",
            message="The Source Evidence change violates a persistence constraint",
            recovery_hint="refresh",
        )
    if isinstance(error, SourceEvidencePersistenceError):
        return _public_error(
            source_version_id,
            error_code="persistence_error",
            message="Source Evidence persistence is unavailable",
            retryability=True,
            recovery_hint="retry_later",
        )
    raise error


class SourceEvidenceApplicationService(SourceEvidenceApplication):
    """Execute one Source processing transition in one short transaction."""

    def __init__(self, uow_factory: SourceEvidenceUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def _write(
        self, command: _ProcessingCommand, transition: _Transition
    ) -> SourceVersionSnapshot:
        try:
            with self._uow_factory() as uow:
                source_version = uow.source_versions.get(command.source_version_id)
                processing = uow.source_version_processing.get(
                    command.source_version_id
                )
                if source_version is None or processing is None:
                    _not_found(command.source_version_id)

                transitioned = transition(processing)
                uow.source_version_processing.save(
                    transitioned, expected_revision=command.expected_revision
                )
                snapshot = source_version_to_snapshot(source_version, transitioned)
                uow.commit()
                return snapshot
        except SourceEvidenceError:
            raise
        except RevisionConflictError as error:
            raise _domain_revision_conflict(error, command.source_version_id) from error
        except InvalidTransitionError as error:
            raise _invalid_transition(error, command.source_version_id) from error
        except (
            SourceEvidenceRevisionConflictError,
            SourceEvidenceOwnershipError,
            SourceEvidenceConstraintError,
            SourceEvidencePersistenceError,
        ) as error:
            raise _translate_adapter_error(error, command.source_version_id) from error
        except ProjectError:
            raise

    def start_source_processing(
        self, command: StartSourceProcessing
    ) -> SourceVersionSnapshot:
        return self._write(
            command,
            lambda processing: processing.start_processing(
                expected_revision=command.expected_revision,
                updated_at=command.updated_at,
            ),
        )

    def mark_source_ready(self, command: MarkSourceReady) -> SourceVersionSnapshot:
        return self._write(
            command,
            lambda processing: processing.mark_ready(
                expected_revision=command.expected_revision,
                updated_at=command.updated_at,
            ),
        )

    def mark_source_ready_with_rejections(
        self, command: MarkSourceReadyWithRejections
    ) -> SourceVersionSnapshot:
        return self._write(
            command,
            lambda processing: processing.mark_ready_with_rejections(
                expected_revision=command.expected_revision,
                updated_at=command.updated_at,
            ),
        )

    def mark_source_processing_failed(
        self, command: MarkSourceProcessingFailed
    ) -> SourceVersionSnapshot:
        return self._write(
            command,
            lambda processing: processing.mark_failed(
                command.failure_summary,
                expected_revision=command.expected_revision,
                updated_at=command.updated_at,
            ),
        )

    def supersede_source_version(
        self, command: SupersedeSourceVersion
    ) -> SourceVersionSnapshot:
        return self._write(
            command,
            lambda processing: processing.supersede(
                expected_revision=command.expected_revision,
                updated_at=command.updated_at,
            ),
        )


__all__ = ["SourceEvidenceApplicationService"]
