"""Framework-neutral opaque identities used by business and persistence code.

Identity classes deliberately wrap their string representation instead of using
plain ``str`` aliases.  This keeps Task, Run, Source, Review and version
identities distinct to static type checkers and prevents accidental equality
between different identity families at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, cast
from uuid import uuid4

_IdentityT = TypeVar("_IdentityT", bound="OpaqueIdentity")


@dataclass(frozen=True, slots=True, order=True)
class OpaqueIdentity:
    """A non-empty, immutable identity value.

    The value is intentionally opaque: callers may persist and transport it,
    but the shared kernel does not assign business meaning to its contents.
    ``new`` is provided for application-owned identities whose creation point
    is this value layer; callers loading an existing identity pass its string
    directly to the constructor.
    """

    value: str

    def __post_init__(self) -> None:
        value = cast(object, self.value)
        if not isinstance(value, str):
            raise TypeError("identity value must be a string")
        if not value.strip():
            raise ValueError("identity value must not be empty")

    @classmethod
    def new(cls: type[_IdentityT]) -> _IdentityT:
        """Create an opaque UUID identity owned by the application layer."""

        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True, order=True)
class TaskId(OpaqueIdentity):
    """Stable identity of a Task."""


@dataclass(frozen=True, slots=True, order=True)
class RunId(OpaqueIdentity):
    """Stable identity of a workflow Run."""


@dataclass(frozen=True, slots=True, order=True)
class SourceId(OpaqueIdentity):
    """Stable identity of a Source."""


@dataclass(frozen=True, slots=True, order=True)
class SourceVersionId(OpaqueIdentity):
    """Stable identity of an immutable Source Version."""


@dataclass(frozen=True, slots=True, order=True)
class SourceAssociationId(OpaqueIdentity):
    """Stable identity of a Task-to-Source association."""


@dataclass(frozen=True, slots=True, order=True)
class ReviewId(OpaqueIdentity):
    """Stable identity of a Human Review."""


@dataclass(frozen=True, slots=True, order=True)
class ReviewPackageId(OpaqueIdentity):
    """Stable identity of an immutable Review Package snapshot."""


@dataclass(frozen=True, slots=True, order=True)
class ReviewDraftId(OpaqueIdentity):
    """Stable identity of a mutable Review Draft."""


@dataclass(frozen=True, slots=True, order=True)
class ReviewDecisionId(OpaqueIdentity):
    """Stable identity of an immutable formal Review Decision."""


@dataclass(frozen=True, slots=True, order=True)
class ExportSnapshotId(OpaqueIdentity):
    """Stable identity of an immutable Export Snapshot."""


@dataclass(frozen=True, slots=True, order=True)
class DomainVersionId(OpaqueIdentity):
    """Stable identity of an immutable domain version row."""
