"""AST-based semantic architecture checks (FND-002).

Import Linter reasons about the import graph; these checks reason about
what the code *does* inside a file. They enforce three accepted rules
(RFC-001-DQ-05, DQ-06, DQ-08) that no import-edge contract can express:

* Core layers (domain / application / skills) must not read the process
  environment or load ``.env`` files — configuration enters through
  bootstrap/platform settings.
* Public contracts must not expose technical implementation types
  (ORM bases and sessions, workflow states, provider SDK types, secrets).
* Skills must respect the skill boundary: no workflow runtime, ORM,
  repository implementation, environment access or spike imports.

Each scanner is deterministic, offline, and works identically on the
production tree (vacuously clean today) and on test-only fixtures.
"""

import ast
from collections.abc import Iterable, Iterator
from pathlib import Path

from helpers.violations import Violation

ENVIRONMENT_RULE = "Core layers must not access the process environment directly"
DOTENV_RULE = "Core layers must not load .env files"
PUBLIC_LEAK_RULE = "Public contracts must not expose technical implementation types"
SKILL_RULE = "Skills must respect the skill boundary"

_ENV_BOUNDARY = (
    "configuration values injected via bootstrap/platform settings "
    "(RFC-001-DQ-06), never os.environ / os.getenv / dotenv"
)
_PUBLIC_BOUNDARY = "technology-neutral data types and protocols only (RFC-001-DQ-08)"
_SKILL_BOUNDARY = (
    "skills prepare and execute through application ports; repository, "
    "transaction, runtime and provider access belong to application and "
    "infrastructure layers (RFC-001-DQ-05)"
)

_FORBIDDEN_PUBLIC_IMPORT_PREFIXES = ("sqlalchemy", "langgraph", "openai", "anthropic")
_FORBIDDEN_PUBLIC_NAME_TOKENS = frozenset(
    {
        "Session",
        "AsyncSession",
        "Engine",
        "DeclarativeBase",
        "StateGraph",
        "CompiledStateGraph",
        "SecretStr",
    }
)
_FORBIDDEN_SKILL_IMPORT_PREFIXES = ("langgraph", "sqlalchemy", "spikes", "prototypes")


def _python_files(scan_base: Path, layer_globs: Iterable[str]) -> list[Path]:
    """Existing source files under the given glob patterns, deduplicated."""
    found: set[Path] = set()
    for pattern in layer_globs:
        found.update(scan_base.glob(pattern))
    return sorted(path for path in found if path.is_file())


