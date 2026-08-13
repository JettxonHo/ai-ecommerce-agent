"""Architecture boundaries for the private OpenAI Responses outcome mapper."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_SOURCE = _BACKEND / "src"
_PACKAGE = _SOURCE / "ai_ecommerce_agent/platform/model_runtime/openai_responses"
_QWEN_PACKAGE = _SOURCE / "ai_ecommerce_agent/platform/model_runtime/qwen_token_plan"
_FILES = [
    _PACKAGE / "__init__.py",
    _PACKAGE / "_schema_compatibility.py",
    _PACKAGE / "request_preparation.py",
    _PACKAGE / "_response_mapping.py",
    _PACKAGE / "_execution.py",
]

_ALLOWED_STDLIB: dict[str, set[str]] = {
    "__init__.py": {"__future__"},
    "_schema_compatibility.py": {
        "__future__",
        "collections.abc",
        "re",
        "typing",
        "urllib.parse",
    },
    "request_preparation.py": {"__future__", "dataclasses", "enum", "json"},
    "_response_mapping.py": {"__future__", "typing"},
    "_execution.py": {
        "__future__",
        "email.utils",
        "math",
        "random",
        "time",
        "typing",
    },
}
_ALLOWED_ABSOLUTE: dict[str, set[str]] = {
    "__init__.py": set(),
    "_schema_compatibility.py": {"ai_ecommerce_agent.application.model_runtime"},
    "request_preparation.py": {
        "ai_ecommerce_agent.application.model_runtime",
        "ai_ecommerce_agent.shared_kernel",
    },
    "_response_mapping.py": {
        "ai_ecommerce_agent.application.model_runtime",
        "openai",
        "openai.types.responses",
    },
    "_execution.py": {
        "ai_ecommerce_agent.application.model_runtime",
        "openai",
        "openai.types.responses",
        "openai.types.responses.response_create_params",
    },
}
_ALLOWED_RELATIVE: dict[str, set[str]] = {
    "__init__.py": {".request_preparation"},
    "_schema_compatibility.py": set(),
    "request_preparation.py": {"._schema_compatibility"},
    "_response_mapping.py": set(),
    "_execution.py": {"._response_mapping", ".request_preparation"},
}
_ALLOWED_MAPPER_IMPORTS: dict[tuple[str, str], set[tuple[str, str | None]]] = {
    ("import", "openai"): {("openai", "_openai")},
    ("import", "openai.types.responses"): {
        (
            "openai.types.responses",
            "_responses",
        )
    },
    ("import", "ai_ecommerce_agent.application.model_runtime"): {
        ("ai_ecommerce_agent.application.model_runtime", "_contracts")
    },
}
_DATACLASS_CLASSES = {
    "OpenAIResponsesCallParameters",
    "PreparedOpenAIResponsesCall",
}
_FORBIDDEN = (
    "httpx",
    "requests",
    "socket",
    "os",
    "pathlib",
    "subprocess",
    "sqlalchemy",
    "psycopg",
    "langgraph",
    "fastapi",
    "starlette",
)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _imports(tree: ast.Module) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.extend(("absolute", alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            values.append(("relative" if node.level else "absolute", module))
    return values


def _unexpected_imports(path: Path, tree: ast.Module) -> list[str]:
    unexpected: list[str] = []
    for kind, module in _imports(tree):
        if (
            module in _ALLOWED_STDLIB[path.name]
            or module in _ALLOWED_ABSOLUTE[path.name]
        ):
            continue
        if kind == "relative" and module in _ALLOWED_RELATIVE[path.name]:
            continue
        unexpected.append(f"{kind}:{module}")
    if path.name == "_response_mapping.py":
        actual_imports: dict[tuple[str, str], set[tuple[str, str | None]]] = {}
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    key = ("import", alias.name)
                    actual_imports.setdefault(key, set()).add(
                        (alias.name, alias.asname)
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                key = ("from", node.module)
                if key in _ALLOWED_MAPPER_IMPORTS:
                    actual_imports.setdefault(key, set()).update(
                        (alias.name, alias.asname) for alias in node.names
                    )
        for key, expected in _ALLOWED_MAPPER_IMPORTS.items():
            if actual_imports.get(key, set()) != expected:
                unexpected.append(f"symbols:{key[1]}")
    return unexpected


def _import_time_effects(tree: ast.Module) -> tuple[list[ast.Call], list[ast.expr]]:
    calls: list[ast.Call] = []
    decorators: list[ast.expr] = []

    def expression(node: ast.AST) -> None:
        calls.extend(
            candidate for candidate in ast.walk(node) if isinstance(candidate, ast.Call)
        )

    def arguments(node: ast.arguments) -> None:
        values = [
            *(
                argument.annotation
                for argument in (*node.posonlyargs, *node.args, *node.kwonlyargs)
                if argument.annotation
            ),
            *(default for default in (*node.defaults, *node.kw_defaults) if default),
        ]
        if node.vararg and node.vararg.annotation:
            values.append(node.vararg.annotation)
        if node.kwarg and node.kwarg.annotation:
            values.append(node.kwarg.annotation)
        for value in values:
            expression(value)

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorators.extend(node.decorator_list)
            arguments(node.args)
            if node.returns:
                expression(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                if (
                    node.name in _DATACLASS_CLASSES
                    and isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Name)
                    and decorator.func.id == "_dataclass"
                ):
                    nested = [
                        candidate
                        for candidate in ast.walk(decorator)
                        if isinstance(candidate, ast.Call)
                        and candidate is not decorator
                    ]
                    calls.extend(nested)
                else:
                    decorators.append(decorator)
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
        if isinstance(node, (ast.If, ast.While)):
            expression(node.test)
            for child in (*node.body, *node.orelse):
                statement(child)
            return
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                expression(item.context_expr)
                if item.optional_vars:
                    expression(item.optional_vars)
            for child in node.body:
                statement(child)
            return
        if isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                statement(child)
            for handler in node.handlers:
                if handler.type:
                    expression(handler.type)
                for child in handler.body:
                    statement(child)
            return
        expression(node)

    for node in tree.body:
        statement(node)
    return calls, decorators


def _mutable_module_globals(tree: ast.Module) -> list[str]:
    names: list[str] = []

    def target_name(node: ast.AST) -> str | None:
        return node.id if isinstance(node, ast.Name) else None

    def mutable(node: ast.AST) -> bool:
        return isinstance(
            node,
            (
                ast.Call,
                ast.Dict,
                ast.DictComp,
                ast.List,
                ast.ListComp,
                ast.NamedExpr,
                ast.Set,
                ast.SetComp,
            ),
        )

    def expression(node: ast.AST) -> None:
        for candidate in ast.walk(node):
            if isinstance(candidate, ast.NamedExpr) and mutable(candidate.value):
                name = target_name(candidate.target)
                if name and name != "__all__":
                    names.append(name)

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if isinstance(node, ast.Assign) and mutable(node.value):
            for target in node.targets:
                name = target_name(target)
                if name and name != "__all__":
                    names.append(name)
        elif isinstance(node, ast.AnnAssign) and node.value and mutable(node.value):
            name = target_name(node.target)
            if name and name != "__all__":
                names.append(name)
        elif (
            isinstance(node, ast.NamedExpr)
            and node.value is not None
            and mutable(node.value)
        ):
            name = target_name(node.target)
            if name and name != "__all__":
                names.append(name)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            expression(node.iter)
            expression(node.target)
            for child in (*node.body, *node.orelse):
                statement(child)
        elif isinstance(node, (ast.If, ast.While)):
            expression(node.test)
            for child in (*node.body, *node.orelse):
                statement(child)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                expression(item.context_expr)
                if item.optional_vars:
                    expression(item.optional_vars)
            for child in node.body:
                statement(child)
        elif isinstance(node, ast.Try):
            for child in (*node.body, *node.orelse, *node.finalbody):
                statement(child)
            for handler in node.handlers:
                for child in handler.body:
                    statement(child)

    for node in tree.body:
        statement(node)
    return names


def _runtime_provider_violations(tree: ast.Module) -> list[ast.AST]:
    violations: list[ast.AST] = []
    forbidden_calls = {
        "AsyncOpenAI",
        "OpenAI",
        "open",
        "requests.get",
        "responses.create",
        "socket.socket",
        "httpx.Client",
    }

    def dotted(node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = dotted(node.value)
            return f"{parent}.{node.attr}" if parent else None
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            chain = dotted(node)
            if (
                chain
                and chain.startswith("_openai.")
                and chain != "_openai.__version__"
            ):
                violations.append(node)
        elif isinstance(node, ast.Call):
            chain = dotted(node.func)
            if chain in forbidden_calls or (
                chain is not None and chain.startswith("_openai.")
            ):
                violations.append(node)
    return violations


def test_private_mapper_has_exact_path_specific_imports_and_no_public_reexport() -> (
    None
):
    assert sorted(path.name for path in _PACKAGE.glob("*.py")) == [
        "__init__.py",
        "_execution.py",
        "_live_evidence.py",
        "_response_mapping.py",
        "_runtime.py",
        "_schema_compatibility.py",
        "request_preparation.py",
    ]
    for path in _FILES:
        assert _unexpected_imports(path, _tree(path)) == []
    facade_tree = _tree(_PACKAGE / "__init__.py")
    assert ast.literal_eval(facade_tree.body[-1].value) == [  # type: ignore[union-attr]
        "OpenAIReasoningEffort",
        "OpenAIResponsesCallParameters",
        "PreparedOpenAIResponsesCall",
        "prepare_openai_responses_call",
    ]


def _expected_sdk_consumers() -> set[Path]:
    return {
        _PACKAGE / "_response_mapping.py",
        _PACKAGE / "_execution.py",
        _PACKAGE / "_runtime.py",
        _QWEN_PACKAGE / "_response_mapping.py",
        _QWEN_PACKAGE / "_runtime.py",
    }


def _assert_exact_sdk_consumers(consumers: set[Path]) -> None:
    assert consumers == _expected_sdk_consumers()


def test_only_private_mapper_imports_openai_and_no_unauthorized_consumers_exist() -> (
    None
):
    consumers: set[Path] = set()
    for path in _SOURCE.rglob("*.py"):
        if "tests" in path.parts:
            continue
        for kind, module in _imports(_tree(path)):
            if kind == "absolute" and (
                module == "openai" or module.startswith("openai.")
            ):
                consumers.add(path)
    _assert_exact_sdk_consumers(consumers)
    mapper_text = (_PACKAGE / "_response_mapping.py").read_text(encoding="utf-8")
    assert "Client" not in mapper_text
    assert "AsyncOpenAI" not in mapper_text
    assert ".responses.create" not in mapper_text


def test_sdk_consumer_inventory_rejects_one_synthetic_extra_consumer() -> None:
    synthetic = _QWEN_PACKAGE / "_synthetic_provider_consumer.py"
    with pytest.raises(AssertionError):
        _assert_exact_sdk_consumers(_expected_sdk_consumers() | {synthetic})


def test_import_time_effects_and_mutable_globals_are_absent() -> None:
    for path in _FILES:
        calls, decorators = _import_time_effects(_tree(path))
        assert calls == []
        assert decorators == []
        assert _mutable_module_globals(_tree(path)) == []


def test_provider_mapper_runtime_access_is_read_only_and_local() -> None:
    assert _runtime_provider_violations(_tree(_PACKAGE / "_response_mapping.py")) == []


@pytest.mark.parametrize(
    "mutation",
    [
        "class Bad:\n    value = open('x')",
        "@print\ndef leaked():\n    pass",
        "def leaked(value=open('x')):\n    pass",
        "def leaked(value: open('x')):\n    pass",
        "def leaked() -> open('x'):\n    pass",
        "_CACHE = []",
        "if (_CACHE := []):\n    pass",
    ],
)
def test_single_import_time_or_global_mutation_is_detectable(mutation: str) -> None:
    baseline = """\
