"""Pure tests for the Business Alembic schema allowlist."""

from __future__ import annotations

import pytest

from ai_ecommerce_agent.platform.postgres.migration import business_schema_scope

pytestmark = pytest.mark.unit


def test_non_public_target_rejects_default_schema_alias() -> None:
    """An isolated target schema never broadens to ``None`` or ``public``."""

    assert business_schema_scope("mvp0_008_migration") == frozenset(
        {"mvp0_008_migration"}
    )


def test_public_target_accepts_default_schema_alias() -> None:
    """The production public target accepts both reflection spellings."""

    assert business_schema_scope("public") == frozenset({None, "public"})
