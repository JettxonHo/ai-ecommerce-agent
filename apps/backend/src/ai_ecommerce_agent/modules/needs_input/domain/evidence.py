"""Truthful, bounded evidence used to derive a Needs Input request."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from ai_ecommerce_agent.shared_kernel import Revision, TaskId


def _bounded_text(value: object, *, name: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value.strip():
        raise ValueError(f"{name} must be non-empty")
    if len(value.encode("utf-8")) > maximum:
        raise ValueError(f"{name} exceeds its bounded size")
    return value


def _mapping_tuple(
    values: object, *, name: str, maximum: int
) -> tuple[Mapping[str, object], ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple")
    copied: list[Mapping[str, object]] = []
    for value in cast(tuple[object, ...], values):
        if not isinstance(value, Mapping):
            raise TypeError(f"{name} entries must be mappings")
        try:
            serialized = json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
                allow_nan=False,
            )
            decoded = json.loads(serialized)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{name} entries must be canonical JSON") from error
        if not isinstance(decoded, Mapping):
            raise ValueError(f"{name} entries must be JSON objects")
        copied.append(dict(cast(Mapping[str, object], decoded)))
    try:
        aggregate = json.dumps(
            copied,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be canonical JSON") from error
    if len(aggregate.encode("utf-8")) > maximum:
        raise ValueError(f"{name} exceeds its bounded size")
    return tuple(copied)


@dataclass(frozen=True, slots=True)
class InsufficientResultEvidence:
    """Current-result evidence that is sufficient to derive one request.

    This is deliberately narrower than the full deterministic result.  It
    carries only the persisted Task/input/result revisions and blocker
    projections; it cannot invent external facts or arbitrary questions.
    """

    task_id: TaskId
    input_revision: Revision
    result_revision: Revision
    missing_information: tuple[str, ...]
    affected_stages: tuple[str, ...]
    source_references: tuple[Mapping[str, object], ...]
    conflict_values: tuple[Mapping[str, object], ...]

    def __post_init__(self) -> None:
        if type(self.task_id) is not TaskId:
            raise TypeError("task_id must be a TaskId")
        if type(self.input_revision) is not Revision:
            raise TypeError("input_revision must be a Revision")
        if type(self.result_revision) is not Revision:
            raise TypeError("result_revision must be a Revision")
        if not self.missing_information:
            raise ValueError("missing_information must not be empty")
        if not self.affected_stages:
            raise ValueError("affected_stages must not be empty")
        for item in self.missing_information:
            _bounded_text(item, name="missing_information item", maximum=4096)
        for stage in self.affected_stages:
            _bounded_text(stage, name="affected_stages item", maximum=200)
        object.__setattr__(
            self,
            "source_references",
            _mapping_tuple(
                self.source_references,
                name="source_references",
                maximum=16384,
            ),
        )
        object.__setattr__(
            self,
            "conflict_values",
            _mapping_tuple(
                self.conflict_values,
                name="conflict_values",
                maximum=32768,
            ),
        )


__all__ = ["InsufficientResultEvidence"]
