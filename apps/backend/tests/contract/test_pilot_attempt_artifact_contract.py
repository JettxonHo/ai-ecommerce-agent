"""Provider-free contract for the bounded P2 attempt artifact seam."""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest

from ai_ecommerce_agent.orchestration.pilot_attempt_artifact import (
    ArtifactErrorCode,
    AttemptArtifactError,
    CaptureExport,
    ExportContentReference,
    ExportVersionReference,
    FinalDisposition,
    FinalizationCost,
    FinalizationExecution,
    FinalizationGates,
    FinalizeAttempt,
    PilotAttemptArtifacts,
    RecordReview,
    RecordRun,
    ReserveAttempt,
)

pytestmark = pytest.mark.contract


def _artifact_service(tmp_path: Path) -> tuple[PilotAttemptArtifacts, Path]:
    repository_root = Path(__file__).resolve().parents[4]
    approved_parent = tmp_path / "approved-artifacts"
    approved_parent.mkdir()
    return PilotAttemptArtifacts(repository_root, approved_parent), approved_parent


def _reserve(service: PilotAttemptArtifacts, approved_parent: Path) -> Path:
    attempt_root = approved_parent / "p2" / "P01" / "P2-P01-A1"
    service.apply(ReserveAttempt(attempt_root))
    return attempt_root


def test_p2_attempt_reserves_and_reads_exact_sanitized_layout(
    tmp_path: Path,
) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    attempt_root = _reserve(service, approved_parent)

    assert stat.S_IMODE(attempt_root.stat().st_mode) == 0o700
    assert stat.S_IMODE((attempt_root / "exports").stat().st_mode) == 0o700
    assert frozenset(path.name for path in attempt_root.iterdir()) == frozenset(
        {"identity.json", "exports"}
    )
    assert not (attempt_root / "review.json").exists()
    assert not (attempt_root / "outcome.json").exists()

    identity = json.loads((attempt_root / "identity.json").read_text())
    assert identity == {
        "record_type": "attempt_identity",
        "sample_id": "P01",
        "attempt_id": "P2-P01-A1",
        "immutable": True,
    }
    assert stat.S_IMODE((attempt_root / "identity.json").stat().st_mode) == 0o400

    snapshot = service.read("P2-P01-A1")
    assert snapshot["identity"] == identity
    assert snapshot["run"] is None
    assert snapshot["review"] == "PENDING"

    service.apply(
        RecordRun(
            task_id="task-P01",
            task_revision=1,
            result_id="result-P01",
            result_revision=1,
            provider_id="deepseek",
            api_family="chat_completions",
            configured_model_id="deepseek-v4-pro",
            resolved_model_id="deepseek-v4-pro",
            base_url="https://api.deepseek.com",
            reasoning_effort="high",
            pricing_record_id="deepseek-v4-pro-2026-08-30-peak-v1",
            pricing_source_url="https://api-docs.deepseek.com/quick_start/pricing/",
            pricing_model_id="deepseek-v4-pro",
            started_at_utc="2026-08-31T00:00:00Z",
            completed_at_utc="2026-08-31T00:01:00Z",
            gates={"pipeline_completed": True, "review_submitted": False},
            call_count=5,
            calls=({"model_call_id": "P2-P01-A1-stage-1", "latency_ms": 100},),
            usage={"input_tokens": 100, "output_tokens": 200, "total_tokens": 300},
            cost={"reserved_micro_usd": 6783834, "actual_micro_usd": None},
            refs=(
                {
                    "kind": "pricing_record",
                    "value": "deepseek-v4-pro-2026-08-30-peak-v1",
                },
            ),
        )
    )

    run = json.loads((attempt_root / "run.json").read_text())
    assert run["record_type"] == "attempt_run"
    assert run["sample_id"] == "P01"
    assert run["attempt_id"] == "P2-P01-A1"
    assert run["immutable"] is True
    assert run["task"] == {"task_id": "task-P01", "revision": 1}
    assert run["result"] == {"result_id": "result-P01", "revision": 1}
    assert run["provider"]["provider_id"] == "deepseek"
    assert run["model"]["configured_model_id"] == "deepseek-v4-pro"
    assert run["base"]["base_url"] == "https://api.deepseek.com"
    assert run["reasoning"]["effort"] == "high"
    assert run["pricing"]["record_id"] == "deepseek-v4-pro-2026-08-30-peak-v1"
    assert run["usage"]["total_tokens"] == 300
    assert run["cost"]["actual_micro_usd"] is None
    assert stat.S_IMODE((attempt_root / "run.json").stat().st_mode) == 0o400

    read_back = service.read("P2-P01-A1")
    assert read_back["run"] == run
    assert read_back["review"] == "PENDING"
    assert not (attempt_root / "review.json").exists()
    assert not (attempt_root / "outcome.json").exists()
    for marker in (
        "OPENAI_API_KEY",
        "Authorization",
        "raw_provider_payload",
        "prompt",
        "traceback",
        "/Users/ketchup/Private",
    ):
        assert marker not in (attempt_root / "run.json").read_text()


