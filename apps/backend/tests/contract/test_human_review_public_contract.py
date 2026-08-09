"""Public facade contract tests for Human Review."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.modules.human_review import public

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = [
    "ReviewPackageStatus",
    "ReviewDecisionOutcome",
    "ReviewPackageIdentity",
    "ReviewPackageReference",
    "ReviewDraftReference",
    "ReviewDecisionBasis",
]


def test_human_review_facade_is_exactly_six_symbols() -> None:
    assert public.__all__ == _EXPECTED_PUBLIC
    assert {name for name in public.__dict__ if not name.startswith("_")} == set(
        _EXPECTED_PUBLIC
    )


def test_human_review_facade_exposes_no_private_or_technical_types() -> None:
    for private_name in (
        "ReviewPackage",
        "ReviewDraft",
        "ReviewDecision",
        "ApprovedStrategy",
        "Repository",
        "UnitOfWork",
        "Session",
        "Engine",
        "StateGraph",
        "SubmitReview",
    ):
        assert not hasattr(public, private_name)
