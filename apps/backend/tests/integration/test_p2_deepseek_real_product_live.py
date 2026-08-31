"""Opt-in P2 runner seam; real Provider execution remains gated and skipped."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NoReturn

import pytest

pytestmark = pytest.mark.live

P2_SAMPLE_ID: Final[str] = "P01"
P2_ATTEMPT_ID: Final[str] = "P2-P01-A1"
P2_PRODUCT_NAME: Final[str] = "Anker Nano Power Bank"
P2_MODEL_DESIGNATION: Final[str] = "A1259"
P2_COLOR: Final[str] = "Black Stone"
P2_VARIANT: Final[str] = "42733233766550"
P2_CATEGORY: Final[str] = "A"
P2_MAX_CALLS: Final[int] = 5
P2_P2_CONTEXT_VERSION: Final[str] = "pilot-p2-v1"
P2_GIT_COMMIT: Final[str] = "8c43068038d4c3859383d68263f0ab0336480f6a"
P2_PRICING_RECORD_ID: Final[str] = "deepseek-v4-pro-2026-08-30-peak-v1"
P2_RESERVATION_MICRO_USD: Final[int] = 6_783_834
P2_PRIVATE_INPUTS_ROOT: Final[Path] = Path(
    "/Users/ketchup/Private/ai-ecommerce-pilot/inputs"
)
P2_PRIVATE_ARTIFACT_PARENT: Final[Path] = Path(
    "/Users/ketchup/Private/ai-ecommerce-pilot/p2"
)
P2_PRIVATE_ARTIFACT_ROOT: Final[Path] = (
    P2_PRIVATE_ARTIFACT_PARENT / P2_SAMPLE_ID / P2_ATTEMPT_ID
)
P2_OPT_IN_ENVIRONMENT: Final[str] = "AI_ECOMMERCE_RUN_P2_REAL"


class P2LiveControlError(ValueError):
    """Fixed safe preflight/runner error with no path or secret leakage."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(f"{code}:preflight")


@dataclass(frozen=True, slots=True)
class P2LiveControlConfig:
    """Sanitized immutable controls; input content is intentionally absent."""

    sample_id: str
    attempt_id: str
    git_commit: str
    product_name: str
    model_designation: str
    color: str
    variant: str
    category: str
    owner_cap_micro_usd: int
    pricing_record_id: str
    max_calls: int
    retry_count: int
    recovery_count: int
    replay_count: int
    fallback_count: int
    manual_intervention_count: int
    input_path: Path
    artifact_root: Path
    approved_artifact_root: Path
    repository_root: Path


@dataclass(frozen=True, slots=True)
class P2RunEvidence:
    """Sanitized result metadata returned by an injected P2 composition."""

    task_id: str
    task_revision: int
    result_id: str
    result_revision: int
    call_ids: tuple[str, ...]
    provider_id: str = "deepseek"
    retry_count: int = 0
    recovery_count: int = 0
    replay_count: int = 0
    fallback_count: int = 0
    manual_intervention_count: int = 0


@dataclass(frozen=True, slots=True)
class P2ExportEvidence:
    """One immutable sanitized export reference and its bytes."""

    kind: str
    export_snapshot_id: str
    content_bytes: bytes
    immutable: bool = True


InputReader = Callable[[Path], str]
ArtifactReserver = Callable[[Path], None]
P2Composer = Callable[[str, P2LiveControlConfig], P2RunEvidence]
RunRecorder = Callable[[P2RunEvidence], None]
ExportCapturer = Callable[
    [P2RunEvidence, P2LiveControlConfig], tuple[P2ExportEvidence, ...]
]
ReviewPendingRecorder = Callable[[P2RunEvidence, tuple[P2ExportEvidence, ...]], None]
RuntimeCloser = Callable[[], None]


@dataclass(frozen=True, slots=True)
class P2RunnerDependencies:
    """Explicit injected side-effect bundle used by provider-free tests."""

    read_input: InputReader
    reserve_artifact: ArtifactReserver
    compose_deepseek: P2Composer
    record_run: RunRecorder
    capture_exports: ExportCapturer
    record_review_pending: ReviewPendingRecorder
    close_runtime: RuntimeCloser = lambda: None


