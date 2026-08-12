"""Task-scoped primary product input for the Fast Lane intake slice."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from typing import Self

from ai_ecommerce_agent.shared_kernel import Revision, TaskId

PRIMARY_INPUT_MAX_BYTES = 1024 * 1024


class PrimaryInputKind(StrEnum):
    """The only input forms accepted by the MVP-0 Fast Lane."""

    PASTED_TEXT = "pasted_text"
    TEXT_FILE = "text_file"
    MARKDOWN_FILE = "markdown_file"


def normalize_primary_content(content: str) -> str:
    """Canonicalize line endings while preserving user-visible whitespace."""

    return content.replace("\r\n", "\n").replace("\r", "\n")


def validate_primary_file_name(
    input_kind: PrimaryInputKind, file_name: str | None
) -> None:
    """Validate display-only filename metadata without treating it as a path."""

    if input_kind is PrimaryInputKind.PASTED_TEXT:
        if file_name is not None:
            raise ValueError("pasted text cannot include a filename")
        return
    if not isinstance(file_name, str) or not file_name:
        raise ValueError("file input requires a filename")
    if file_name in {".", ".."} or "/" in file_name or "\\" in file_name:
        raise ValueError("filename must be a display basename")
    normalized_name = file_name.lower()
    if not normalized_name.endswith((".txt", ".md")):
        raise ValueError("filename must end in .txt or .md")
    expected_kind = (
        PrimaryInputKind.TEXT_FILE
        if normalized_name.endswith(".txt")
        else PrimaryInputKind.MARKDOWN_FILE
    )
    if input_kind is not expected_kind:
        raise ValueError("filename extension does not match input kind")


def validate_primary_content(content: str) -> tuple[str, int]:
    """Normalize content and return its UTF-8 byte count under the hard limit."""

    if type(content) is not str:
        raise TypeError("content must be text")
    normalized = normalize_primary_content(content)
    if not normalized.strip():
        raise ValueError("content must be nonblank")
    try:
        byte_count = len(normalized.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise ValueError("content must be valid UTF-8 text") from error
    if byte_count > PRIMARY_INPUT_MAX_BYTES:
        raise ValueError("content exceeds the maximum size")
    return normalized, byte_count


@dataclass(frozen=True, slots=True)
class TaskPrimaryInput:
    """Current primary input owned by one Task and one fixed workspace."""

    task_id: TaskId
    input_kind: PrimaryInputKind
    file_name: str | None
    content: str
    revision: Revision
    updated_at: datetime

    def __post_init__(self) -> None:
        validate_primary_file_name(self.input_kind, self.file_name)
        normalized, _ = validate_primary_content(self.content)
        if normalized != self.content:
            raise ValueError("content must be normalized before persistence")

    @property
    def byte_count(self) -> int:
        """Return the persisted content's UTF-8 size."""

        return len(self.content.encode("utf-8"))

    @classmethod
    def create(
        cls,
        task_id: TaskId,
        *,
        input_kind: PrimaryInputKind,
        file_name: str | None,
        content: str,
        updated_at: datetime,
    ) -> Self:
        normalized, _ = validate_primary_content(content)
        validate_primary_file_name(input_kind, file_name)
        return cls(
            task_id=task_id,
            input_kind=input_kind,
            file_name=file_name,
            content=normalized,
            revision=Revision.initial(),
            updated_at=updated_at,
        )

    def replace(
        self,
        *,
        input_kind: PrimaryInputKind,
        file_name: str | None,
        content: str,
        updated_at: datetime,
    ) -> Self:
        """Return a changed current input with exactly one revision advance."""

        normalized, _ = validate_primary_content(content)
        validate_primary_file_name(input_kind, file_name)
        return replace(
            self,
            input_kind=input_kind,
            file_name=file_name,
            content=normalized,
            revision=self.revision.next(),
            updated_at=updated_at,
        )


__all__ = [
    "PRIMARY_INPUT_MAX_BYTES",
    "PrimaryInputKind",
    "TaskPrimaryInput",
    "normalize_primary_content",
    "validate_primary_content",
    "validate_primary_file_name",
]
