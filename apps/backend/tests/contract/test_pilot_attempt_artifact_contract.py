"""Provider-free contract for the bounded P2 attempt artifact seam."""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

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
    IdempotencyBundle,
    PilotAttemptArtifacts,
    RecordReview,
    RecordRun,
    ReserveAttempt,
    ReviewDimension,
    UnknownValue,
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


def _idempotency_bundle() -> IdempotencyBundle:
    return IdempotencyBundle.for_identity("P01", "P2-P01-A1")


def test_precommitted_idempotency_bundle_is_complete_and_deterministic() -> None:
    first = _idempotency_bundle()
    second = IdempotencyBundle.for_identity("P01", "P2-P01-A1")

    assert first == second
    assert first.sample_id == "P01"
    assert first.attempt_id == "P2-P01-A1"
    assert first.to_mapping() == {
        "sample_id": "P01",
        "attempt_id": "P2-P01-A1",
        "task_create": "operator-P2-P01-A1-task",
        "generate": "operator-P2-P01-A1-generate",
        "confirm": "operator-P2-P01-A1-confirm",
        "marketing_export": "operator-P2-P01-A1-export-marketing",
        "xiaohongshu_export": "operator-P2-P01-A1-export-xiaohongshu",
    }


def test_precommitted_bundle_cannot_be_reused_for_altered_identity() -> None:
    bundle = _idempotency_bundle()
    with pytest.raises((TypeError, ValueError)):
        IdempotencyBundle.from_value({**bundle.to_mapping(), "sample_id": "P02"})
    with pytest.raises((TypeError, ValueError)):
        IdempotencyBundle.for_identity("P02", "P2-P02-A1")
    assert bundle == IdempotencyBundle.for_identity("P01", "P2-P01-A1")


def test_reservation_persists_bundle_for_fresh_read(tmp_path: Path) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    attempt_root = approved_parent / "p2" / "P01" / "P2-P01-A1"
    bundle = _idempotency_bundle()

    service.apply(ReserveAttempt(attempt_root, idempotency_bundle=bundle))

    identity = json.loads((attempt_root / "identity.json").read_text())
    assert identity["idempotency_bundle"] == bundle.to_mapping()
    fresh = PilotAttemptArtifacts(Path(__file__).resolve().parents[4], approved_parent)
    fresh_identity = cast(Mapping[str, object], fresh.read("P2-P01-A1")["identity"])
    assert fresh_identity["idempotency_bundle"] == bundle.to_mapping()


def _approved_review_kwargs() -> dict[str, Any]:
    return {
        "dimensions": (
            ReviewDimension("product_fact_correctness", "PASS", True),
            ReviewDimension("mandatory_messages", "PASS", True),
            ReviewDimension("prohibited_claims", "PASS", True),
            ReviewDimension("fabrication_misleading_content", "PASS", True),
            ReviewDimension("marketing_brief_usability", "PASS", True),
            ReviewDimension("xiaohongshu_consistency", "NOT_APPLICABLE", False),
            ReviewDimension("markdown_delivery", "PASS", True),
        ),
        "overall": "APPROVED",
        "rationale": "approved_all_applicable_critical_dimensions_pass",
    }


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
    assert run["cost"]["actual_micro_usd"] == "NOT_EXPOSED"
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


def test_root_validation_requires_exact_p2_attempt_destination(tmp_path: Path) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    with pytest.raises(AttemptArtifactError) as error:
        service.apply(ReserveAttempt(approved_parent / "p2" / "P01" / "other-attempt"))
    assert error.value.error_code == ArtifactErrorCode.ROOT_NOT_ALLOWED.value


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
    fresh_service = PilotAttemptArtifacts(
        Path(__file__).resolve().parents[4], approved_parent
    )
    assert fresh_service.read(probe.attempt_id)["exports"] == exports
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
        captured_export_snapshot_ids=(export.export_snapshot_id,),
        **_approved_review_kwargs(),
    )

    # Slice 3C GREEN: the review command is provider-free and persists exactly
    # one immutable, sanitized decision bound to the captured export.
    snapshot = service.apply(review)
    assert snapshot is not None
    assert snapshot["review"] == "APPROVED"
    assert review.dimensions is not None
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


