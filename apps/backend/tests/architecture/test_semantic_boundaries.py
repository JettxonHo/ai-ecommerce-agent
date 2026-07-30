"""Semantic architecture tests (FND-002).

AST-based rules no import-edge contract can express: environment access in
core layers (RFC-001-DQ-06), technical type leakage in public contracts
(RFC-001-DQ-08) and the skill boundary (RFC-001-DQ-05). Each check runs on
the production tree (vacuous until real code lands) and on fixtures that
prove detection. All detection is static: the fixture files deliberately
import packages that are not installed (no ORM, no LangGraph in FND-002).
"""

from pathlib import Path

import pytest
from helpers import ast_scanner
from helpers.lint_runner import fixture_dir
from helpers.violations import render_all

pytestmark = pytest.mark.architecture

PRODUCTION_SRC: Path = Path(__file__).resolve().parents[2] / "src"

_PRODUCTION_CORE_GLOBS = (
    "ai_ecommerce_agent/modules/*/domain/**/*.py",
    "ai_ecommerce_agent/modules/*/application/**/*.py",
)
_FIXTURE_CORE_GLOBS = (
    "fixture_pkg/modules/*/domain/**/*.py",
    "fixture_pkg/modules/*/application/**/*.py",
)
_PRODUCTION_PUBLIC_GLOBS = ("ai_ecommerce_agent/modules/*/public/**/*.py",)
_FIXTURE_PUBLIC_GLOBS = ("fixture_pkg/modules/*/public/**/*.py",)
_PRODUCTION_SKILL_GLOBS = ("ai_ecommerce_agent/modules/*/application/skills/**/*.py",)
_FIXTURE_SKILL_GLOBS = ("fixture_pkg/modules/*/application/skills/**/*.py",)

_VALID_FIXTURES = (
    "valid_layered_package",
    "valid_public_facade_dependency",
    "valid_shared_kernel_dependency",
    "valid_orchestration_dependency",
)


def test_production_core_has_no_environment_access() -> None:
    """Core layers must never read os.environ / os.getenv / dotenv."""
    violations = ast_scanner.find_environment_access(
        PRODUCTION_SRC, _PRODUCTION_CORE_GLOBS
    )
    assert violations == [], render_all(violations)


def test_invalid_core_reads_environment_is_detected() -> None:
    """Domain os.environ, application os.getenv and dotenv import: all found."""
    violations = ast_scanner.find_environment_access(
        fixture_dir("invalid_core_reads_environment"), _FIXTURE_CORE_GLOBS
    )
    targets = {violation.illegal_target for violation in violations}
    sources = {violation.source for violation in violations}
    assert "os.environ" in targets, render_all(violations)
    assert "os.getenv" in targets, render_all(violations)
    assert "dotenv" in targets, render_all(violations)
    assert "fixture_pkg.modules.brief.domain.policy" in sources
    assert "fixture_pkg.modules.brief.application.settings_reader" in sources
    rendered = render_all(violations)
    for field in ("Rule: ", "Source: ", "Illegal Target: ", "Expected Boundary: "):
        assert field in rendered, f"missing report field {field!r}"


def test_valid_fixtures_have_no_environment_access() -> None:
    """The check must not produce false positives on legal fixtures."""
    for name in _VALID_FIXTURES:
        violations = ast_scanner.find_environment_access(
            fixture_dir(name), _FIXTURE_CORE_GLOBS
        )
        assert violations == [], f"{name}:\n{render_all(violations)}"


def test_production_public_contracts_are_clean() -> None:
    """No public contract exists yet, so nothing can leak yet."""
    violations = ast_scanner.find_public_contract_leakage(
        PRODUCTION_SRC, _PRODUCTION_PUBLIC_GLOBS
    )
    assert violations == [], render_all(violations)


def test_invalid_public_contract_exposes_technical_type_is_detected() -> None:
    """ORM base/session, workflow state and technical imports in a facade."""
    violations = ast_scanner.find_public_contract_leakage(
        fixture_dir("invalid_public_contract_exposes_technical_type"),
        _FIXTURE_PUBLIC_GLOBS,
    )
    targets = {violation.illegal_target for violation in violations}
    assert "import sqlalchemy.orm" in targets, render_all(violations)
    assert "import langgraph.graph" in targets, render_all(violations)
    assert "exposed technical type Session" in targets
    assert "exposed technical type StateGraph" in targets
    assert "exposed technical type DeclarativeBase" in targets
    assert {violation.source for violation in violations} == {
        "fixture_pkg.modules.brief.public.api"
    }


def test_valid_public_facade_fixture_is_clean() -> None:
    """A technology-neutral facade must pass the leakage check."""
    violations = ast_scanner.find_public_contract_leakage(
        fixture_dir("valid_public_facade_dependency"), _FIXTURE_PUBLIC_GLOBS
    )
    assert violations == [], render_all(violations)


def test_production_has_no_skill_boundary_violations() -> None:
    """No skills exist yet, so the boundary is unbroken (and armed)."""
    violations = ast_scanner.find_skill_boundary_violations(
        PRODUCTION_SRC, _PRODUCTION_SKILL_GLOBS, "ai_ecommerce_agent"
    )
    assert violations == [], render_all(violations)


def test_invalid_skill_boundary_is_detected() -> None:
    """A skill violating every clause of RFC-001-DQ-05 is fully reported."""
    violations = ast_scanner.find_skill_boundary_violations(
        fixture_dir("invalid_skill_boundary"), _FIXTURE_SKILL_GLOBS, "fixture_pkg"
    )
    targets = {violation.illegal_target for violation in violations}
    assert "import langgraph.graph" in targets, render_all(violations)
    assert "import sqlalchemy.orm" in targets, render_all(violations)
    assert "import spikes.prototype" in targets, render_all(violations)
    assert (
        "import repository implementation "
        "fixture_pkg.modules.brief.infrastructure.repository" in targets
    )
    assert "os.getenv" in targets, render_all(violations)
    assert "accepts a database Session parameter" in targets, render_all(violations)
    assert {violation.source for violation in violations} == {
        "fixture_pkg.modules.brief.application.skills.summary_skill"
    }
