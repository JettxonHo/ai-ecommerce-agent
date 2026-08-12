"""Application service for one Task-scoped primary input."""

from __future__ import annotations

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

from ..domain import (
    PrimaryInputSnapshot,
    TaskPrimaryInput,
    validate_primary_content,
    validate_primary_file_name,
)
from .primary_input_commands import SavePrimaryInput
from .primary_input_errors import (
    PrimaryInputError,
    PrimaryInputNotFound,
    PrimaryInputPersistenceError,
    PrimaryInputRevisionConflictError,
)
from .primary_input_mappers import primary_input_to_snapshot
from .primary_input_ports import PrimaryInputUnitOfWorkFactory
from .primary_input_protocols import PrimaryInputApplication
from .primary_input_queries import GetPrimaryInput


def _persistence_error(task_id: TaskId) -> PrimaryInputError:
    return PrimaryInputError(
        error_code="persistence_error",
        message="Primary input persistence is unavailable",
        task_id=task_id,
        retryability=True,
    )


class PrimaryInputApplicationService(PrimaryInputApplication):
    """Execute one replay-safe input write or one no-commit read."""

    def __init__(self, uow_factory: PrimaryInputUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    def save_primary_input(self, command: SavePrimaryInput) -> PrimaryInputSnapshot:
        try:
            normalized_content, _ = validate_primary_content(command.content)
            validate_primary_file_name(command.input_kind, command.file_name)
            with self._uow_factory() as uow:
                current = uow.primary_inputs.get(command.task_id)
                if current is None:
                    value = TaskPrimaryInput.create(
                        command.task_id,
                        input_kind=command.input_kind,
                        file_name=command.file_name,
                        content=normalized_content,
                        updated_at=command.updated_at,
                    )
                    uow.primary_inputs.add(value)
                elif (
                    current.input_kind is command.input_kind
                    and current.file_name == command.file_name
                    and current.content == normalized_content
                ):
                    value = current
                else:
                    value = current.replace(
                        input_kind=command.input_kind,
                        file_name=command.file_name,
                        content=normalized_content,
                        updated_at=command.updated_at,
                    )
                    uow.primary_inputs.save(value, expected_revision=current.revision)
                snapshot = primary_input_to_snapshot(value)
                uow.commit()
                return snapshot
        except PrimaryInputError:
            raise
        except PrimaryInputRevisionConflictError as error:
            raise PrimaryInputError(
                error_code="revision_conflict",
                message="The primary input changed; refresh before retrying",
                task_id=command.task_id,
                expected_revision=Revision(
                    int(error.safe_context["expected_revision"])
                ),
            ) from error
        except PrimaryInputPersistenceError as error:
            raise _persistence_error(command.task_id) from error
        except ValueError as error:
            raise PrimaryInputError(
                error_code="invalid_request",
                message="The primary input is invalid",
                task_id=command.task_id,
            ) from error

    def get_primary_input(self, query: GetPrimaryInput) -> PrimaryInputSnapshot:
        try:
            with self._uow_factory() as uow:
                value = uow.primary_inputs.get(query.task_id)
                if value is None:
                    raise PrimaryInputNotFound(query.task_id)
                return primary_input_to_snapshot(value)
        except PrimaryInputError:
            raise
        except PrimaryInputPersistenceError as error:
            raise _persistence_error(query.task_id) from error


__all__ = ["PrimaryInputApplicationService"]