from __future__ import annotations
from typing import Any
def map_value(value: Any) -> str:
    return str(value)
__all__ = []
"""
    baseline_tree = ast.parse(baseline)
    assert _import_time_effects(baseline_tree) == ([], [])
    assert _mutable_module_globals(baseline_tree) == []
    mutated = ast.parse(baseline + "\n" + mutation)
    calls, decorators = _import_time_effects(mutated)
    assert calls or decorators or _mutable_module_globals(mutated)


@pytest.mark.parametrize(
    "mutation",
    [
        "def leaked():\n    return _openai.OpenAI()",
        "def leaked():\n    return _openai.AsyncOpenAI()",
        "def leaked():\n    return _openai.responses.create()",
        "def leaked():\n    return responses.create()",
        "def leaked():\n    return open('x')",
        "def leaked():\n    return socket.socket()",
        "def leaked():\n    return httpx.Client()",
    ],
)
def test_provider_runtime_probes_reject_one_call_mutation(mutation: str) -> None:
    baseline = """\
from __future__ import annotations
import openai as _openai
def map_value() -> str:
    return _openai.__version__
"""
    assert _runtime_provider_violations(ast.parse(baseline)) == []
    assert _runtime_provider_violations(ast.parse(baseline + "\n" + mutation))


@pytest.mark.parametrize(
    ("filename", "source"),
    [
        ("_response_mapping.py", "from openai import OpenAI"),
        ("request_preparation.py", "import openai"),
        ("_schema_compatibility.py", "import json"),
    ],
)
def test_path_specific_import_mutations_are_rejected(
    filename: str, source: str
) -> None:
    assert _unexpected_imports(_PACKAGE / filename, ast.parse(source))
