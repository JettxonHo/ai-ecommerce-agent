"""Import-graph loading for architecture tests (FND-002).

Uses ``grimp``, the same graph engine Import Linter runs on, so the custom
graph rules (public facade, module DAG) evaluate the identical import data
as the Import Linter contracts — one graph, no divergent source of truth.
"""

import sys
from pathlib import Path
from types import TracebackType

import grimp

PRODUCTION_ROOT_PACKAGE = "ai_ecommerce_agent"
FIXTURE_ROOT_PACKAGE = "fixture_pkg"


def build_production_graph() -> grimp.ImportGraph:
    """Build the import graph of the installed production package."""
    graph: grimp.ImportGraph = grimp.build_graph(PRODUCTION_ROOT_PACKAGE)
    return graph


class FixtureGraphScope:
    """Scope that builds a fixture's import graph in isolation.

    The fixture directory is placed on ``sys.path`` only for the duration
    of the scope; grimp analyzes sources statically (it does not import
    fixture modules), and the path entry is removed on exit so fixtures
    can never leak into later tests.

    Usage::

        with fixture_graph(fixture_dir("valid_layered_package")) as graph:
            ...
    """

    def __init__(self, fixture_dir_path: Path) -> None:
        self._target = str(fixture_dir_path)
        assert (fixture_dir_path / FIXTURE_ROOT_PACKAGE).is_dir(), (
            f"fixture has no {FIXTURE_ROOT_PACKAGE} package: {fixture_dir_path}"
        )

    def __enter__(self) -> grimp.ImportGraph:
        sys.path.insert(0, self._target)
        graph: grimp.ImportGraph = grimp.build_graph(FIXTURE_ROOT_PACKAGE)
        return graph

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        sys.path.remove(self._target)