def _module_name_for(file: Path, scan_base: Path) -> str:
    """Dotted module name of a source file relative to the scan base."""
    parts = list(file.relative_to(scan_base).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _dotted_name(node: ast.AST) -> str | None:
    """Reconstruct a dotted name from a Name/Attribute chain, if it is one."""
    parts: list[str] = []
    current: ast.AST = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _iter_imported_modules(tree: ast.Module) -> Iterator[str]:
    """Absolute module names imported anywhere in the file."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            yield node.module


def _environment_violations(tree: ast.Module, source: str) -> Iterator[Violation]:
    """Direct os.environ / os.getenv / dotenv usage in one file."""
    reported: set[str] = set()
    for imported in _iter_imported_modules(tree):
        if (
            imported == "dotenv" or imported.startswith("dotenv.")
        ) and "dotenv" not in reported:
            reported.add("dotenv")
            yield Violation(
                rule=DOTENV_RULE,
                source=source,
                illegal_target="dotenv",
                expected_boundary=_ENV_BOUNDARY,
            )
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            call_name = _dotted_name(node.func)
            if call_name == "os.getenv" and "os.getenv" not in reported:
                reported.add("os.getenv")
                yield Violation(
                    rule=ENVIRONMENT_RULE,
                    source=source,
                    illegal_target="os.getenv",
                    expected_boundary=_ENV_BOUNDARY,
                )
        else:
            chain = _dotted_name(node)
            if (
                chain is not None
                and (chain == "os.environ" or chain.startswith("os.environ."))
                and "os.environ" not in reported
            ):
                reported.add("os.environ")
                yield Violation(
                    rule=ENVIRONMENT_RULE,
                    source=source,
                    illegal_target="os.environ",
                    expected_boundary=_ENV_BOUNDARY,
                )


def find_environment_access(
    scan_base: Path, layer_globs: Iterable[str]
) -> list[Violation]:
    """Core-layer files that read the process environment or load .env.

    Missing directories (e.g. no business modules exist yet) yield no
    files and therefore no violations: the rule is live but vacuous until
    real core code lands.
    """
    violations: list[Violation] = []
    for file in _python_files(scan_base, layer_globs):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        source = _module_name_for(file, scan_base)
        violations.extend(_environment_violations(tree, source))
    return sorted(set(violations))


def find_public_contract_leakage(
    scan_base: Path, public_globs: Iterable[str]
) -> list[Violation]:
    """Public contract files exposing technical implementation types."""
    violations: list[Violation] = []
    for file in _python_files(scan_base, public_globs):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        source = _module_name_for(file, scan_base)
        for imported in sorted(set(_iter_imported_modules(tree))):
            if imported.startswith(_FORBIDDEN_PUBLIC_IMPORT_PREFIXES):
                violations.append(
                    Violation(
                        rule=PUBLIC_LEAK_RULE,
                        source=source,
                        illegal_target=f"import {imported}",
                        expected_boundary=_PUBLIC_BOUNDARY,
                    )
                )
        leaked_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in _FORBIDDEN_PUBLIC_NAME_TOKENS:
                leaked_names.add(node.id)
            elif (
                isinstance(node, ast.Attribute)
                and node.attr in _FORBIDDEN_PUBLIC_NAME_TOKENS
            ):
                leaked_names.add(node.attr)
        for name in sorted(leaked_names):
            violations.append(
                Violation(
                    rule=PUBLIC_LEAK_RULE,
                    source=source,
                    illegal_target=f"exposed technical type {name}",
                    expected_boundary=_PUBLIC_BOUNDARY,
                )
            )
    return sorted(set(violations))


def _has_session_parameter(tree: ast.Module) -> bool:
    """Any function parameter annotated with a Session-like type."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for argument in (
                node.args.args + node.args.kwonlyargs + node.args.posonlyargs
            ):
                if argument.annotation is not None:
                    annotation = _dotted_name(argument.annotation)
                    if annotation is not None and "Session" in annotation.split("."):
                        return True
    return False


def find_skill_boundary_violations(
    scan_base: Path, skill_globs: Iterable[str], root_package: str
) -> list[Violation]:
    """Skill files that break the skill boundary (RFC-001-DQ-05)."""
    violations: list[Violation] = []
    infrastructure_prefix = f"{root_package}.modules"
    for file in _python_files(scan_base, skill_globs):
        tree = ast.parse(file.read_text(encoding="utf-8"))
        source = _module_name_for(file, scan_base)
        for imported in sorted(set(_iter_imported_modules(tree))):
            if imported.startswith(_FORBIDDEN_SKILL_IMPORT_PREFIXES):
                violations.append(
                    Violation(
                        rule=SKILL_RULE,
                        source=source,
                        illegal_target=f"import {imported}",
                        expected_boundary=_SKILL_BOUNDARY,
                    )
                )
            elif (
                imported.startswith(infrastructure_prefix)
                and ".infrastructure" in imported
            ):
                violations.append(
                    Violation(
                        rule=SKILL_RULE,
                        source=source,
                        illegal_target=f"import repository implementation {imported}",
                        expected_boundary=_SKILL_BOUNDARY,
                    )
                )
        violations.extend(_environment_violations(tree, source))
        if _has_session_parameter(tree):
            violations.append(
                Violation(
                    rule=SKILL_RULE,
                    source=source,
                    illegal_target="accepts a database Session parameter",
                    expected_boundary=_SKILL_BOUNDARY,
                )
            )
    return sorted(set(violations))