def test_rejected_review_keeps_inspected_export_bindings_without_approval(
    tmp_path: Path,
) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    _reserve(service, approved_parent)
    service.apply(
        RecordRun(
            task_id="task-real-1",
            task_revision=1,
            result_id="result-real-1",
            result_revision=1,
        )
    )
    export = CaptureExport(
        task_id="task-real-1",
        task_revision=1,
        result_id="result-real-1",
        result_revision=1,
        brief_version=ExportVersionReference("brief-real-1", 1),
        content_reference=ExportContentReference(
            "local_relative", "exports/marketing-brief.md"
        ),
    )
    service.apply(export)
    rejected = RecordReview(
        task_id="task-real-1",
        task_revision=1,
        result_id="result-real-1",
        result_revision=1,
        captured_export_snapshot_ids=(export.export_snapshot_id,),
        dimensions=(
            ReviewDimension("product_fact_correctness", "FAIL", True),
            ReviewDimension("mandatory_messages", "PASS", True),
            ReviewDimension("prohibited_claims", "PASS", True),
            ReviewDimension("fabrication_misleading_content", "PASS", True),
            ReviewDimension("marketing_brief_usability", "PASS", True),
            ReviewDimension("xiaohongshu_consistency", "NOT_APPLICABLE", False),
            ReviewDimension("markdown_delivery", "PASS", True),
        ),
        overall="REJECTED",
        rationale="rejected_critical_dimension_or_export",
    )
    rejected_all_pass = replace(
        rejected,
        review_id="review-P2-P01-A1-all-pass-rejected",
        dimensions=cast(
            tuple[ReviewDimension, ...], _approved_review_kwargs()["dimensions"]
        ),
    )
    with pytest.raises(AttemptArtifactError):
        service.apply(rejected_all_pass)
    snapshot = service.apply(rejected)
    assert snapshot is not None
    record = cast(Mapping[str, object], snapshot["review_record"])
    assert record["overall"] == "REJECTED"
    assert record["captured_export_snapshot_ids"] == (export.export_snapshot_id,)


def test_usage_and_cost_unknowns_are_typed_in_durable_run_projection(
    tmp_path: Path,
) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    attempt_root = _reserve(service, approved_parent)
    service.apply(
        RecordRun(
            task_id="task-real-2",
            task_revision=1,
            result_id="result-real-2",
            result_revision=1,
            calls=({"model_call_id": "call-real-2"},),
            usage=None,
            cost=None,
        )
    )
    run = json.loads((attempt_root / "run.json").read_text())
    assert isinstance(run["usage"], dict)
    assert isinstance(run["cost"], dict)
    assert run["usage"] == {
        "input_tokens": "NOT_EXPOSED",
        "output_tokens": "NOT_EXPOSED",
        "total_tokens": "NOT_EXPOSED",
    }
    assert run["cost"] == {
        "reserved_micro_usd": "UNKNOWN",
        "actual_micro_usd": "NOT_EXPOSED",
        "currency": "NOT_DERIVABLE",
    }
    assert run["calls"][0]["usage"] == {
        "input_tokens": "NOT_EXPOSED",
        "output_tokens": "NOT_EXPOSED",
        "total_tokens": "NOT_EXPOSED",
    }


def test_review_and_finalize_do_not_infer_approval_or_actual_cost() -> None:
    review = RecordReview()
    finalize = FinalizeAttempt()
    assert review.overall is None
    assert review.dimensions is None
    assert review.captured_export_snapshot_ids == ()
    assert finalize.outcome is None
    assert finalize.cost is None


@pytest.mark.parametrize(
    "reason_code",
    (
        "review_rejected",
        "automated_gate_failed",
        "cost_cap_exceeded",
        "execution_not_qualified",
        "missing_export",
    ),
)
def test_nonpass_reason_codes_require_matching_evidence(
    tmp_path: Path, reason_code: str
) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    _reserve(service, approved_parent)
    service.apply(
        RecordRun(
            task_id="task-reason",
            task_revision=1,
            result_id="result-reason",
            result_revision=1,
            call_count=5,
            calls=tuple({"model_call_id": f"call-{index}"} for index in range(1, 6)),
            gates={
                "schema": True,
                "domain": True,
                "persistence": True,
                "export": reason_code != "missing_export",
            },
            cost={"reserved_micro_usd": 100, "actual_micro_usd": 100},
        )
    )
    command = FinalizeAttempt(
        task_id="task-reason",
        task_revision=1,
        result_id="result-reason",
        result_revision=1,
        outcome=FinalDisposition.FAIL,
        reason_code=reason_code,
        approved_review_id=None,
        selected_export_snapshot_ids=(),
        automated_gates=FinalizationGates(
            schema=True,
            domain=True,
            persistence=True,
            export=reason_code != "missing_export",
        ),
        cost=FinalizationCost(
            actual_micro_usd=100,
            owner_cap_micro_usd=200,
            reservation_ref="pricing-reason",
        ),
        execution=FinalizationExecution(
            call_count=5,
            retry_count=0,
            recovery_count=0,
            replay_count=0,
            fallback_count=0,
            manual_intervention_count=0,
        ),
    )
    if reason_code == "missing_export":
        snapshot = service.apply(command)
        assert snapshot is not None
        assert snapshot["outcome"] == "FAIL"
    else:
        with pytest.raises(AttemptArtifactError):
            service.apply(command)


