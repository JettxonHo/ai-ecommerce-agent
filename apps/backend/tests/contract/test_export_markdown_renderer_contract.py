"""Contract tests for the private deterministic Markdown renderer seam."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from datetime import UTC, datetime
from typing import get_type_hints

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

pytestmark = pytest.mark.contract


_MARKETING_GOLDEN = (
    "# Marketing Brief\n"
    "**Brief type:** marketing\n"
    "\n"
    "## Task and version\n"
    '- Task: "task-m"\n'
    '- Brief version: "brief-m-1" (v2)\n'
    "- Valid: true\n"
    '- Created at: "2026-08-09T01:02:03Z"\n'
    "### Upstream versions\n"
    '- "strategy-m (v1)"\n'
    "\n"
    "## Objective And Audience\n"
    '- Origin: "model"\n'
    "````json\n"
    "    {\n"
    '        "nested": {\n'
    '            "a": "é",\n'
    '            "z": 1\n'
    "        },\n"
    '        "title": "objective_and_audience value"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Message Architecture\n"
    '- Origin: "model"\n'
    "````json\n"
    "    {\n"
    '        "nested": {\n'
    '            "a": "é",\n'
    '            "z": 1\n'
    "        },\n"
    '        "title": "message_architecture value"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Reasons To Believe And Evidence\n"
    '- Origin: "model"\n'
    "````json\n"
    "    {\n"
    '        "nested": {\n'
    '            "a": "é",\n'
    '            "z": 1\n'
    "        },\n"
    '        "title": "reasons_to_believe_and_evidence value"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Execution Direction\n"
    "- Origin: 无 / 不适用\n"
    "````json\n"
    "    {\n"
    '        "nested": {\n'
    '            "a": "é",\n'
    '            "z": 1\n'
    "        },\n"
    '        "title": "execution_direction value"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Constraints And Honesty\n"
    '- Origin: "model"\n'
    "````json\n"
    "    {\n"
    '        "nested": {\n'
    '            "a": "é",\n'
    '            "z": 1\n'
    "        },\n"
    '        "title": "constraints_and_honesty value"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Version And Workflow Context\n"
    '- Origin: "model"\n'
    "````json\n"
    "    {\n"
    '        "nested": {\n'
    '            "a": "é",\n'
    '            "z": 1\n'
    "        },\n"
    '        "title": "version_and_workflow_context value"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Hypotheses\n"
    '- "test hypothesis"\n'
    "\n"
    "## Evidence limitations\n"
    '- "limited evidence"\n'
    "\n"
    "## Risks\n"
    '- "test risk"\n'
    "\n"
    "## Evidence references\n"
    '- "source_fragment": "fragment-m"\n'
    "\n"
    "## Export metadata\n"
    '- Export snapshot: "export-1"\n'
    '- Exported at: "2026-08-09T02:03:04Z"\n'
    '- File name: "task-export.md"\n'
    '- Content location: "memory://export-1"\n'
    '- Media type: "text/markdown; charset=utf-8"\n'
    '- Template version: "mvp0-markdown-v1"\n'
)

_XIAOHONGSHU_GOLDEN = (
    "# Xiaohongshu Brief\n"
    "**Brief type:** xiaohongshu\n"
    "\n"
    "## Task and version\n"
    '- Task: "task-x"\n'
    '- Brief version: "brief-x-1" (v3)\n'
    "- Valid: true\n"
    '- Created at: "2026-08-09T01:02:03Z"\n'
    "### Upstream versions\n"
    '- "marketing-x (v2)"\n'
    '- "policy-x (v1)"\n'
    "\n"
    "## Platform And Campaign Context\n"
    '- Origin: "user"\n'
    "````json\n"
    "    {\n"
    '        "direction": "platform_and_campaign_context"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Note Format And Content Mode\n"
    '- Origin: "user"\n'
    "````json\n"
    "    {\n"
    '        "direction": "note_format_and_content_mode"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Creative Structure Directions\n"
    '- Origin: "user"\n'
    "````json\n"
    "    {\n"
    '        "direction": "creative_structure_directions"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Discovery And Action Directions\n"
    '- Origin: "user"\n'
    "````json\n"
    "    {\n"
    '        "direction": "discovery_and_action_directions"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Evidence And Platform Constraints\n"
    '- Origin: "user"\n'
    "````json\n"
    "    {\n"
    '        "direction": "evidence_and_platform_constraints"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Workflow And Version Context\n"
    '- Origin: "user"\n'
    "````json\n"
    "    {\n"
    '        "direction": "workflow_and_version_context"\n'
    "    }\n"
    "````\n"
    "\n"
    "## Hypotheses\n"
    "- 无 / 不适用\n"
    "\n"
    "## Evidence limitations\n"
    "- 无 / 不适用\n"
    "\n"
    "## Risks\n"
    "- 无 / 不适用\n"
    "\n"
    "## Evidence references\n"
    "- 无 / 不适用\n"
    "\n"
    "## Export metadata\n"
    '- Export snapshot: "export-1"\n'
    '- Exported at: "2026-08-09T02:03:04Z"\n'
    '- File name: "task-export.md"\n'
    '- Content location: "memory://export-1"\n'
    '- Media type: "text/markdown; charset=utf-8"\n'
    '- Template version: "mvp0-markdown-v1"\n'
)


def _marketing() -> MarketingBriefVersionSnapshot:
    return MarketingBriefVersionSnapshot(
        DomainVersionId("brief-m-1"),
        TaskId("task-m"),
        VersionNumber(2),
        True,
        datetime(2026, 8, 9, 1, 2, 3, tzinfo=UTC),
        (DomainVersionReference(DomainVersionId("strategy-m"), VersionNumber(1)),),
        tuple(
            MarketingBriefSemanticGroup(
                name,
                StructuredContent.from_mapping(
                    {"title": f"{name.value} value", "nested": {"z": 1, "a": "é"}}
                ),
                ContentOrigin.MODEL
                if name is not MarketingBriefSemanticGroupName.EXECUTION_DIRECTION
                else None,
            )
            for name in reversed(tuple(MarketingBriefSemanticGroupName))
        ),
        ("test hypothesis",),
        ("limited evidence",),
        ("test risk",),
        (ResourceReference("source_fragment", "fragment-m"),),
    )


def _xiaohongshu() -> XiaohongshuBriefVersionSnapshot:
    return XiaohongshuBriefVersionSnapshot(
        DomainVersionId("brief-x-1"),
        TaskId("task-x"),
        VersionNumber(3),
        True,
        datetime(2026, 8, 9, 1, 2, 3, tzinfo=UTC),
        (
            DomainVersionReference(DomainVersionId("marketing-x"), VersionNumber(2)),
            DomainVersionReference(DomainVersionId("policy-x"), VersionNumber(1)),
        ),
        tuple(
            XiaohongshuBriefSemanticGroup(
                name,
                StructuredContent.from_mapping({"direction": name.value}),
                ContentOrigin.USER,
            )
            for name in reversed(tuple(XiaohongshuBriefSemanticGroupName))
        ),
        (),
        (),
        (),
        (),
    )


def _export(
    brief: MarketingBriefVersionSnapshot | XiaohongshuBriefVersionSnapshot,
) -> ExportSnapshot:
    kind = (
        ExportBriefKind.MARKETING
        if type(brief) is MarketingBriefVersionSnapshot
        else ExportBriefKind.XIAOHONGSHU
    )
    return ExportSnapshot(
        ExportSnapshotId("export-1"),
        brief.task_id,
        kind,
        DomainVersionReference(brief.brief_version_id, brief.version_number),
        brief.upstream_versions,
        datetime(2026, 8, 9, 2, 3, 4, tzinfo=UTC),
        "task-export.md",
        "text/markdown; charset=utf-8",
        "memory://export-1",
        "mvp0-markdown-v1",
    )


def test_private_renderer_has_exact_keyword_only_interface_and_no_public_reexport() -> (
    None
):
    signature = inspect.signature(render_export_markdown)
    assert list(signature.parameters) == ["export_snapshot", "brief_snapshot"]
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for parameter in signature.parameters.values()
    )
    assert get_type_hints(render_export_markdown)["return"] is str
    assert get_type_hints(render_export_markdown) == {
        "export_snapshot": ExportSnapshot,
        "brief_snapshot": (
            MarketingBriefVersionSnapshot | XiaohongshuBriefVersionSnapshot
        ),
        "return": str,
    }
    import ai_ecommerce_agent.modules.export_delivery.application as application

    assert not hasattr(application, "render_export_markdown")


@pytest.mark.parametrize(
    "brief_factory",
    [_marketing, _xiaohongshu],
    ids=["marketing", "xiaohongshu"],
)
def test_independent_golden_documents_are_complete_and_deterministic(
    brief_factory: Callable[
        [], MarketingBriefVersionSnapshot | XiaohongshuBriefVersionSnapshot
    ],
) -> None:
    brief = brief_factory()
    first = render_export_markdown(export_snapshot=_export(brief), brief_snapshot=brief)
    second = render_export_markdown(
        export_snapshot=_export(brief), brief_snapshot=brief
    )
    assert first == second
    expected = _MARKETING_GOLDEN if brief_factory is _marketing else _XIAOHONGSHU_GOLDEN
    assert first == expected
    assert first.endswith("\n") and not first.endswith("\n\n")
    assert "## Task and version" in first
    assert "## Hypotheses" in first
    assert "## Evidence references" in first
    assert "## Export metadata" in first
    assert "**Brief type:**" in first
