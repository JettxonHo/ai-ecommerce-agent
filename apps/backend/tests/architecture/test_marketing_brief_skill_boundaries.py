"""Architecture evidence for the Marketing Brief output-only seam."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_SRC = _BACKEND / "src/ai_ecommerce_agent"
_PACKAGE = _SRC / "modules/marketing_brief"
_GENERATION = _PACKAGE / "application/skills/marketing_brief_generation"
_OUTPUT = _GENERATION / "output_contract.py"
_FILES = [
    _PACKAGE / "application/__init__.py",
    _PACKAGE / "application/skills/__init__.py",
    _GENERATION / "__init__.py",
    _OUTPUT,
]
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
    "product_positioning",
    "human_review",
    "fragment",
    "evidence",
    "brief",
    "pathlib",
    "os",
    "socket",
    "requests",
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _imports(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.append("." * node.level + (node.module or ""))
    return names


def _relative_targets(path: Path, node: ast.ImportFrom) -> list[Path]:
    base = path.parent
    for _ in range(max(0, node.level - 1)):
        base = base.parent
    if node.module:
        target = base.joinpath(*node.module.split("."))
        return [target.with_suffix(".py"), target / "__init__.py"]
    targets = [base / alias.name for alias in node.names]
    return [target.with_suffix(".py") for target in targets] + [
        target / "__init__.py" for target in targets
    ]


def _consumer_violations(path: Path, tree: ast.Module) -> list[str]:
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any("marketing_brief" in alias.name for alias in node.names):
                violations.append(f"{path}:import")
            continue
        if not isinstance(node, ast.ImportFrom):
            continue
        imported = "." * node.level + (node.module or "")
        aliases = {alias.name for alias in node.names}
        targets = _relative_targets(path, node) if node.level else []
        targets_output = _OUTPUT in targets
        allowed_facade_import = (
            path == _GENERATION / "__init__.py"
            and node.level == 1
            and (
                node.module == "output_contract"
                or (node.module is None and aliases == {"output_contract"})
            )
            and targets_output
        )
        if allowed_facade_import:
            continue
        if (
            "marketing_brief" in imported
            or "marketing_brief" in aliases
            or targets_output
        ):
            violations.append(f"{path}:{imported}")
    return violations


def _import_time_effects(tree: ast.Module) -> tuple[list[ast.Call], list[ast.expr]]:
    calls: list[ast.Call] = []
    decorators: list[ast.expr] = []

    def expression(node: ast.AST) -> None:
        calls.extend(item for item in ast.walk(node) if isinstance(item, ast.Call))

    def decorator_list(values: list[ast.expr]) -> None:
        for value in values:
            if isinstance(value, ast.Call):
                expression(value)
            else:
                decorators.append(value)

    def arguments(values: ast.arguments) -> None:
        for argument in (
            *values.posonlyargs,
            *values.args,
            *values.kwonlyargs,
        ):
            if argument.annotation is not None:
                expression(argument.annotation)
        if values.vararg and values.vararg.annotation:
            expression(values.vararg.annotation)
        if values.kwarg and values.kwarg.annotation:
            expression(values.kwarg.annotation)
        for default in (*values.defaults, *values.kw_defaults):
            if default is not None:
                expression(default)

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorator_list(node.decorator_list)
            arguments(node.args)
            if node.returns is not None:
                expression(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            decorator_list(node.decorator_list)
            for base in node.bases:
                expression(base)
            for keyword in node.keywords:
                expression(keyword.value)
            for child in node.body:
                statement(child)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
            expression(node.iter)
            expression(node.target)
            for child in (*node.body, *node.orelse):
                statement(child)
            return
        if isinstance(node, ast.While):
            expression(node.test)
            for child in (*node.body, *node.orelse):
                statement(child)
            return
        if isinstance(node, ast.If):
            expression(node.test)
            for child in (*node.body, *node.orelse):
                statement(child)
            return
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                expression(item.context_expr)
                if item.optional_vars is not None:
                    expression(item.optional_vars)
            for child in node.body:
                statement(child)
            return
        if isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                statement(child)
            for handler in node.handlers:
                if handler.type is not None:
                    expression(handler.type)
                for child in handler.body:
                    statement(child)
            return
        expression(node)

    for node in tree.body:
        statement(node)
    return calls, decorators


def _mutable_globals(tree: ast.Module) -> list[ast.AST]:
    mutable: list[ast.AST] = []

    def names(target: ast.AST) -> set[str]:
        if isinstance(target, ast.Name):
            return {target.id}
        if isinstance(target, (ast.Tuple, ast.List)):
            return {name for item in target.elts for name in names(item)}
        return set()

    def mutable_value(value: ast.AST) -> bool:
        return isinstance(
            value,
            (ast.List, ast.ListComp, ast.Dict, ast.DictComp, ast.Set, ast.SetComp),
        )

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                statement(child)
            return
        if isinstance(node, ast.Assign):
            if mutable_value(node.value) and not any(
                name == "__all__" for target in node.targets for name in names(target)
            ):
                mutable.append(node)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if mutable_value(node.value) and names(node.target) != {"__all__"}:
                mutable.append(node)
        children: tuple[ast.stmt, ...] = ()
        if isinstance(
            node, (ast.For, ast.AsyncFor, ast.While, ast.If, ast.With, ast.AsyncWith)
        ):
            children = tuple(node.body) + tuple(getattr(node, "orelse", ()))
        elif isinstance(node, ast.Try):
            children = tuple(node.body) + tuple(node.orelse) + tuple(node.finalbody)
            for handler in node.handlers:
                children += tuple(handler.body)
        for child in children:
            statement(child)

    for node in tree.body:
        statement(node)
    return mutable


def test_exact_new_file_inventory_and_imports() -> None:
    assert all(path.is_file() for path in _FILES)
    for path in _FILES:
        for imported in _imports(_tree(path)):
            assert imported in _ALLOWED_IMPORTS, (path, imported)
            if imported.startswith("ai_ecommerce_agent."):
                assert not any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for forbidden in _FORBIDDEN
                )
            else:
                assert not any(part in _FORBIDDEN for part in imported.split("."))


def test_repository_has_only_generation_facade_as_output_consumer() -> None:
    violations: list[str] = []
    for path in _SRC.rglob("*.py"):
        violations.extend(_consumer_violations(path, _tree(path)))
    assert violations == []


def test_consumer_guard_rejects_unauthorized_sibling_and_allows_facade() -> None:
    facade = _GENERATION / "__init__.py"
    assert not _consumer_violations(
        facade,
        ast.parse(
            "from .output_contract import marketing_brief_candidate_output_spec\n"
        ),
    )
    assert not _consumer_violations(
        facade, ast.parse("from . import output_contract\n")
    )
    sibling = _GENERATION / "sibling.py"
    for source in (
        "from .output_contract import marketing_brief_candidate_output_spec\n",
        "from . import output_contract\n",
        (
            "from ai_ecommerce_agent.modules.marketing_brief.application.skills."
            "marketing_brief_generation import marketing_brief_candidate_output_spec\n"
        ),
    ):
        assert _consumer_violations(sibling, ast.parse(source))


def test_no_import_time_effects_or_mutable_globals() -> None:
    for path in _FILES:
        calls, decorators = _import_time_effects(_tree(path))
        assert not calls, path
        assert not decorators, path
        assert not _mutable_globals(_tree(path)), path


def test_import_time_guard_has_production_shaped_single_mutations() -> None:
    baseline = ast.parse(
        "from enum import StrEnum\n"
        "class Contract(StrEnum):\n"
        "    VALUE = 'value'\n"
        "def build(value: str = 'value') -> str:\n"
        "    return value\n"
    )
    calls, decorators = _import_time_effects(baseline)
    assert not calls and not decorators
    for source in (
        "def build(value=print()):\n    return value\n",
        "@print\ndef build():\n    return 'value'\n",
        "def build(value: factory()):\n    return value\n",
        "def build() -> factory():\n    return 'value'\n",
        "class Contract(factory()):\n    pass\n",
        "if True:\n    _cache = []\n",
    ):
        calls, decorators = _import_time_effects(ast.parse(source))
        mutable = _mutable_globals(ast.parse(source))
        assert calls or decorators or mutable