@pytest.mark.parametrize(
    "reason_code",
    (
        "review_rejected",
        "automated_gate_failed",
        "cost_cap_exceeded",
        "execution_not_qualified",
        "missing_export",
    ),
)
def test_supported_nonpass_reason_codes_accept_matching_evidence(
    tmp_path: Path, reason_code: str
) -> None:
    service, approved_parent = _artifact_service(tmp_path)
    _reserve(service, approved_parent)
    gates = {
        "schema": True,
        "domain": True,
        "persistence": True,
        "export": reason_code not in {"automated_gate_failed", "missing_export"},
    }
    call_count = 4 if reason_code == "execution_not_qualified" else 5
    actual_cost = 300 if reason_code == "cost_cap_exceeded" else 0
    service.apply(
        RecordRun(
            task_id="task-supported",
            task_revision=1,
            result_id="result-supported",
            result_revision=1,
            call_count=call_count,
            calls=tuple(
                {"model_call_id": f"call-{index}"} for index in range(1, call_count + 1)
            ),
            gates=gates,
            pricing_record_id="pricing-supported",
            cost={"reserved_micro_usd": 100, "actual_micro_usd": actual_cost},
        )
    )
    captured_export_ids: tuple[str, ...] = ()
    if reason_code == "review_rejected":
        export_id = "export-supported"
        captured_export_ids = (export_id,)
        service.apply(
            CaptureExport(
                task_id="task-supported",
                task_revision=1,
                result_id="result-supported",
                result_revision=1,
                export_snapshot_id=export_id,
                brief_version=ExportVersionReference("brief-supported", 1),
                content_reference=ExportContentReference(
                    "local_relative", "exports/marketing-brief.md"
                ),
            )
        )
        service.apply(
            RecordReview(
                task_id="task-supported",
                task_revision=1,
                result_id="result-supported",
                result_revision=1,
                captured_export_snapshot_ids=captured_export_ids,
                dimensions=(
                    ReviewDimension("product_fact_correctness", "FAIL", True),
                    ReviewDimension("mandatory_messages", "PASS", True),
                    ReviewDimension("prohibited_claims", "PASS", True),
                    ReviewDimension("fabrication_misleading_content", "PASS", True),
                    ReviewDimension("marketing_brief_usability", "PASS", True),
                    ReviewDimension("xiaohongshu_consistency", "NOT_APPLICABLE", False),
                    ReviewDimension("markdown_delivery", "PASS", True),
                ),
                overall="REJECTED",
                rationale="rejected_critical_dimension_or_export",
            )
        )
    command = FinalizeAttempt(
        task_id="task-supported",
        task_revision=1,
        result_id="result-supported",
        result_revision=1,
        outcome=(
            FinalDisposition.BLOCKED
            if reason_code == "cost_cap_exceeded"
            else FinalDisposition.FAIL
        ),
        reason_code=reason_code,
        selected_export_snapshot_ids=(),
        automated_gates=FinalizationGates(**gates),
        cost=FinalizationCost(
            actual_micro_usd=actual_cost,
            owner_cap_micro_usd=200,
            reservation_ref="pricing-supported",
        ),
        execution=FinalizationExecution(
            call_count=call_count,
            retry_count=0,
            recovery_count=0,
            replay_count=0,
            fallback_count=0,
            manual_intervention_count=0,
        ),
    )
    snapshot = service.apply(command)
    assert snapshot is not None
    assert snapshot["outcome"] == command.outcome


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
                {
                    "model_call_id": f"P2-P01-A1-stage-{index}",
                    "latency_ms": 100,
                    "status": "COMPLETED",
                }
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
        captured_export_snapshot_ids=(export.export_snapshot_id,),
        **_approved_review_kwargs(),
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
        reason_code="qualifying_approved_export",
        approved_review_id=review.review_id,
        selected_export_snapshot_ids=(export.export_snapshot_id,),
        automated_gates=FinalizationGates(),
        cost=FinalizationCost(
            actual_micro_usd=6_783_834,
            owner_cap_micro_usd=7_000_000,
            reservation_ref="deepseek-v4-pro-2026-08-30-peak-v1",
        ),
        execution=FinalizationExecution(),
    )
    assert finalize.automated_gates is not None
    assert finalize.cost is not None
    assert finalize.execution is not None

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


