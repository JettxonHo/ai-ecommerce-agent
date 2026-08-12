"""Pure, deterministic Markdown rendering for immutable export snapshots."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import cast

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


def _exact(value: object, expected: type[object], field_name: str) -> None:
    if type(value) is not expected:
        raise TypeError(f"{field_name} must be an exact {expected.__name__}")


def _text(value: object, field_name: str) -> str:
    _exact(value, str, field_name)
    if not cast(str, value).strip():
        raise ValueError(f"{field_name} must not be blank")
    return cast(str, value)


def _identity_text(value: object, expected: type[object], field_name: str) -> str:
    _exact(value, expected, field_name)
    return _text(object.__getattribute__(value, "value"), f"{field_name}.value")


def _json_value(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
    delimiter = "`" * (
        max((len(run) for run in re.findall(r"`+", encoded)), default=0) + 1
    )
    return f"{delimiter} {encoded} {delimiter}"


def _timestamp(value: object, field_name: str) -> str:
    _exact(value, datetime, field_name)
    moment = cast(datetime, value)
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return moment.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _reference(value: object, field_name: str) -> str:
    _exact(value, DomainVersionReference, field_name)
    reference = cast(DomainVersionReference, value)
    _identity_text(reference.version_id, DomainVersionId, f"{field_name}.version_id")
    _exact(reference.version_number, VersionNumber, f"{field_name}.version_number")
    if type(reference.version_number.value) is not int:
        raise TypeError(f"{field_name}.version_number.value must be an exact int")
    return _json_value(
        f"{reference.version_id.value} (v{reference.version_number.value})"
    )


def _list_lines(values: tuple[str, ...]) -> list[str]:
    if type(values) is not tuple:
        raise TypeError("collection must be an exact tuple")
    if any(type(value) is not str for value in values):
        raise TypeError("collection items must be exact strings")
    return [
        f"- {_json_value(value)}" if value.strip() else "- 无 / 不适用"
        for value in values
    ] or ["- 无 / 不适用"]


def _content_block(content: StructuredContent) -> list[str]:
    _exact(content, StructuredContent, "group.content")
    data = content.to_mapping()
    if not data:
        return ["- 无 / 不适用"]
    encoded = json.dumps(
        data, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=4
    )
    return ["````json", *(f"    {line}" for line in encoded.splitlines()), "````"]


def _group_title(group: StrEnum) -> str:
    return group.value.replace("_", " ").title()


def _validate_snapshot(
    export_snapshot: ExportSnapshot,
    brief_snapshot: MarketingBriefVersionSnapshot | XiaohongshuBriefVersionSnapshot,
) -> tuple[ExportBriefKind, tuple[object, ...], tuple[str, ...], str, str]:
    _exact(export_snapshot, ExportSnapshot, "export_snapshot")
    brief_type: (
        type[MarketingBriefVersionSnapshot] | type[XiaohongshuBriefVersionSnapshot]
    )
    if type(brief_snapshot) is MarketingBriefVersionSnapshot:
        brief_type = MarketingBriefVersionSnapshot
        expected_kind = ExportBriefKind.MARKETING
    elif type(brief_snapshot) is XiaohongshuBriefVersionSnapshot:
        brief_type = XiaohongshuBriefVersionSnapshot
        expected_kind = ExportBriefKind.XIAOHONGSHU
    else:
        raise TypeError("brief_snapshot must be an exact Brief snapshot family")
    _exact(export_snapshot.brief_kind, ExportBriefKind, "export_snapshot.brief_kind")
    if export_snapshot.brief_kind is not expected_kind:
        raise ValueError("export snapshot and brief family do not match")
    _identity_text(
        export_snapshot.export_snapshot_id,
        ExportSnapshotId,
        "export_snapshot.export_snapshot_id",
    )
    _identity_text(export_snapshot.task_id, TaskId, "export_snapshot.task_id")
    _identity_text(brief_snapshot.task_id, TaskId, "brief_snapshot.task_id")
    if export_snapshot.task_id != brief_snapshot.task_id:
        raise ValueError("export snapshot and brief task identities do not match")
    _identity_text(
        brief_snapshot.brief_version_id,
        DomainVersionId,
        "brief_snapshot.brief_version_id",
    )
    _exact(
        brief_snapshot.version_number, VersionNumber, "brief_snapshot.version_number"
    )
    if type(brief_snapshot.version_number.value) is not int:
        raise TypeError("brief_snapshot.version_number.value must be an exact int")
    brief_reference = DomainVersionReference(
        brief_snapshot.brief_version_id, brief_snapshot.version_number
    )
    if export_snapshot.brief_version != brief_reference:
        raise ValueError("export snapshot and brief versions do not match")
    _exact(
        export_snapshot.brief_version,
        DomainVersionReference,
        "export_snapshot.brief_version",
    )
    _exact(
        export_snapshot.upstream_versions, tuple, "export_snapshot.upstream_versions"
    )
    _exact(brief_snapshot.upstream_versions, tuple, "brief_snapshot.upstream_versions")
    if export_snapshot.upstream_versions != brief_snapshot.upstream_versions:
        raise ValueError("export snapshot and brief upstream versions do not match")
    upstream = tuple(
        _reference(value, "upstream_versions")
        for value in brief_snapshot.upstream_versions
    )
    _exact(brief_snapshot.valid, bool, "brief_snapshot.valid")
    if not brief_snapshot.valid:
        raise ValueError("brief snapshot must be valid")
    created_at = _timestamp(brief_snapshot.created_at, "brief_snapshot.created_at")
    exported_at = _timestamp(export_snapshot.exported_at, "export_snapshot.exported_at")
    _text(export_snapshot.file_name, "export_snapshot.file_name")
    _text(export_snapshot.content_location, "export_snapshot.content_location")
    if (
        _text(export_snapshot.template_version, "export_snapshot.template_version")
        != "mvp0-markdown-v1"
    ):
        raise ValueError("unsupported template version")
    if (
        _text(export_snapshot.media_type, "export_snapshot.media_type")
        != "text/markdown; charset=utf-8"
    ):
        raise ValueError("unsupported media type")
    _exact(brief_snapshot.semantic_groups, tuple, "brief_snapshot.semantic_groups")
    if brief_type is MarketingBriefVersionSnapshot:
        expected_names = tuple(MarketingBriefSemanticGroupName)
        group_type = MarketingBriefSemanticGroup
    else:
        expected_names = tuple(XiaohongshuBriefSemanticGroupName)
        group_type = XiaohongshuBriefSemanticGroup
    groups: list[MarketingBriefSemanticGroup | XiaohongshuBriefSemanticGroup] = []
    seen: set[object] = set()
    for group in brief_snapshot.semantic_groups:
        _exact(group, group_type, "semantic_groups item")
        group_value = group
        _exact(group_value.group, type(expected_names[0]), "semantic group name")
        if group_value.group in seen:
            raise ValueError("duplicate semantic group")
        seen.add(group_value.group)
        _content_block(group_value.content)
        if group_value.origin is not None:
            _exact(group_value.origin, ContentOrigin, "semantic group origin")
        groups.append(group)
    if seen != set(expected_names):
        raise ValueError("semantic groups do not match the accepted family")
    groups.sort(key=lambda item: expected_names.index(item.group))
    for field_name in ("hypotheses", "evidence_limitations", "risks"):
        values = getattr(brief_snapshot, field_name)
        _exact(values, tuple, field_name)
        for value in values:
            _text(value, f"{field_name} item")
    _exact(brief_snapshot.evidence_references, tuple, "evidence_references")
    for reference in brief_snapshot.evidence_references:
        _exact(reference, ResourceReference, "evidence reference")
        _text(reference.resource_kind, "evidence reference kind")
        _text(reference.resource_id, "evidence reference id")
    return expected_kind, tuple(groups), upstream, created_at, exported_at


def render_export_markdown(
    *,
    export_snapshot: ExportSnapshot,
    brief_snapshot: MarketingBriefVersionSnapshot | XiaohongshuBriefVersionSnapshot,
) -> str:
    """Render one immutable Brief export as deterministic UTF-8 Markdown."""

    brief_kind, groups, upstream, created_at, exported_at = _validate_snapshot(
        export_snapshot, brief_snapshot
    )
    lines = [
        f"# {brief_kind.value.title()} Brief",
        f"**Brief type:** {brief_kind.value}",
        "",
        "## Task and version",
        f"- Task: {_json_value(brief_snapshot.task_id.value)}",
        "- Brief version: "
        f"{_json_value(brief_snapshot.brief_version_id.value)} "
        f"(v{_json_value(brief_snapshot.version_number.value)})",
        f"- Valid: {str(brief_snapshot.valid).lower()}",
        f"- Created at: {_json_value(created_at)}",
        "### Upstream versions",
        *(tuple(f"- {value}" for value in upstream) or ("- 无 / 不适用",)),
    ]
    for group in groups:
        typed_group = cast(
            MarketingBriefSemanticGroup | XiaohongshuBriefSemanticGroup, group
        )
        origin = (
            _json_value(typed_group.origin.value)
            if typed_group.origin is not None
            else "无 / 不适用"
        )
        lines.extend(
            [
                "",
                f"## {_group_title(typed_group.group)}",
                f"- Origin: {origin}",
                *_content_block(typed_group.content),
            ]
        )
    for field_name, heading in (
        ("hypotheses", "Hypotheses"),
        ("evidence_limitations", "Evidence limitations"),
        ("risks", "Risks"),
    ):
        lines.extend(
            ["", f"## {heading}", *_list_lines(getattr(brief_snapshot, field_name))]
        )
    lines.extend(["", "## Evidence references"])
    if brief_snapshot.evidence_references:
        lines.extend(
            f"- {_json_value(reference.resource_kind)}: "
            f"{_json_value(reference.resource_id)}"
            for reference in brief_snapshot.evidence_references
        )
    else:
        lines.append("- 无 / 不适用")
    lines.extend(
        [
            "",
            "## Export metadata",
            "- Export snapshot: "
            f"{_json_value(export_snapshot.export_snapshot_id.value)}",
            f"- Exported at: {_json_value(exported_at)}",
            f"- File name: {_json_value(export_snapshot.file_name)}",
            f"- Content location: {_json_value(export_snapshot.content_location)}",
            f"- Media type: {_json_value(export_snapshot.media_type)}",
            f"- Template version: {_json_value(export_snapshot.template_version)}",
            "",
        ]
    )
    return "\n".join(lines)
