"""Contract tests for the private Marketing Brief output seam."""

from __future__ import annotations

import inspect
from typing import get_type_hints

import pytest

from ai_ecommerce_agent.application.model_runtime import StructuredOutputSpec
from ai_ecommerce_agent.modules.marketing_brief.application.skills import (
    marketing_brief_generation,
)

pytestmark = pytest.mark.contract


def test_private_facade_exports_exact_ordered_symbols() -> None:
    assert marketing_brief_generation.__all__ == [
        "MarketingBriefStageDecision",
        "marketing_brief_candidate_output_spec",
    ]
    assert [
        getattr(marketing_brief_generation, name)
        for name in marketing_brief_generation.__all__
    ] == [
        marketing_brief_generation.MarketingBriefStageDecision,
        marketing_brief_generation.marketing_brief_candidate_output_spec,
    ]


def test_stage_decision_and_spec_function_are_exact() -> None:
    decision = marketing_brief_generation.MarketingBriefStageDecision
    assert list(decision) == [
        decision.VALID,
        decision.VALID_WITH_LIMITATIONS,
        decision.STRATEGY_CHANGE_REQUIRED,
        decision.WAITING_INPUT,
        decision.PAUSED,
        decision.FAILED,
    ]
    function = marketing_brief_generation.marketing_brief_candidate_output_spec
    assert list(inspect.signature(function).parameters) == []
    assert not inspect.iscoroutinefunction(function)
    assert get_type_hints(function)["return"] is StructuredOutputSpec
