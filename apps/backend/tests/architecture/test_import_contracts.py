"""Import Linter contract verification (FND-002).

Runs the fixture contract suite (a one-to-one mirror of the production
contracts, rooted at ``fixture_pkg``) against positive and negative
fixtures, and asserts the mirror stays in sync with production.

Positive fixtures prove the contracts never reject legal architecture;
negative fixtures prove each contract really executes, finds the fixture,
and fails for the target rule with source and target in the report —
never through a configuration or path error.
"""

import configparser
import tomllib
from pathlib import Path

import pytest
from helpers.lint_runner import (
    FIXTURE_CONTRACTS_CONFIG,
    assert_contract_broken,
    assert_contracts_kept,
    fixture_dir,
    run_lint_imports,
)

pytestmark = pytest.mark.architecture

PRODUCTION_PYPROJECT: Path = Path(__file__).resolve().parents[2] / "pyproject.toml"

_VALID_FIXTURES = (
    "valid_layered_package",
    "valid_public_facade_dependency",
    "valid_shared_kernel_dependency",
    "valid_orchestration_dependency",
)


def test_fixture_contract_suite_mirrors_production_contracts() -> None:
    """Fixture evidence is only valid while it tests the real contract set."""
    production = tomllib.loads(PRODUCTION_PYPROJECT.read_text(encoding="utf-8"))
    production_contracts = {
        (contract["name"], contract["type"])
        for contract in production["tool"]["importlinter"]["contracts"]
    }
    parser = configparser.ConfigParser()
    read_files = parser.read(FIXTURE_CONTRACTS_CONFIG, encoding="utf-8")
    assert read_files, f"fixture contract config not found: {FIXTURE_CONTRACTS_CONFIG}"
    fixture_contracts = {
        (parser[section]["name"], parser[section]["type"])
        for section in parser.sections()
        if section.startswith("importlinter:contract:")
    }
    assert fixture_contracts == production_contracts


@pytest.mark.parametrize("fixture_name", _VALID_FIXTURES)
def test_valid_fixture_keeps_all_contracts(fixture_name: str) -> None:
    """Legal architecture must never be rejected (no over-enforcement)."""
    assert_contracts_kept(run_lint_imports(fixture_dir(fixture_name)))


def test_domain_imports_infrastructure_is_rejected() -> None:
    """Rule: Domain -X-> Infrastructure (same module, upward)."""
    result = run_lint_imports(fixture_dir("invalid_domain_imports_infrastructure"))
    assert_contract_broken(
        result,
        "Module layer direction",
        expected_fragments=(
            "fixture_pkg.modules.brief.domain",
            "fixture_pkg.modules.brief.infrastructure",
        ),
    )


def test_application_imports_adapter_is_rejected() -> None:
    """Rule: Application -X-> Infrastructure implementation (upward)."""
    result = run_lint_imports(fixture_dir("invalid_application_imports_adapter"))
    assert_contract_broken(
        result,
        "Module layer direction",
        expected_fragments=(
            "fixture_pkg.modules.brief.application",
            "fixture_pkg.modules.brief.infrastructure",
        ),
    )


def test_shared_kernel_business_dependency_is_rejected() -> None:
    """Rule: Shared kernel -X-> business modules (upward)."""
    result = run_lint_imports(fixture_dir("invalid_shared_kernel_dependency"))
    assert_contract_broken(
        result,
        "Top-level package direction",
        expected_fragments=(
            "fixture_pkg.shared_kernel",
            "fixture_pkg.modules",
        ),
    )


def test_production_spike_import_is_rejected() -> None:
    """Rule: production -X-> spikes/prototypes (even when unresolvable)."""
    result = run_lint_imports(fixture_dir("invalid_production_imports_spike"))
    assert_contract_broken(
        result,
        "Production and Spike isolation",
        expected_fragments=("fixture_pkg.service", "spikes"),
    )
