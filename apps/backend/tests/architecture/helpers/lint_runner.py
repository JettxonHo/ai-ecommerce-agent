"""Run Import Linter against test-only fixture packages (FND-002).

The fixture contract suite (``fixtures/fixture-importlinter.ini``) mirrors
the production contracts in ``pyproject.toml`` one-to-one, rooted at the
test-only ``fixture_pkg`` package. Each fixture directory contains exactly
one ``fixture_pkg`` package; it is made importable for the run via
``PYTHONPATH`` without touching the real environment.

Running the real ``lint-imports`` CLI (rather than a private API) keeps the
fixture evidence identical to what future CI will execute.
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR: Path = Path(__file__).resolve().parents[3]
FIXTURES_DIR: Path = Path(__file__).resolve().parents[1] / "fixtures"
FIXTURE_CONTRACTS_CONFIG: Path = FIXTURES_DIR / "fixture-importlinter.ini"

_SUBPROCESS_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class LintResult:
    """Captured outcome of one ``lint-imports`` run."""

    exit_code: int
    output: str

    @property
    def passed(self) -> bool:
        """True when every contract was kept (exit status 0)."""
        return self.exit_code == 0


def fixture_dir(name: str) -> Path:
    """Resolve a fixture directory by name, asserting it exists.

    Negative tests must never pass because a fixture path silently
    vanished; a missing fixture is a hard test error.
    """
    path = FIXTURES_DIR / name
    assert path.is_dir(), f"architecture fixture directory is missing: {path}"
    assert (path / "fixture_pkg").is_dir(), (
        f"fixture has no fixture_pkg package: {path}"
    )
    return path


def run_lint_imports(fixture: Path) -> LintResult:
    """Run the fixture contract suite against one fixture package."""
    environment = {**os.environ, "PYTHONPATH": str(fixture)}
    completed = subprocess.run(
        ["lint-imports", "--config", str(FIXTURE_CONTRACTS_CONFIG)],
        cwd=BACKEND_DIR,
        env=environment,
        capture_output=True,
        text=True,
        timeout=_SUBPROCESS_TIMEOUT_SECONDS,
        check=False,
    )
    return LintResult(
        exit_code=completed.returncode,
        output=completed.stdout + completed.stderr,
    )


def assert_contracts_kept(result: LintResult) -> None:
    """Assert a clean run that is not secretly a configuration failure."""
    assert "not configured correctly" not in result.output, result.output
    assert "does not exist" not in result.output, result.output
    assert result.passed, f"expected all fixture contracts kept:\n{result.output}"


def assert_contract_broken(
    result: LintResult,
    contract_name: str,
    *,
    expected_fragments: tuple[str, ...],
) -> None:
    """Assert one named contract broke for the expected reason.

    Guards against false negatives in three ways: the run must not be a
    misconfiguration error, the named contract must be reported BROKEN,
    and every expected fragment (source/target modules) must appear in
    the violation report.
    """
    assert "not configured correctly" not in result.output, result.output
    assert "does not exist" not in result.output, result.output
    assert not result.passed, f"expected a broken contract:\n{result.output}"
    assert f"{contract_name} BROKEN" in result.output, (
        f"contract {contract_name!r} was not reported broken:\n{result.output}"
    )
    for fragment in expected_fragments:
        assert fragment in result.output, (
            f"expected fragment {fragment!r} in report:\n{result.output}"
        )