def test_pass_rejects_durable_phase_metadata() -> None:
    """Phase-specific failure metadata is only valid on non-PASS outcomes."""

    command = cast(Any, FinalizeAttempt)(
        outcome=FinalDisposition.PASS,
        reason_code="qualifying_approved_export",
        error_category="operator_failure",
        terminal_stage="confirmation",
    )
    with pytest.raises(AttemptArtifactError):
        PilotAttemptArtifacts._validate_finalize(  # pyright: ignore[reportPrivateUsage]
            command
        )


@pytest.mark.parametrize(
    ("reserved_micro_usd", "owner_cap_micro_usd", "reject"),
    (
        (UnknownValue.UNKNOWN, 6_783_834, True),
        (6_783_835, 6_783_834, True),
        (6_783_834, 6_783_834, False),
    ),
)
def test_unknown_actual_pass_requires_known_reservation_within_owner_cap(
    tmp_path: Path,
    reserved_micro_usd: int | UnknownValue,
    owner_cap_micro_usd: int,
    reject: bool,
) -> None:
    """An unknown actual cannot turn an absent/over-cap reservation into PASS."""

    service, approved_parent = _artifact_service(tmp_path)
    _reserve(service, approved_parent)
    task_id = "task-unknown-cost"
    result_id = f"{task_id}:r1"
    service.apply(
        RecordRun(
            task_id=task_id,
            task_revision=1,
            result_id=result_id,
            result_revision=1,
            call_count=5,
            calls=tuple(
                {
                    "model_call_id": f"P2-P01-A1-stage-{index}",
                    "status": "COMPLETED",
                }
                for index in range(1, 6)
            ),
            gates={"schema": True, "domain": True, "persistence": True},
            pricing_record_id="deepseek-v4-pro-2026-08-30-peak-v1",
            cost={
                "reserved_micro_usd": reserved_micro_usd,
                "actual_micro_usd": UnknownValue.NOT_DERIVABLE,
            },
        )
    )
    export = CaptureExport(
        task_id=task_id,
        task_revision=1,
        result_id=result_id,
        result_revision=1,
        brief_version=ExportVersionReference("brief-unknown-cost-v1", 1),
        content_reference=ExportContentReference(
            "local_relative", "exports/marketing-brief.md"
        ),
    )
    service.apply(export)
    review = RecordReview(
        task_id=task_id,
        task_revision=1,
        result_id=result_id,
        result_revision=1,
        captured_export_snapshot_ids=(export.export_snapshot_id,),
        **_approved_review_kwargs(),
    )
    service.apply(review)
    finalize = FinalizeAttempt(
        task_id=task_id,
        task_revision=1,
        result_id=result_id,
        result_revision=1,
        outcome=FinalDisposition.PASS,
        reason_code="qualifying_approved_export",
        approved_review_id=review.review_id,
        selected_export_snapshot_ids=(export.export_snapshot_id,),
        automated_gates=FinalizationGates(),
        cost=FinalizationCost(
            actual_micro_usd=UnknownValue.NOT_DERIVABLE,
            owner_cap_micro_usd=owner_cap_micro_usd,
            reservation_ref="deepseek-v4-pro-2026-08-30-peak-v1",
        ),
        execution=FinalizationExecution(),
    )

    if reject:
        with pytest.raises(AttemptArtifactError):
            service.apply(finalize)
    else:
        snapshot = service.apply(finalize)
        assert snapshot is not None
        assert snapshot["outcome"] == "PASS"
