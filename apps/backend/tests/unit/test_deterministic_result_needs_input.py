"""Tests-first contract for the result-to-Needs-Input composition seam."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from ai_ecommerce_agent.bootstrap.deterministic_result_postgres import (
    DeterministicResultApplication,
    DeterministicResultError,
    DeterministicResultSnapshot,
)
from ai_ecommerce_agent.modules.needs_input.application.errors import (
    NeedsInputPersistenceError,
)
from ai_ecommerce_agent.modules.needs_input.public import InsufficientResultEvidence
from ai_ecommerce_agent.orchestration.deterministic_pipeline import PipelineResult
from ai_ecommerce_agent.shared_kernel import Revision, TaskId

pytestmark = pytest.mark.unit

NOW = datetime(2026, 8, 24, 16, 0, tzinfo=UTC)


class _NeedsInputProbe:
    def __init__(self) -> None:
        self.evidence: list[InsufficientResultEvidence] = []
        self.repositories: list[Any] = []
        self.supersessions: list[tuple[Any, TaskId, Revision, Revision]] = []

    def publish_from_result_in_transaction(
        self, repository: Any, evidence: InsufficientResultEvidence
    ) -> Any:
        self.repositories.append(repository)
        self.evidence.append(evidence)
        return SimpleNamespace(action_request_id="needs-input-1")

    def supersede_current_for_result_in_transaction(
        self,
        repository: Any,
        *,
        task_id: TaskId,
        input_revision: Revision,
        result_revision: Revision,
    ) -> None:
        """Record the transaction-neutral sufficient-result reconciliation."""

        self.supersessions.append(
            (repository, task_id, input_revision, result_revision)
        )


class _FailingNeedsInputProbe(_NeedsInputProbe):
    """A transaction participant that surfaces its private adapter failure."""

    def publish_from_result_in_transaction(
        self, repository: Any, evidence: InsufficientResultEvidence
    ) -> Any:
        del repository, evidence
        raise NeedsInputPersistenceError()


class _Coordinator:
    def __init__(self, generated: PipelineResult) -> None:
        self.generated = generated
        self.calls = 0

    def generate(self, *, input_text: str) -> PipelineResult:
        self.calls += 1
        assert input_text == "synthetic insufficient input"
        return self.generated


class _MappingsResult:
    def __init__(self, row: dict[str, object] | None) -> None:
        self._row = row

    def mappings(self) -> _MappingsResult:
        return self

    def one_or_none(self) -> dict[str, object] | None:
        return self._row

    def one(self) -> dict[str, object]:
        assert self._row is not None
        return self._row


class _Transaction:
    def __init__(self, session: _Session) -> None:
        self.session = session

    def __enter__(self) -> _Transaction:
        self.session.transaction_entries += 1
        return self

    def __exit__(self, exc_type: object, *_: object) -> None:
        if exc_type is None:
            self.session.commit_count += 1
        else:
            self.session.rollback_count += 1
        return None


class _Session:
    def __init__(self) -> None:
        self.transaction_entries = 0
        self.commit_count = 0
        self.rollback_count = 0
        self.statements: list[object] = []
        self._results: Iterator[_MappingsResult] = iter(
            (
                _MappingsResult({"task_id": "task-result-needs-input"}),
                _MappingsResult({"revision": 3}),
                _MappingsResult(None),
                _MappingsResult(None),
                _MappingsResult(
                    {
                        "task_id": "task-result-needs-input",
                        "result_revision": 7,
                        "input_revision": 3,
                        "status": "insufficient_input",
                        "generated_at": NOW,
                        "missing_information": '["verified competitor evidence"]',
                        "product_intake": None,
                        "customer_insight": None,
                        "product_positioning": None,
                        "marketing_brief": None,
                        "xiaohongshu_brief": None,
                    }
                ),
            )
        )

    def __enter__(self) -> _Session:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def begin(self) -> _Transaction:
        return _Transaction(self)

    def scalar(self, _statement: object) -> int:
        return 6

    def execute(self, statement: object) -> _MappingsResult:
        self.statements.append(statement)
        if "INSERT INTO" in str(statement).upper():
            return _MappingsResult(None)
        return next(self._results)


class _SufficientSession(_Session):
    """Result-session double for a newer sufficient commit."""

    def __init__(self) -> None:
        super().__init__()
        self._results = iter(
            (
                _MappingsResult({"task_id": "task-result-needs-input"}),
                _MappingsResult({"revision": 4}),
                _MappingsResult(None),
                _MappingsResult(None),
                _MappingsResult(
                    {
                        "task_id": "task-result-needs-input",
                        "result_revision": 8,
                        "input_revision": 4,
                        "status": "awaiting_review",
                        "generated_at": NOW,
                        "missing_information": "[]",
                        "product_intake": None,
                        "customer_insight": None,
                        "product_positioning": None,
                        "marketing_brief": None,
                        "xiaohongshu_brief": None,
                    }
                ),
            )
        )

    def scalar(self, _statement: object) -> int:
        return 7


class _ProbeResultApplication(DeterministicResultApplication):
    def __init__(self, session: _Session, needs_input: _NeedsInputProbe) -> None:
        self._session = session
        self._needs_input_application = needs_input

    def _read_input(
        self, task_id: TaskId, expected_input_revision: int
    ) -> tuple[str, int]:
        assert task_id == TaskId("task-result-needs-input")
        assert expected_input_revision in (3, 4)
        return "synthetic insufficient input", expected_input_revision

    def _read_existing_key(
        self, task_id: TaskId, idempotency_key: str
    ) -> DeterministicResultSnapshot | None:
        assert task_id == TaskId("task-result-needs-input")
        assert idempotency_key in ("result-1", "result-2")
        return None

    def _sessions(self) -> _Session:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self._session


class _ReplayResultApplication(_ProbeResultApplication):
    """Keep the first committed result as the deterministic replay row."""

    def __init__(self, session: _Session, needs_input: _NeedsInputProbe) -> None:
        super().__init__(session, needs_input)
        self._committed: DeterministicResultSnapshot | None = None

    def _read_existing_key(
        self, task_id: TaskId, idempotency_key: str
    ) -> DeterministicResultSnapshot | None:
        assert task_id == TaskId("task-result-needs-input")
        assert idempotency_key == "result-1"
        return self._committed

    def _commit(self, **kwargs: Any) -> tuple[DeterministicResultSnapshot, bool]:
        committed, replayed = super()._commit(**kwargs)
        self._committed = committed
        return committed, replayed


def test_insufficient_result_publishes_needs_input_from_saved_result_evidence() -> None:
    """A committed insufficient result must derive one Task-owned request."""

    needs_input = _NeedsInputProbe()
    session = _Session()
    application = _ProbeResultApplication(session, needs_input)
    generated = PipelineResult(
        status="insufficient_input",
        missing_information=("verified competitor evidence",),
        candidates=(),
    )

    result, replayed = application.generate_result(
        task_id=TaskId("task-result-needs-input"),
        idempotency_key="result-1",
        expected_input_revision=3,
        coordinator=_Coordinator(generated),  # type: ignore[arg-type]
    )

    assert replayed is False
    assert result.status == "insufficient_input"
    assert session.transaction_entries == 1
    assert len(session.statements) == 6
    assert len(needs_input.evidence) == 1
    assert len(needs_input.repositories) == 1
    assert needs_input.repositories[0]._session is session
    evidence = needs_input.evidence[0]
    assert evidence.task_id == TaskId("task-result-needs-input")
    assert evidence.input_revision == Revision(3)
    assert evidence.result_revision == Revision(7)
    assert evidence.missing_information == ("verified competitor evidence",)
    assert evidence.affected_stages == ("product_intake_and_fact_extraction",)


def test_newer_sufficient_result_supersedes_current_blocker_in_same_transaction() -> (
    None
):
    """A sufficient commit must clear the obsolete current blocker atomically."""

    needs_input = _NeedsInputProbe()
    session = _SufficientSession()
    application = _ProbeResultApplication(session, needs_input)
    generated = PipelineResult(
        status="awaiting_review",
        missing_information=(),
        candidates=(),
    )

    result, replayed = application.generate_result(
        task_id=TaskId("task-result-needs-input"),
        idempotency_key="result-2",
        expected_input_revision=4,
        coordinator=_Coordinator(generated),  # type: ignore[arg-type]
    )

    assert replayed is False
    assert result.status == "awaiting_review"
    assert session.transaction_entries == 1
    assert len(needs_input.supersessions) == 1
    repository, task_id, input_revision, result_revision = needs_input.supersessions[0]
    assert repository._session is session
    assert task_id == TaskId("task-result-needs-input")
    assert input_revision == Revision(4)
    assert result_revision == Revision(8)


def test_needs_input_transaction_failure_is_a_retryable_result_error() -> None:
    """A participant failure cannot escape or claim a partial result commit."""

    needs_input = _FailingNeedsInputProbe()
    session = _Session()
    application = _ProbeResultApplication(session, needs_input)
    generated = PipelineResult(
        status="insufficient_input",
        missing_information=("verified competitor evidence",),
        candidates=(),
    )

    with pytest.raises(DeterministicResultError) as raised:
        application.generate_result(
            task_id=TaskId("task-result-needs-input"),
            idempotency_key="result-1",
            expected_input_revision=3,
            coordinator=_Coordinator(generated),  # type: ignore[arg-type]
        )

    assert raised.value.error_code == "persistence_error"
    assert raised.value.retryability is True
    assert session.commit_count == 0
    assert session.rollback_count == 1


def test_exact_result_replay_does_not_duplicate_or_mutate_needs_input_request() -> None:
    """Replaying a committed result must not publish or mutate the request."""

    needs_input = _NeedsInputProbe()
    session = _Session()
    application = _ReplayResultApplication(session, needs_input)
    coordinator = _Coordinator(
        PipelineResult(
            status="insufficient_input",
            missing_information=("verified competitor evidence",),
            candidates=(),
        )
    )

    first, first_replayed = application.generate_result(
        task_id=TaskId("task-result-needs-input"),
        idempotency_key="result-1",
        expected_input_revision=3,
        coordinator=coordinator,  # type: ignore[arg-type]
    )
    before_evidence = tuple(needs_input.evidence)
    before_supersessions = tuple(needs_input.supersessions)
    second, second_replayed = application.generate_result(
        task_id=TaskId("task-result-needs-input"),
        idempotency_key="result-1",
        expected_input_revision=3,
        coordinator=coordinator,  # type: ignore[arg-type]
    )

    assert first_replayed is False
    assert second_replayed is True
    assert second == first
    assert coordinator.calls == 1
    assert tuple(needs_input.evidence) == before_evidence
    assert tuple(needs_input.supersessions) == before_supersessions
    assert session.transaction_entries == 1