@dataclass(frozen=True, slots=True)
class P2ExecutionResult:
    """Provider-neutral post-run state before human review/outcome."""

    run: P2RunEvidence
    exports: tuple[P2ExportEvidence, ...]
    review_state: str = "PENDING"
    outcome: None = None


@dataclass(frozen=True, slots=True)
class PreparedP2Attempt:
    """Lazy one-shot P2 execution seam with no construction side effects."""

    controls: P2LiveControlConfig
    dependencies: P2RunnerDependencies
    _executed: list[bool] = field(
        default_factory=lambda: [False], repr=False, compare=False
    )

    def execute(self) -> P2ExecutionResult:
        if self._executed[0]:
            raise P2LiveControlError("attempt_already_executed")
        self._executed[0] = True
        dependencies = self.dependencies
        runtime_started = False
        try:
            content = dependencies.read_input(self.controls.input_path)
            if type(content) is not str or not content.strip():
                raise P2LiveControlError("input_content_invalid")
            dependencies.reserve_artifact(self.controls.artifact_root)
            runtime_started = True
            run = dependencies.compose_deepseek(content, self.controls)
            _validate_run_evidence(run, self.controls)
            dependencies.record_run(run)
            exports = dependencies.capture_exports(run, self.controls)
            _validate_export_evidence(exports, run, self.controls)
            dependencies.record_review_pending(run, exports)
            return P2ExecutionResult(run=run, exports=exports)
        finally:
            if runtime_started:
                dependencies.close_runtime()


def _fail(code: str) -> NoReturn:
    raise P2LiveControlError(code)


def _preflight_controls(
    *,
    live_execution_enabled: bool,
    provider_access_enabled: bool,
    git_commit: str,
    git_head: str,
    sample_id: str,
    attempt_id: str,
    product_name: str,
    model_designation: str,
    color: str,
    variant: str,
    category: str,
    owner_cap_micro_usd: int,
    pricing_record_id: str,
    max_calls: int,
    retry_count: int,
    recovery_count: int,
    replay_count: int,
    fallback_count: int,
    manual_intervention_count: int,
    input_path: Path,
    approved_inputs_root: Path,
    artifact_root: Path,
    approved_artifact_root: Path,
    repository_root: Path,
) -> P2LiveControlConfig:
    """Validate all controls before reading content or creating artifacts."""

    if type(live_execution_enabled) is not bool or not live_execution_enabled:
        _fail("live_execution_flag_required")
    if type(provider_access_enabled) is not bool or not provider_access_enabled:
        _fail("provider_access_flag_required")
    if type(git_commit) is not str or git_commit != git_head:
        _fail("git_head_mismatch")
    if type(git_commit) is not str or not git_commit.strip():
        _fail("git_commit_invalid")
    if sample_id != P2_SAMPLE_ID or attempt_id != P2_ATTEMPT_ID:
        _fail("attempt_identity_mismatch")
    if (
        product_name != P2_PRODUCT_NAME
        or model_designation != P2_MODEL_DESIGNATION
        or color != P2_COLOR
        or variant != P2_VARIANT
        or category != P2_CATEGORY
    ):
        _fail("admitted_product_identity_mismatch")
    if type(owner_cap_micro_usd) is not int or owner_cap_micro_usd <= 0:
        _fail("owner_cap_invalid")
    if owner_cap_micro_usd < P2_RESERVATION_MICRO_USD:
        _fail("owner_cap_underfunded")
    if pricing_record_id != P2_PRICING_RECORD_ID:
        _fail("pricing_record_mismatch")
    if max_calls != P2_MAX_CALLS:
        _fail("max_calls_mismatch")
    counts = (
        max_calls,
        retry_count,
        recovery_count,
        replay_count,
        fallback_count,
        manual_intervention_count,
    )
    if any(type(count) is not int for count in counts):
        _fail("execution_count_invalid")
    if any(count != 0 for count in counts[1:]):
        _fail("retry_or_fallback_not_zero")
    if not approved_inputs_root.is_absolute() or approved_inputs_root.is_symlink():
        _fail("approved_input_root_invalid")
    if not approved_inputs_root.is_dir():
        _fail("approved_input_root_invalid")
    if (
        not input_path.is_absolute()
        or input_path.is_symlink()
        or not input_path.is_file()
    ):
        _fail("input_path_invalid")
    try:
        input_path.relative_to(approved_inputs_root)
    except ValueError:
        _fail("input_path_outside_approved_root")
    if any(
        token in input_path.name.casefold()
        for token in ("anchor", "backpack", "scripted")
    ):
        _fail("fixture_input_rejected")
    if not approved_artifact_root.is_absolute() or approved_artifact_root.is_symlink():
        _fail("approved_artifact_root_invalid")
    if not approved_artifact_root.is_dir():
        _fail("approved_artifact_root_invalid")
    if not artifact_root.is_absolute():
        _fail("artifact_root_invalid")
    if artifact_root.is_symlink() or artifact_root.exists():
        _fail("artifact_root_must_be_absent")
    if artifact_root != approved_artifact_root / P2_SAMPLE_ID / P2_ATTEMPT_ID:
        _fail("artifact_root_mismatch")
    try:
        artifact_root.relative_to(repository_root)
    except ValueError:
        pass
    else:
        _fail("artifact_root_inside_repository")
    if any(
        token
        in " ".join(
            (product_name, model_designation, color, variant, category)
        ).casefold()
        for token in ("anchor", "backpack", "scripted")
    ):
        _fail("fixture_product_rejected")
    return P2LiveControlConfig(
        sample_id=sample_id,
        attempt_id=attempt_id,
        git_commit=git_commit,
        product_name=product_name,
        model_designation=model_designation,
        color=color,
        variant=variant,
        category=category,
        owner_cap_micro_usd=owner_cap_micro_usd,
        pricing_record_id=pricing_record_id,
        max_calls=max_calls,
        retry_count=retry_count,
        recovery_count=recovery_count,
        replay_count=replay_count,
        fallback_count=fallback_count,
        manual_intervention_count=manual_intervention_count,
        input_path=input_path,
        artifact_root=artifact_root,
        approved_artifact_root=approved_artifact_root,
        repository_root=repository_root,
    )


