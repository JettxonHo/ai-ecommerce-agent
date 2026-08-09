"""Public facade contract tests for Export Delivery."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.modules.export_delivery import public

pytestmark = pytest.mark.contract

_EXPECTED_PUBLIC = [
    "ExportBriefKind",
    "ExportBasis",
    "ExportPreview",
    "ConfirmExportRequest",
    "ExportSnapshot",
]


def test_export_delivery_facade_is_exactly_five_symbols() -> None:
    assert public.__all__ == _EXPECTED_PUBLIC
    assert {name for name in public.__dict__ if not name.startswith("_")} == set(
        _EXPECTED_PUBLIC
    )


def test_export_delivery_facade_exposes_no_private_or_technical_types() -> None:
    for private_name in (
        "ExportRenderer",
        "MarkdownRenderer",
        "ExportRepository",
        "UnitOfWork",
        "Session",
        "Engine",
        "StateGraph",
        "DomainVersionReference",
        "TaskId",
        "Revision",
        "MARKDOWN_MEDIA_TYPE",
    ):
        assert not hasattr(public, private_name)
