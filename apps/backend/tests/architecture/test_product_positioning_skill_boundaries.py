"""Architecture boundaries for the Product Positioning output-only seam."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_SRC = _BACKEND / "src/ai_ecommerce_agent"
_PACKAGE = _SRC / "modules/product_positioning"
_FILES = [
    _PACKAGE / "__init__.py",
    _PACKAGE / "application/__init__.py",
    _PACKAGE / "application/skills/__init__.py",
    _PACKAGE / "application/skills/product_positioning/__init__.py",
    _PACKAGE / "application/skills/product_positioning/output_contract.py",
]
_FACADE = _PACKAGE / "application/skills/product_positioning/__init__.py"
_ALLOWED_IMPORTS = {
    "__future__",
    "collections.abc",
    "enum",
    "typing",
    "ai_ecommerce_agent.application.model_runtime",
    "ai_ecommerce_agent.shared_kernel.structured_content",
    ".output_contract",
}
_FORBIDDEN = {
    "openai",
    "langgraph",
    "sqlalchemy",
    "psycopg",
    "repository",
    "uow",
    "source_evidence",
    "product_intake",
    "customer_insight",
    "fragment",
    "evidence",
    "review",
    "brief",
    "pathlib",
    "os",
    "socket",
    "requests",
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _import_names(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.append("." * node.level + (node.module or ""))
    return names


def _positioning_consumer_violations(path: Path, tree: ast.Module) -> list[str]:
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "product_positioning" in alias.name:
                    violations.append(f"{path}:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            imported = "." * node.level + (node.module or "")
            if path == _FACADE and imported == ".output_contract":
                continue
            if "product_positioning" in imported:
                violations.append(f"{path}:{imported}")
    return violations


def _import_time_effects(tree: ast.Module) -> tuple[list[ast.Call], list[ast.expr]]:
    calls: list[ast.Call] = []
    bare_decorators: list[ast.expr] = []

    def scan_expression(node: ast.AST) -> None:
        calls.extend(item for item in ast.walk(node) if isinstance(item, ast.Call))

    def scan_decorators(decorators: list[ast.expr]) -> None:
        for decorator in decorators:
            if isinstance(decorator, ast.Call):
                scan_expression(decorator)
            else:
                bare_decorators.append(decorator)

    def scan_arguments(arguments: ast.arguments) -> None:
        for argument in (
            *arguments.posonlyargs,
            *arguments.args,
            *arguments.kwonlyargs,
        ):
            if argument.annotation is not None:
                scan_expression(argument.annotation)
        if arguments.vararg and arguments.vararg.annotation:
            scan_expression(arguments.vararg.annotation)
        if arguments.kwarg and arguments.kwarg.annotation:
            scan_expression(arguments.kwarg.annotation)
        for default in (*arguments.defaults, *arguments.kw_defaults):
            if default is not None:
                scan_expression(default)

    def scan_statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scan_decorators(node.decorator_list)
            scan_arguments(node.args)
            if node.returns is not None:
                scan_expression(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            scan_decorators(node.decorator_list)
            for base in node.bases:
                scan_expression(base)
            for keyword in node.keywords:
                scan_expression(keyword.value)
            for child in node.body:
                scan_statement(child)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            scan_expression(node.iter)
            scan_expression(node.target)
            for child in (*node.body, *node.orelse):
                scan_statement(child)
            return
        if isinstance(node, ast.While):
            scan_expression(node.test)
            for child in (*node.body, *node.orelse):
                scan_statement(child)
            return
        if isinstance(node, ast.If):
            scan_expression(node.test)
            for child in (*node.body, *node.orelse):
                scan_statement(child)
            return
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                scan_expression(item.context_expr)
                if item.optional_vars is not None:
                    scan_expression(item.optional_vars)
            for child in node.body:
                scan_statement(child)
            return
        if isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                scan_statement(child)
            for handler in node.handlers:
                if handler.type is not None:
                    scan_expression(handler.type)
                for child in handler.body:
                    scan_statement(child)
            return
        scan_expression(node)

    for statement in tree.body:
        scan_statement(statement)
    return calls, bare_decorators


def _mutable_module_assignments(tree: ast.Module) -> list[ast.AST]:
    mutable: list[ast.AST] = []

    def target_names(target: ast.AST) -> set[str]:
        if isinstance(target, ast.Name):
            return {target.id}
        if isinstance(target, (ast.Tuple, ast.List)):
            return {name for item in target.elts for name in target_names(item)}
        return set()

    def is_mutable(value: ast.AST) -> bool:
        return isinstance(
            value,
            (ast.List, ast.ListComp, ast.Dict, ast.DictComp, ast.Set, ast.SetComp),
        )

    def scan_statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                scan_statement(child)
            return
        if isinstance(node, ast.Assign):
            if is_mutable(node.value) and not any(
                name == "__all__"
                for target in node.targets
                for name in target_names(target)
            ):
                mutable.append(node)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if is_mutable(node.value) and target_names(node.target) != {"__all__"}:
                mutable.append(node)
        if isinstance(node, (ast.For, ast.AsyncFor)):
            for child in (*node.body, *node.orelse):
                scan_statement(child)
        elif isinstance(node, ast.While):
            for child in (*node.body, *node.orelse):
                scan_statement(child)
        elif isinstance(node, ast.If):
            for child in (*node.body, *node.orelse):
                scan_statement(child)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for child in node.body:
                scan_statement(child)
        elif isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                scan_statement(child)
            for handler in node.handlers:
                for child in handler.body:
                    scan_statement(child)

    for statement in tree.body:
        scan_statement(statement)
    return mutable


def test_exact_allowlisted_files_and_imports() -> None:
    assert all(path.is_file() for path in _FILES)
    for path in _FILES:
        tree = _tree(path)
        for imported in _import_names(tree):
            assert imported in _ALLOWED_IMPORTS, (path.name, imported)
            if imported.startswith("ai_ecommerce_agent."):
                assert not any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for forbidden in _FORBIDDEN
                )
            else:
                assert not any(part in _FORBIDDEN for part in imported.split("."))


def test_repository_has_only_the_private_facade_seam_owner_and_consumer() -> None:
    violations: list[str] = []
    for path in _SRC.rglob("*.py"):
        violations.extend(_positioning_consumer_violations(path, _tree(path)))
    assert violations == []


def test_repository_consumer_guard_rejects_an_unauthorized_production_import() -> None:
    baseline = ast.parse(
        "from enum import StrEnum\nclass OtherContract(StrEnum):\n    VALUE = 'value'\n"
    )
    assert _positioning_consumer_violations(_SRC / "modules/other.py", baseline) == []
    mutation = ast.parse(
        "from ai_ecommerce_agent.modules.product_positioning.application.skills "
        "import product_positioning\n"
    )
    assert _positioning_consumer_violations(_SRC / "modules/other.py", mutation)


def test_no_import_time_calls_or_mutable_module_globals() -> None:
    for path in _FILES:
        tree = _tree(path)
        calls, bare_decorators = _import_time_effects(tree)
        assert not calls, path
        assert not bare_decorators, path
        assert not _mutable_module_assignments(tree), path


def test_production_shaped_single_mutation_probe_catches_forbidden_import() -> None:
    baseline = ast.parse(
        "from enum import StrEnum\n"
        "from ai_ecommerce_agent.application.model_runtime import "
        "StructuredOutputSpec\n"
    )
    mutation = ast.parse("import openai\n")
    assert all(name not in _FORBIDDEN for name in _import_names(baseline))
    assert any(name == "openai" for name in _import_names(mutation))


def test_import_time_guard_rejects_metadata_effect_mutations() -> None:
    baseline = ast.parse(
        "from enum import StrEnum\n"
        "class Contract(StrEnum):\n"
        "    VALUE = 'value'\n"
        "def build(value: str = 'value') -> str:\n"
        "    return value\n"
    )
    baseline_calls, baseline_decorators = _import_time_effects(baseline)
    assert not baseline_calls
    assert not baseline_decorators
    mutations = [
        ast.parse("def build(value=print()):\n    return value\n"),
        ast.parse("@print\ndef build():\n    return 'value'\n"),
        ast.parse("def build(value: factory()):\n    return value\n"),
        ast.parse("def build() -> factory():\n    return 'value'\n"),
        ast.parse("class Contract(factory()):\n    pass\n"),
        ast.parse("class Contract(metaclass=factory()):\n    pass\n"),
    ]
    for mutation in mutations:
        calls, decorators = _import_time_effects(mutation)
        assert calls or decorators


def test_mutable_global_guard_rejects_module_and_control_scope_mutations() -> None:
    baseline = ast.parse(
        "__all__ = ['build']\nif True:\n    pass\nclass Contract:\n    pass\n"
    )
    assert not _mutable_module_assignments(baseline)
    mutations = [
        ast.parse("_cache = []\n"),
        ast.parse("_cache: list[object] = []\n"),
        ast.parse("if True:\n    _cache = {}\n"),
        ast.parse("class Contract:\n    _cache = {1}\n"),
        ast.parse("try:\n    _cache = [1]\nexcept Exception:\n    pass\n"),
    ]
    for mutation in mutations:
        assert _mutable_module_assignments(mutation)