def prepare_p2_attempt(
    controls: P2LiveControlConfig,
    dependencies: P2RunnerDependencies | None = None,
) -> PreparedP2Attempt:
    """Prepare lazily; dependency factories are not touched here."""

    if type(controls) is not P2LiveControlConfig:
        raise TypeError("controls must be P2LiveControlConfig")
    if dependencies is None:
        _fail("postgres_operator_dependencies_required")
    if type(dependencies) is not P2RunnerDependencies:
        raise TypeError("dependencies must be P2RunnerDependencies")
    return PreparedP2Attempt(controls=controls, dependencies=dependencies)


def _required_environment_value(name: str) -> str:
    value = os.environ.get(name, "")
    if not value.strip():
        _fail("live_environment_incomplete")
    return value


def _required_environment_int(name: str) -> int:
    value = _required_environment_value(name)
    try:
        return int(value)
    except ValueError:
        _fail("live_environment_invalid")


def _controls_from_environment() -> P2LiveControlConfig:
    """Read only explicit live controls; no content or Secret is read here."""

    repository_root = Path(__file__).resolve().parents[3]
    return _preflight_controls(
        live_execution_enabled=os.environ.get("AI_ECOMMERCE_P2_LIVE") == "1",
        provider_access_enabled=os.environ.get("AI_ECOMMERCE_P2_PROVIDER_ACCESS")
        == "1",
        git_commit=_required_environment_value("AI_ECOMMERCE_P2_GIT_COMMIT"),
        git_head=_required_environment_value("AI_ECOMMERCE_P2_GIT_HEAD"),
        sample_id=P2_SAMPLE_ID,
        attempt_id=P2_ATTEMPT_ID,
        product_name=P2_PRODUCT_NAME,
        model_designation=P2_MODEL_DESIGNATION,
        color=P2_COLOR,
        variant=P2_VARIANT,
        category=P2_CATEGORY,
        owner_cap_micro_usd=_required_environment_int("AI_ECOMMERCE_P2_OWNER_CAP"),
        pricing_record_id=_required_environment_value("AI_ECOMMERCE_P2_PRICING_RECORD"),
        max_calls=_required_environment_int("AI_ECOMMERCE_P2_MAX_CALLS"),
        retry_count=_required_environment_int("AI_ECOMMERCE_P2_RETRY_COUNT"),
        recovery_count=_required_environment_int("AI_ECOMMERCE_P2_RECOVERY_COUNT"),
        replay_count=_required_environment_int("AI_ECOMMERCE_P2_REPLAY_COUNT"),
        fallback_count=_required_environment_int("AI_ECOMMERCE_P2_FALLBACK_COUNT"),
        manual_intervention_count=_required_environment_int(
            "AI_ECOMMERCE_P2_MANUAL_INTERVENTION_COUNT"
        ),
        input_path=Path(_required_environment_value("AI_ECOMMERCE_P2_INPUT_PATH")),
        approved_inputs_root=P2_PRIVATE_INPUTS_ROOT,
        artifact_root=P2_PRIVATE_ARTIFACT_ROOT,
        approved_artifact_root=P2_PRIVATE_ARTIFACT_PARENT,
        repository_root=repository_root,
    )


