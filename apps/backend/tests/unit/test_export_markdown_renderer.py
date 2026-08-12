"""Behavioral tests for deterministic Markdown rendering."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

import pytest

from ai_ecommerce_agent.modules.export_delivery.application.markdown_renderer import (
    render_export_markdown,
)
from ai_ecommerce_agent.modules.export_delivery.public import (
    ExportBriefKind,
    ExportSnapshot,
)
from ai_ecommerce_agent.modules.marketing_brief.public import (
    MarketingBriefSemanticGroup,
    MarketingBriefSemanticGroupName,
    MarketingBriefVersionSnapshot,
)
from ai_ecommerce_agent.modules.task_management.public import DomainVersionReference
from ai_ecommerce_agent.modules.xiaohongshu_adapter.public import (
    XiaohongshuBriefSemanticGroup,
    XiaohongshuBriefSemanticGroupName,
    XiaohongshuBriefVersionSnapshot,
)
from ai_ecommerce_agent.shared_kernel import (
    ContentOrigin,
    DomainVersionId,
    ExportSnapshotId,
    ResourceReference,
    StructuredContent,
    TaskId,
    VersionNumber,
)

pytestmark = pytest.mark.unit


class _MarketingSubclass(MarketingBriefVersionSnapshot):
    pass


class _ExportSubclass(ExportSnapshot):
    pass


def _groups(
    kind: str, *, reversed_order: bool = True, empty: bool = False
) -> tuple[Any, ...]:
    if kind == "marketing":
        names = tuple(MarketingBriefSemanticGroupName)
        return tuple(
            MarketingBriefSemanticGroup(
                name,
                StructuredContent.from_mapping(
                    {} if empty else {"value": f"<{name.value}> # heading <h1> ```"}
                ),
                None if index == 0 else ContentOrigin.MODEL,
            )
            for index, name in enumerate(reversed(names) if reversed_order else names)
        )
    else:
        names = tuple(XiaohongshuBriefSemanticGroupName)
        return tuple(
            XiaohongshuBriefSemanticGroup(
                name,
                StructuredContent.from_mapping(
                    {} if empty else {"value": f"<{name.value}> # heading <h1> ```"}
                ),
                None if index == 0 else ContentOrigin.MODEL,
            )
            for index, name in enumerate(reversed(names) if reversed_order else names)
        )


def _brief(
    kind: str = "marketing", **changes: Any
) -> MarketingBriefVersionSnapshot | XiaohongshuBriefVersionSnapshot:
    values: dict[str, Any] = {
        "brief_version_id": DomainVersionId("brief-1"),
        "task_id": TaskId("task-1"),
        "version_number": VersionNumber(2),
        "valid": True,
        "created_at": datetime(2026, 8, 9, 1, 2, 3, tzinfo=UTC),
        "upstream_versions": (
            DomainVersionReference(DomainVersionId("upstream-2"), VersionNumber(2)),
            DomainVersionReference(DomainVersionId("upstream-1"), VersionNumber(1)),
        ),
        "semantic_groups": _groups(kind),
        "hypotheses": ("hypothesis one",),
        "evidence_limitations": ("limitation one",),
        "risks": ("risk one",),
        "evidence_references": (ResourceReference("fragment", "fragment-1"),),
    }
    values.update(changes)
    if kind == "marketing":
        return MarketingBriefVersionSnapshot(**values)
    return XiaohongshuBriefVersionSnapshot(**values)


def _export(
    brief: MarketingBriefVersionSnapshot | XiaohongshuBriefVersionSnapshot,
    **changes: Any,
) -> ExportSnapshot:
    values: dict[str, Any] = {
        "export_snapshot_id": ExportSnapshotId("export-1"),
        "task_id": brief.task_id,
        "brief_kind": ExportBriefKind.MARKETING
        if type(brief) is MarketingBriefVersionSnapshot
        else ExportBriefKind.XIAOHONGSHU,
        "brief_version": DomainVersionReference(
            brief.brief_version_id, brief.version_number
        ),
        "upstream_versions": brief.upstream_versions,
        "exported_at": datetime(2026, 8, 9, 2, 3, 4, tzinfo=UTC),
        "file_name": "task-export.md",
        "media_type": "text/markdown; charset=utf-8",
        "content_location": "memory://export",
        "template_version": "mvp0-markdown-v1",
    }
    values.update(changes)
    return ExportSnapshot(**values)


def test_group_order_is_canonical_and_content_is_detached_json() -> None:
    brief = _brief()
    rendered = render_export_markdown(
        export_snapshot=_export(brief), brief_snapshot=brief
    )
    positions = [
        rendered.index(f"## {name.value.replace('_', ' ').title()}")
        for name in MarketingBriefSemanticGroupName
    ]
    assert positions == sorted(positions)
    assert "<objective_and_audience> # heading <h1> ```" in rendered
    assert "````json" in rendered
    assert '"value": "<objective_and_audience> # heading <h1> ```"' in rendered
    assert "<h1>" in rendered


@pytest.mark.parametrize("kind", ["marketing", "xiaohongshu"])
def test_empty_collections_and_empty_group_are_honest(kind: str) -> None:
    brief = _brief(
        kind,
        semantic_groups=_groups(kind, empty=True),
        hypotheses=(),
        evidence_limitations=(),
        risks=(),
        evidence_references=(),
        upstream_versions=(),
    )
    rendered = render_export_markdown(
        export_snapshot=_export(brief), brief_snapshot=brief
    )
    assert rendered.count("无 / 不适用") >= 6


@pytest.mark.parametrize(
    ("brief_changes", "export_changes"),
    [
        ({"valid": False}, {}),
        ({"created_at": datetime(2026, 8, 9)}, {}),
        ({"task_id": TaskId("other")}, {}),
        ({}, {"template_version": "v2"}),
        ({}, {"media_type": "text/plain"}),
        ({}, {"task_id": TaskId("other")}),
    ],
)
def test_basis_family_and_value_rules_are_rejected(
    brief_changes: dict[str, Any], export_changes: dict[str, Any]
) -> None:
    brief_changes = dict(brief_changes)
    if "task_id" in brief_changes:
        export_changes = {"task_id": brief_changes["task_id"]}
        brief_changes = {}
    brief = _brief(**brief_changes)
    with pytest.raises((TypeError, ValueError)):
        render_export_markdown(
            export_snapshot=_export(brief, **export_changes), brief_snapshot=brief
        )


@pytest.mark.parametrize("bad", [None, object(), _ExportSubclass])
def test_export_input_requires_exact_type(bad: object) -> None:
    brief = _brief()
    export = _export(brief)
    if bad is _ExportSubclass:
        candidate = _ExportSubclass(
            export.export_snapshot_id,
            export.task_id,
            export.brief_kind,
            export.brief_version,
            export.upstream_versions,
            export.exported_at,
            export.file_name,
            export.media_type,
            export.content_location,
            export.template_version,
        )
    else:
        candidate = bad
    with pytest.raises(TypeError):
        render_export_markdown(export_snapshot=candidate, brief_snapshot=brief)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [None, object(), _MarketingSubclass])
def test_brief_input_requires_exact_type(bad: object) -> None:
    brief = _brief()
    candidate = (
        bad(  # type: ignore[operator]
            brief.brief_version_id,
            brief.task_id,
            brief.version_number,
            brief.valid,
            brief.created_at,
            brief.upstream_versions,
            cast(tuple[MarketingBriefSemanticGroup, ...], brief.semantic_groups),
            brief.hypotheses,
            brief.evidence_limitations,
            brief.risks,
            brief.evidence_references,
        )
        if bad is _MarketingSubclass
        else bad
    )
    with pytest.raises(TypeError):
        render_export_markdown(export_snapshot=_export(brief), brief_snapshot=candidate)  # type: ignore[arg-type]


def test_timezone_is_normalized_to_utc_and_output_has_one_lf_and_no_bom() -> None:
    brief = _brief(created_at=datetime(2026, 8, 9, 3, 2, 3, tzinfo=UTC))
    rendered = render_export_markdown(
        export_snapshot=_export(
            brief, exported_at=datetime(2026, 8, 9, 4, 3, tzinfo=UTC)
        ),
        brief_snapshot=brief,
    )
    assert "2026-08-09T03:02:03Z" in rendered
    assert "2026-08-09T04:03:00Z" in rendered
    assert "\r" not in rendered
    assert rendered.encode("utf-8").decode("utf-8") == rendered
    assert not rendered.startswith("\ufeff")


def test_renderer_does_not_mutate_or_retain_structured_content() -> None:
    brief = _brief()
    before = brief.semantic_groups[0].content.to_mapping()
    rendered = render_export_markdown(
        export_snapshot=_export(brief), brief_snapshot=brief
    )
    after = brief.semantic_groups[0].content.to_mapping()
    assert before == after
    assert "memory://" not in rendered
