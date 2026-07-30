"""Module dependency DAG verification (FND-002, RFC-001-DQ-08).

Business modules must form a directed acyclic graph at module level —
including cycles formed through public facades, which Python's file-level
circular-import detection never reports. Import Linter's ``acyclic_siblings``
contract hard-errors while the ``modules`` package does not exist yet, so
this rule runs as a custom check on the grimp graph until real modules land.
"""

import pytest
from helpers.lint_runner import fixture_dir
from helpers.module_graph import (
    FIXTURE_ROOT_PACKAGE,
    PRODUCTION_ROOT_PACKAGE,
    FixtureGraphScope,
    build_production_graph,
)
from helpers.rules import DAG_RULE, find_module_cycles, find_witness_chain
from helpers.violations import render_all

pytestmark = pytest.mark.architecture


def test_production_module_graph_is_acyclic() -> None:
    """Vacuous today (no business modules yet) and live from the first two."""
    violations = find_module_cycles(build_production_graph(), PRODUCTION_ROOT_PACKAGE)
    assert violations == [], render_all(violations)


def test_one_way_module_dependency_is_legal() -> None:
    """beta -> alpha through public facades, with no return edge: no cycle."""
    with FixtureGraphScope(fixture_dir("valid_public_facade_dependency")) as graph:
        violations = find_module_cycles(graph, FIXTURE_ROOT_PACKAGE)
    assert violations == [], render_all(violations)


def test_module_cycle_through_public_facades_is_detected() -> None:
    """alpha.public <-> beta.public is a module-level cycle and must fail.

    This is precisely the case file-level circular-import detection misses:
    every import goes through a legal public facade, yet the modules form a
    cycle. The check must report both directions with witness chains.
    """
    with FixtureGraphScope(fixture_dir("invalid_module_dependency_cycle")) as graph:
        violations = find_module_cycles(graph, FIXTURE_ROOT_PACKAGE)
        assert violations, "module dependency cycle was not detected"
        violation = violations[0]
        assert violation.rule == DAG_RULE
        assert {violation.source, violation.illegal_target} == {
            "fixture_pkg.modules.alpha",
            "fixture_pkg.modules.beta",
        }
        assert "Rule: " in violation.render()
        assert "Expected Boundary: " in violation.render()
        forward = find_witness_chain(graph, violation.source, violation.illegal_target)
        backward = find_witness_chain(graph, violation.illegal_target, violation.source)
    assert forward, "no witness chain for the forward direction"
    assert backward, "no witness chain for the backward direction"
    assert forward[0].startswith("fixture_pkg.modules")
    assert backward[0].startswith("fixture_pkg.modules")