def _validate_run_evidence(run: P2RunEvidence, controls: P2LiveControlConfig) -> None:
    if type(run) is not P2RunEvidence:
        _fail("run_evidence_invalid")
    if (
        type(run.task_id) is not str
        or not run.task_id.strip()
        or any(character in run.task_id for character in "\r\n")
        or type(run.result_id) is not str
        or not run.result_id.strip()
        or any(character in run.result_id for character in "\r\n")
        or type(run.task_revision) is not int
        or isinstance(run.task_revision, bool)
        or run.task_revision < 0
        or type(run.result_revision) is not int
        or isinstance(run.result_revision, bool)
        or run.result_revision < 0
        or run.result_id != f"{run.task_id}:r{run.result_revision}"
    ):
        _fail("run_identity_or_provider_mismatch")
    if run.provider_id != "deepseek" or run.call_ids != tuple(
        f"P2-P01-A1-stage-{index}" for index in range(1, P2_MAX_CALLS + 1)
    ):
        _fail("run_identity_or_provider_mismatch")
    if len(run.call_ids) != controls.max_calls:
        _fail("run_call_count_mismatch")
    if any(
        count != 0
        for count in (
            run.retry_count,
            run.recovery_count,
            run.replay_count,
            run.fallback_count,
            run.manual_intervention_count,
        )
    ):
        _fail("run_retry_or_fallback_not_zero")


def _validate_export_evidence(
    exports: tuple[P2ExportEvidence, ...],
    run: P2RunEvidence,
    controls: P2LiveControlConfig,
) -> None:
    if type(exports) is not tuple or not 1 <= len(exports) <= 2:
        _fail("export_selection_invalid")
    seen: set[str] = set()
    for export in exports:
        if type(export) is not P2ExportEvidence:
            _fail("export_evidence_invalid")
        if export.kind not in {"marketing", "xiaohongshu"}:
            _fail("export_kind_invalid")
        if export.export_snapshot_id in seen:
            _fail("export_identity_duplicate")
        seen.add(export.export_snapshot_id)
        if export.immutable is not True:
            _fail("export_not_immutable")
        if type(export.content_bytes) is not bytes:
            _fail("export_bytes_invalid")
        try:
            export.content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            _fail("export_bytes_invalid")
    if controls.sample_id != P2_SAMPLE_ID:
        _fail("export_identity_mismatch")


@pytest.mark.skipif(
    os.environ.get(P2_OPT_IN_ENVIRONMENT) != "1",
    reason="P2 real-product runner requires explicit opt-in",
)
def test_p2_deepseek_real_product_runner_requires_all_owner_controls() -> None:
    """Opt-in flags alone never trigger an unbound default runner."""

    controls = _controls_from_environment()
    with pytest.raises(P2LiveControlError) as error:
        prepare_p2_attempt(controls)
    assert error.value.code == "postgres_operator_dependencies_required"
