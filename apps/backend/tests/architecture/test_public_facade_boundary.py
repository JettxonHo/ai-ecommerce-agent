"""Public facade boundary verification (FND-002, RFC-001-DQ-08).

Cross-module imports may only target ``modules.<target>.public``. This rule
needs same-module-relative reasoning that Import Linter's built-in contracts
cannot express, so it runs as a custom check on the grimp graph (the same
engine Import Linter uses). Fixtures prove detection; one fixture also shows
the Import Linter suite alone stays green there — the concrete evidence that
this custom check is not redundant.
"""

import pytest
from helpers.lint_runner import assert_contracts_kept, fixture_dir, run_lint_imports
from helpers.module_graph import (
    FIXTURE_ROOT_PACKAGE,
    PRODUCTION_ROOT_PACKAGE,
    FixtureGraphScope,
    build_production_graph,
)
from helpers.rules import FACADE_RULE, find_facade_violations
from helpers.violations import render_all

pytestmark = pytest.mark.architecture

_REPORT_FIELDS = ("Rule: ", "Source: ", "Illegal Target: ", "Expected Boundary: ")


def test_production_has_no_facade_violations() -> None:
    """Vacuous today (no business modules yet) and live from the first one."""
    violations = find_facade_violations(
        build_production_graph(), PRODUCTION_ROOT_PACKAGE
    )
    assert violations == [], render_all(violations)


def test_valid_public_facade_dependency_passes() -> None:
    """Cross-module import through ``.public`` is legal and stays clean."""
    with FixtureGraphScope(fixture_dir("valid_public_facade_dependency")) as graph:
        violations = find_facade_violations(graph, FIXTURE_ROOT_PACKAGE)
    assert violations == [], render_all(violations)


def test_valid_orchestration_dependency_passes() -> None:
    """Orchestration importing module public contracts is legal."""
    with FixtureGraphScope(fixture_dir("valid_orchestration_dependency")) as graph:
        violations = find_facade_violations(graph, FIXTURE_ROOT_PACKAGE)
    assert violations == [], render_all(violations)


def test_cross_module_private_import_is_detected() -> None:
    """beta.application reaching into alpha.domain must be reported."""
    with FixtureGraphScope(fixture_dir("invalid_cross_module_private_import")) as graph:
        violations = find_facade_violations(graph, FIXTURE_ROOT_PACKAGE)
    assert violations, "facade violation was not detected"
    violation = violations[0]
    assert violation.rule == FACADE_RULE
    assert violation.source == "fixture_pkg.modules.beta.application.service"
    assert violation.illegal_target == "fixture_pkg.modules.alpha.domain.model"
    assert violation.expected_boundary == "fixture_pkg.modules.alpha.public"
    rendered = render_all(violations)
    for field in _REPORT_FIELDS:
        assert field in rendered, f"missing report field {field!r} in:\n{rendered}"


def test_cross_module_private_import_is_outside_import_linter_reach() -> None:
    """The Import Linter suite alone stays green on this fixture.

    Evidence that the facade rule genuinely requires this custom checker:
    no built-in contract expresses "same module may, other modules may not".
    """
    assert_contracts_kept(
        run_lint_imports(fixture_dir("invalid_cross_module_private_import"))
    )


def test_orchestration_imports_infrastructure_is_detected() -> None:
    """Orchestration bypassing the public facade into infrastructure."""
    with FixtureGraphScope(
        fixture_dir("invalid_orchestration_imports_infrastructure")
    ) as graph:
        violations = find_facade_violations(graph, FIXTURE_ROOT_PACKAGE)
    assert violations, "orchestration facade violation was not detected"
    violation = violations[0]
    assert violation.source == "fixture_pkg.orchestration.flow"
    assert (
        violation.illegal_target == "fixture_pkg.modules.brief.infrastructure.adapter"
    )
    assert violation.expected_boundary == "fixture_pkg.modules.brief.public"


def test_entrypoint_imports_repository_is_detected() -> None:
    """Entrypoint bypassing the application layer into a repository."""
    with FixtureGraphScope(
        fixture_dir("invalid_entrypoint_imports_repository")
    ) as graph:
        violations = find_facade_violations(graph, FIXTURE_ROOT_PACKAGE)
    assert violations, "entrypoint facade violation was not detected"
    violation = violations[0]
    assert violation.source == "fixture_pkg.entrypoints.api"
    assert (
        violation.illegal_target
        == "fixture_pkg.modules.brief.infrastructure.repository"
    )
    assert violation.expected_boundary == "fixture_pkg.modules.brief.public"