def test_reservation_and_run_are_exclusive_and_identity_bound(tmp_path: Path) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    attempt_root = _reserve(service, approved_parent)
    identity_before = (attempt_root / "identity.json").read_bytes()

    with pytest.raises(AttemptArtifactError) as reserve_error:
        service.apply(ReserveAttempt(attempt_root))
    assert reserve_error.value.error_code == ArtifactErrorCode.ROOT_EXISTS.value
    assert (attempt_root / "identity.json").read_bytes() == identity_before

    service.apply(RecordRun())
    run_before = (attempt_root / "run.json").read_bytes()
    with pytest.raises(AttemptArtifactError) as run_error:
        service.apply(RecordRun())
    assert run_error.value.error_code == ArtifactErrorCode.RECORD_EXISTS.value
    assert (attempt_root / "run.json").read_bytes() == run_before

    with pytest.raises(AttemptArtifactError) as mismatch_error:
        service.apply(RecordRun(sample_id="P02"))
    assert mismatch_error.value.error_code == ArtifactErrorCode.IDENTITY_MISMATCH.value


def test_root_validation_rejects_relative_root(tmp_path: Path) -> None:
    service, _approved_parent = _artifact_service(tmp_path)
    with pytest.raises(AttemptArtifactError):
        service.apply(ReserveAttempt(Path("relative-root")))


def test_root_validation_rejects_in_repository_root(tmp_path: Path) -> None:
    service, _approved_parent = _artifact_service(tmp_path)
    repository_root = Path(__file__).resolve().parents[4]
    with pytest.raises(AttemptArtifactError):
        service.apply(ReserveAttempt(repository_root / "inside-repository"))


def test_root_validation_rejects_traversal_root(tmp_path: Path) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    with pytest.raises(AttemptArtifactError):
        service.apply(ReserveAttempt(approved_parent / "p2" / "P01" / ".." / "outside"))


def test_root_validation_rejects_symlink(tmp_path: Path) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    symlink = approved_parent / "p2"
    symlink.symlink_to(target, target_is_directory=True)
    with pytest.raises(AttemptArtifactError) as error:
        service.apply(ReserveAttempt(symlink / "P01" / "P2-P01-A1"))
    assert error.value.error_code == ArtifactErrorCode.ROOT_NOT_ALLOWED.value


