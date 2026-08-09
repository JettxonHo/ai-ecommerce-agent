"""Public facade contract tests for the Xiaohongshu Brief adapter."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.modules.xiaohongshu_adapter import public

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = [
    "XiaohongshuBriefSemanticGroupName",
    "XiaohongshuBriefSemanticGroup",
    "XiaohongshuBriefVersionSnapshot",
]


def test_xiaohongshu_adapter_facade_is_exactly_three_symbols() -> None:
    assert public.__all__ == _EXPECTED_PUBLIC
    assert {name for name in public.__dict__ if not name.startswith("_")} == set(
        _EXPECTED_PUBLIC
    )


def test_xiaohongshu_adapter_facade_exposes_no_private_or_technical_types() -> None:
    for private_name in (
        "XiaohongshuBrief",
        "XiaohongshuBriefVersion",
        "Repository",
        "UnitOfWork",
        "Session",
        "Engine",
        "StateGraph",
        "DomainVersionReference",
        "ResourceReference",
        "StructuredContent",
        "ContentOrigin",
        "OpenAI",
    ):
        assert not hasattr(public, private_name)
