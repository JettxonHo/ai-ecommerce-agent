"""Graph-level architecture rules Import Linter cannot express (FND-002).

Two accepted rules need same-module-relative reasoning:

* **Public facade** (RFC-001-DQ-08): anything outside a business module may
  only reach into that module through ``modules.<module>.public``. The
  composition root is the one accepted exception: ``<root>.bootstrap`` may
  bind that module's Application Port to its concrete Application service and
  Infrastructure implementation, as required by RFC-001 DQ-06. It may not
  reach into the module Domain or any other private layer.
* **Module dependency DAG** (RFC-001-DQ-08): business modules must form a
  directed acyclic graph, including cycles formed *through* public facades
  (which Python's file-level circular-import detection never reports).
  Import Linter's ``acyclic_siblings`` contract hard-errors while the
  ``modules`` package does not exist yet, so the rule lives here until the
  first real module lands (then either checker may carry it).

Both rules evaluate the grimp graph — the same engine Import Linter uses.
"""

import grimp

from helpers.violations import Violation

FACADE_RULE = "Cross-module imports must use the public facade"
DAG_RULE = "Business module dependencies must form a directed acyclic graph"


def module_siblings(graph: grimp.ImportGraph, root: str) -> list[str]:
    """Business module containers under ``<root>.modules`` (sorted)."""
    modules_root = f"{root}.modules"
    if modules_root not in graph.modules:
        return []
    return sorted(graph.find_children(modules_root))


def find_facade_violations(graph: grimp.ImportGraph, root: str) -> list[Violation]:
    """Find imports that reach into a module without going through public.

    An edge ``importer -> imported`` violates the rule when ``imported``
    lives inside some module ``modules.<target>`` but outside its
    ``public`` facade, and ``importer`` does not belong to that same
    module. Same-module imports (any layer to any layer) are governed by
    the layer-direction contract instead, never by this rule.
    """
    violations: list[Violation] = []
    for target_module in module_siblings(graph, root):
        public_facade = f"{target_module}.public"
        for module in sorted(graph.modules):
            if not module.startswith(root):
                continue
            bootstrap_source = module == f"{root}.bootstrap" or module.startswith(
                f"{root}.bootstrap."
            )
            if module == target_module or module.startswith(f"{target_module}."):
                continue  # same module: layer contract's jurisdiction
            for imported in sorted(graph.find_modules_directly_imported_by(module)):
                inside_target = imported == target_module or imported.startswith(
                    f"{target_module}."
                )
                through_facade = imported == public_facade or imported.startswith(
                    f"{public_facade}."
                )
                bootstrap_infrastructure = bootstrap_source and (
                    imported == f"{target_module}.infrastructure"
                    or imported.startswith(f"{target_module}.infrastructure.")
                )
                bootstrap_application = bootstrap_source and (
                    imported == f"{target_module}.application"
                    or imported.startswith(f"{target_module}.application.")
                )
                if (
                    inside_target
                    and not through_facade
                    and not bootstrap_infrastructure
                    and not bootstrap_application
                ):
                    violations.append(
                        Violation(
                            rule=FACADE_RULE,
                            source=module,
                            illegal_target=imported,
                            expected_boundary=public_facade,
                        )
                    )
    return violations


def _module_depends_on(
    graph: grimp.ImportGraph, upstream: str, downstream: str
) -> bool:
    """True when anything inside ``upstream`` imports anything inside ``downstream``."""
    downstream_modules = graph.find_descendants(downstream) | {downstream}
    upstream_modules = graph.find_descendants(upstream) | {upstream}
    for module in upstream_modules:
        if graph.find_downstream_modules(module) & downstream_modules:
            return True
    return False


def find_witness_chain(
    graph: grimp.ImportGraph, upstream: str, downstream: str
) -> tuple[str, ...] | None:
    """One concrete import chain witnessing ``upstream -> downstream``."""
    downstream_modules = sorted(graph.find_descendants(downstream) | {downstream})
    for module in sorted(graph.find_descendants(upstream) | {upstream}):
        for target in downstream_modules:
            chain = graph.find_shortest_chain(module, target)
            if chain:
                return tuple(chain)
    return None


def find_module_cycles(graph: grimp.ImportGraph, root: str) -> list[Violation]:
    """Find module-level dependency cycles, however they are formed.

    Detects cycles through public facades too: each unordered pair of
    business modules is checked in both directions on the transitive
    module-level dependency relation, not on file-level imports.
    """
    violations: list[Violation] = []
    siblings = module_siblings(graph, root)
    for index, module_a in enumerate(siblings):
        for module_b in siblings[index + 1 :]:
            if _module_depends_on(graph, module_a, module_b) and _module_depends_on(
                graph, module_b, module_a
            ):
                violations.append(
                    Violation(
                        rule=DAG_RULE,
                        source=module_a,
                        illegal_target=module_b,
                        expected_boundary=(
                            "one-way module dependency, or coordination through "
                            f"{root}.orchestration"
                        ),
                    )
                )
    return violations