def test_marketing_export_capture_is_exclusive_and_sanitized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    attempt_root = _reserve(service, approved_parent)
    service.apply(
        RecordRun(
            task_id="task-P01",
            task_revision=1,
            result_id="result-P01",
            result_revision=1,
        )
    )
    probe = CaptureExport(
        task_id="task-P01",
        task_revision=1,
        result_id="result-P01",
        result_revision=1,
        brief_version=ExportVersionReference("brief-P01-v1", 1),
        upstream_versions=(ExportVersionReference("positioning-P01-v1", 1),),
        content_reference=ExportContentReference(
            "local_relative", "exports/marketing-brief.md"
        ),
    )

    fsync_calls: list[int] = []
    real_fsync = os.fsync

    def _record_fsync(descriptor: int) -> None:
        fsync_calls.append(descriptor)
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", _record_fsync)
    fsync_count_before_export = len(fsync_calls)

    # Slice 3B GREEN: the export command is provider-free and persists only
    # the fixed Markdown file plus sanitized metadata.
    snapshot = service.apply(probe)
    assert snapshot is not None

    export_path = attempt_root / probe.content_reference.value
    assert export_path == attempt_root / "exports" / "marketing-brief.md"
    assert export_path.read_bytes() == probe.content_bytes
    assert export_path.read_bytes().decode("utf-8").startswith("# ")
    assert stat.S_IMODE(export_path.stat().st_mode) == 0o400
    assert len(fsync_calls) >= fsync_count_before_export + 2

    exports = cast(Mapping[str, Mapping[str, object]], snapshot["exports"])
    assert exports == {
        "marketing": {
            "record_type": probe.record_type,
            "sample_id": probe.sample_id,
            "attempt_id": probe.attempt_id,
            "task": {
                "task_id": probe.task_id,
                "revision": probe.task_revision,
            },
            "result": {
                "result_id": probe.result_id,
                "revision": probe.result_revision,
            },
            "export_snapshot_id": probe.export_snapshot_id,
            "brief_kind": probe.brief_kind,
            "brief_version": {
                "version_id": probe.brief_version.version_id,
                "version_number": probe.brief_version.version_number,
            },
            "upstream_versions": (
                {
                    "version_id": probe.upstream_versions[0].version_id,
                    "version_number": probe.upstream_versions[0].version_number,
                },
            ),
            "exported_at": probe.exported_at,
            "file_name": probe.file_name,
            "server_file_name": probe.server_file_name,
            "template_version": probe.template_version,
            "media_type": probe.media_type,
            "content_reference": {
                "kind": probe.content_reference.kind,
                "value": probe.content_reference.value,
            },
            "byte_count": len(probe.content_bytes),
            "capture_method": probe.capture_method,
            "immutable": probe.immutable,
        }
    }
    assert service.read(probe.attempt_id)["exports"] == exports
    export = exports[probe.brief_kind]
    content_reference = cast(Mapping[str, object], export["content_reference"])
    assert not Path(cast(str, content_reference["value"])).is_absolute()
    assert "hash" not in export
    serialized_export = repr(export)
    for marker in (
        "content_bytes",
        "OPENAI_API_KEY",
        "Authorization",
        "raw_provider_payload",
        "prompt",
        "traceback",
        str(approved_parent),
    ):
        assert marker not in serialized_export

    bytes_before_duplicate = export_path.read_bytes()
    duplicate = replace(probe, content_bytes=b"# duplicate must not overwrite\n")
    with pytest.raises(AttemptArtifactError):
        service.apply(duplicate)
    assert export_path.read_bytes() == bytes_before_duplicate

    cross_identity = replace(
        probe,
        sample_id="P02",
        content_bytes=b"# cross identity must not overwrite\n",
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(cross_identity)
    assert export_path.read_bytes() == bytes_before_duplicate

    malicious_filename = replace(
        probe,
        server_file_name="../marketing-brief.md",
        content_bytes=b"# malicious filename must not write\n",
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(malicious_filename)
    assert export_path.read_bytes() == bytes_before_duplicate

    cross_kind_filename = replace(
        probe,
        brief_kind="xiaohongshu",
        file_name="xiaohongshu-brief.md",
        server_file_name="marketing-brief.md",
        content_reference=ExportContentReference(
            "local_relative", "exports/xiaohongshu-brief.md"
        ),
        content_bytes=b"# cross-kind filename must not write\n",
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(cross_kind_filename)
    assert not (attempt_root / "exports" / "xiaohongshu-brief.md").exists()


def test_human_review_capture_is_bound_and_sanitized(tmp_path: Path) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    attempt_root = _reserve(service, approved_parent)
    service.apply(
        RecordRun(
            task_id="task-P01",
            task_revision=1,
            result_id="result-P01",
            result_revision=1,
        )
    )
    export = CaptureExport(
        task_id="task-P01",
        task_revision=1,
        result_id="result-P01",
        result_revision=1,
        brief_version=ExportVersionReference("brief-P01-v1", 1),
        upstream_versions=(ExportVersionReference("positioning-P01-v1", 1),),
        content_reference=ExportContentReference(
            "local_relative", "exports/marketing-brief.md"
        ),
    )
    service.apply(export)
    initial = service.read(export.attempt_id)
    assert initial["review"] == "PENDING"
    review = RecordReview(
        task_id="task-P01",
        task_revision=1,
        result_id="result-P01",
        result_revision=1,
    )

    # Slice 3C GREEN: the review command is provider-free and persists exactly
    # one immutable, sanitized decision bound to the captured export.
    snapshot = service.apply(review)
    assert snapshot is not None
    assert snapshot["review"] == "APPROVED"
    review_path = attempt_root / "review.json"
    assert stat.S_IMODE(review_path.stat().st_mode) == 0o400
    record = json.loads(review_path.read_text())
    assert record == {
        "record_type": review.record_type,
        "sample_id": review.sample_id,
        "attempt_id": review.attempt_id,
        "task": {"task_id": review.task_id, "revision": review.task_revision},
        "result": {
            "result_id": review.result_id,
            "revision": review.result_revision,
        },
        "review_id": review.review_id,
        "captured_export_snapshot_ids": list(review.captured_export_snapshot_ids),
        "reviewer_role": review.reviewer_role,
        "reviewed_at": review.reviewed_at,
        "dimensions": [
            {
                "name": dimension.name,
                "decision": dimension.decision,
                "critical": dimension.critical,
            }
            for dimension in review.dimensions
        ],
        "overall": review.overall,
        "rationale": review.rationale,
        "notes": list(review.notes),
        "material_edits": list(review.material_edits),
        "immutable": review.immutable,
    }
    review_record = cast(Mapping[str, object], snapshot["review_record"])
    assert review_record["captured_export_snapshot_ids"] == ("export-P2-P01-A1",)
    dimensions = cast(tuple[Mapping[str, object], ...], review_record["dimensions"])
    assert len(dimensions) == 7
    assert dimensions[5]["decision"] == "NOT_APPLICABLE"
    assert dimensions[5]["name"] == "xiaohongshu_consistency"
    assert cast(str, review_record["reviewed_at"]) > cast(str, export.exported_at)
    assert "hash" not in review_record
    serialized_review = repr(review_record)
    for marker in (
        "OPENAI_API_KEY",
        "Authorization",
        "prompt",
        "traceback",
        "@",
        str(approved_parent),
    ):
        assert marker not in serialized_review

    record_before_rejection = review_path.read_bytes()
    second_review = replace(review, review_id="review-P2-P01-A1-2")
    with pytest.raises(AttemptArtifactError):
        service.apply(second_review)
    assert review_path.read_bytes() == record_before_rejection

    cross_identity = replace(review, sample_id="P02")
    with pytest.raises(AttemptArtifactError):
        service.apply(cross_identity)
    assert review_path.read_bytes() == record_before_rejection

    unknown_export = replace(
        review,
        review_id="review-P2-P01-A1-unknown",
        captured_export_snapshot_ids=("export-unknown",),
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(unknown_export)
    assert review_path.read_bytes() == record_before_rejection

    invalid_timing = replace(
        review,
        review_id="review-P2-P01-A1-early",
        reviewed_at="2026-08-31T00:01:00Z",
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(invalid_timing)
    assert review_path.read_bytes() == record_before_rejection

    pii_reviewer = replace(
        review,
        review_id="review-P2-P01-A1-pii",
        reviewer_role="reviewer@example.com",
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(pii_reviewer)
    assert review_path.read_bytes() == record_before_rejection


def test_attempt_finalization_qualifies_only_approved_export(tmp_path: Path) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    attempt_root = _reserve(service, approved_parent)
    service.apply(
        RecordRun(
            task_id="task-P01",
            task_revision=1,
            result_id="result-P01",
            result_revision=1,
            call_count=5,
            calls=tuple(
                {"model_call_id": f"P2-P01-A1-stage-{index}", "latency_ms": 100}
                for index in range(1, 6)
            ),
            gates={
                "schema": True,
                "domain": True,
                "persistence": True,
                "export": True,
            },
            pricing_record_id="deepseek-v4-pro-2026-08-30-peak-v1",
            cost={
                "reserved_micro_usd": 6_783_834,
                "actual_micro_usd": 6_783_834,
            },
        )
    )
    export = CaptureExport(
        task_id="task-P01",
        task_revision=1,
        result_id="result-P01",
        result_revision=1,
        brief_version=ExportVersionReference("brief-P01-v1", 1),
        upstream_versions=(ExportVersionReference("positioning-P01-v1", 1),),
        content_reference=ExportContentReference(
            "local_relative", "exports/marketing-brief.md"
        ),
    )
    service.apply(export)
    review = RecordReview(
        task_id="task-P01",
        task_revision=1,
        result_id="result-P01",
        result_revision=1,
    )
    service.apply(review)
    assert service.read(review.attempt_id)["review"] == "APPROVED"
    assert not (attempt_root / "outcome.json").exists()

    finalize = FinalizeAttempt(
        task_id="task-P01",
        task_revision=1,
        result_id="result-P01",
        result_revision=1,
        outcome=FinalDisposition.PASS,
        automated_gates=FinalizationGates(),
        cost=FinalizationCost(
            actual_micro_usd=6_783_834,
            owner_cap_micro_usd=7_000_000,
            reservation_ref="deepseek-v4-pro-2026-08-30-peak-v1",
        ),
        execution=FinalizationExecution(),
    )

    # Slice 3D GREEN: finalization persists one explicit terminal outcome and
    # never computes a cohort numerator, ratio, or exclusion classification.
    snapshot = service.apply(finalize)
    assert snapshot is not None
    assert snapshot["outcome"] == "PASS"
    outcome_path = attempt_root / "outcome.json"
    assert stat.S_IMODE(outcome_path.stat().st_mode) == 0o400
    outcome = json.loads(outcome_path.read_text())
    assert outcome == {
        "record_type": "attempt_outcome",
        "sample_id": finalize.sample_id,
        "attempt_id": finalize.attempt_id,
        "task": {
            "task_id": finalize.task_id,
            "revision": finalize.task_revision,
        },
        "result": {
            "result_id": finalize.result_id,
            "revision": finalize.result_revision,
        },
        "outcome": finalize.outcome,
        "reason_code": finalize.reason_code,
        "approved_review_id": finalize.approved_review_id,
        "selected_export_snapshot_ids": list(finalize.selected_export_snapshot_ids),
        "automated_gates": {
            "schema": finalize.automated_gates.schema,
            "domain": finalize.automated_gates.domain,
            "persistence": finalize.automated_gates.persistence,
            "export": finalize.automated_gates.export,
        },
        "cost": {
            "actual_micro_usd": finalize.cost.actual_micro_usd,
            "owner_cap_micro_usd": finalize.cost.owner_cap_micro_usd,
            "reservation_ref": finalize.cost.reservation_ref,
        },
        "execution": {
            "call_count": finalize.execution.call_count,
            "retry_count": finalize.execution.retry_count,
            "recovery_count": finalize.execution.recovery_count,
            "replay_count": finalize.execution.replay_count,
            "fallback_count": finalize.execution.fallback_count,
            "manual_intervention_count": finalize.execution.manual_intervention_count,
        },
        "immutable": finalize.immutable,
    }
    outcome_record = cast(Mapping[str, object], snapshot["outcome_record"])
    assert outcome_record["record_type"] == "attempt_outcome"
    assert outcome_record["outcome"] == finalize.outcome
    assert (
        tuple(cast(tuple[str, ...], outcome_record["selected_export_snapshot_ids"]))
        == finalize.selected_export_snapshot_ids
    )
    for forbidden in (
        "EXCLUDED",
        "numerator",
        "denominator",
        "ratio",
        "approved_export_count",
    ):
        assert forbidden not in outcome

    outcome_before_mutation = outcome_path.read_bytes()
    second_finalize = replace(finalize, reason_code="different_reason")
    with pytest.raises(AttemptArtifactError):
        service.apply(second_finalize)
    assert outcome_path.read_bytes() == outcome_before_mutation

    cross_identity = replace(finalize, sample_id="P02")
    with pytest.raises(AttemptArtifactError):
        service.apply(cross_identity)
    assert outcome_path.read_bytes() == outcome_before_mutation

    unknown_export = replace(
        finalize,
        selected_export_snapshot_ids=("export-unknown",),
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(unknown_export)
    assert outcome_path.read_bytes() == outcome_before_mutation

    over_cap = replace(
        finalize,
        cost=replace(finalize.cost, actual_micro_usd=7_000_001),
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(over_cap)
    assert outcome_path.read_bytes() == outcome_before_mutation

    retry_observed = replace(
        finalize,
        execution=replace(finalize.execution, retry_count=1),
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(retry_observed)
    assert outcome_path.read_bytes() == outcome_before_mutation
