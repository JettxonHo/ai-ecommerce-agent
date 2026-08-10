"""Architecture checks for the private single-attempt OpenAI executor."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_SOURCE = _BACKEND / "src"
_PACKAGE = _SOURCE / "ai_ecommerce_agent/platform/model_runtime/openai_responses"
_EXECUTION = _PACKAGE / "_execution.py"
_PRODUCTION_FILES = [
    _PACKAGE / "__init__.py",
    _PACKAGE / "_schema_compatibility.py",
    _PACKAGE / "request_preparation.py",
    _PACKAGE / "_response_mapping.py",
    _EXECUTION,
]

_ALLOWED_STDLIB = {
    "__future__",
    "email.utils",
    "math",
    "random",
    "time",
    "typing",
}
_ALLOWED_ABSOLUTE = {
    "ai_ecommerce_agent.application.model_runtime",
    "ai_ecommerce_agent.platform.model_runtime.openai_responses._response_mapping",
    "ai_ecommerce_agent.platform.model_runtime.openai_responses.request_preparation",
    "openai",
    "openai.types.responses",
    "openai.types.responses.response_create_params",
}
_ALLOWED_RELATIVE: dict[str, set[str]] = {
    "__init__.py": {".request_preparation"},
    "_schema_compatibility.py": set(),
    "request_preparation.py": {"._schema_compatibility"},
    "_response_mapping.py": set(),
    "_execution.py": {"._response_mapping", ".request_preparation"},
}
_FORBIDDEN_NAMES = {
    "AsyncOpenAI",
    "OpenAI",
    "Client",
    "AsyncClient",
    "with_options",
    "sleep",
    "retry",
    "backoff",
    "create",
    "socket",
    "requests",
    "httpx",
    "open",
    "logging",
    "print",
}
_ALLOWED_OPENAI_ATTRIBUTES = {
    "OpenAI",
    "OpenAIError",
    "APIError",
    "APIStatusError",
    "APIResponseValidationError",
    "APITimeoutError",
    "APIConnectionError",
    "__version__",
}


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _imports(tree: ast.Module) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.extend(("absolute", alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            values.append(
                (
                    "relative" if node.level else "absolute",
                    "." * node.level + (node.module or ""),
                )
            )
    return values


def _import_bindings(tree: ast.Module) -> list[tuple[str, str, str, str | None]]:
    values: list[tuple[str, str, str, str | None]] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            values.extend(
                ("import", alias.name, "", alias.asname) for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            values.extend(
                ("from", module, alias.name, alias.asname) for alias in node.names
            )
    return values


_EXPECTED_EXECUTION_IMPORTS = [
    ("from", "__future__", "annotations", None),
    ("from", "email.utils", "parsedate_to_datetime", None),
    ("from", "math", "isfinite", None),
    ("from", "random", "random", None),
    ("from", "time", "monotonic", None),
    ("from", "time", "sleep", None),
    ("from", "time", "time", None),
    ("from", "typing", "cast", None),
    ("import", "openai", "", "_openai"),
    ("import", "openai.types.responses", "", "_responses"),
    ("import", "openai.types.responses.response_create_params", "", "_response_params"),
    ("import", "ai_ecommerce_agent.application.model_runtime", "", "_contracts"),
    (
        "from",
        "._response_mapping",
        "map_openai_responses_response",
        None,
    ),
    (
        "from",
        ".request_preparation",
        "OpenAIResponsesCallParameters",
        None,
    ),
    (
        "from",
        ".request_preparation",
        "prepare_openai_responses_call",
        None,
    ),
]


def _dotted(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _dotted(node.value)
        return f"{parent}.{node.attr}" if parent else None
    return None


def _controlled_call_owners(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    controlled = {
        "monotonic",
        "isfinite",
        "parsedate_to_datetime",
        "random",
        "sleep",
        "time",
    }
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }

    def owner(node: ast.AST) -> str:
        names: list[str] = []
        parent = parents.get(node)
        while parent is not None:
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.append(parent.name)
            parent = parents.get(parent)
        return ".".join(reversed(names)) or "<module>"

    values: dict[str, list[str]] = {name: [] for name in controlled}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            dotted = _dotted(node.func)
            if dotted in controlled:
                values[dotted].append(owner(node))
    return {name: tuple(sorted(owners)) for name, owners in values.items()}


def _transport_attempt_call_count(function: ast.FunctionDef) -> int:
    return sum(
        isinstance(node, ast.Call) and _dotted(node.func) == "_transport_attempt"
        for node in ast.walk(function)
    )


def _runtime_violations(tree: ast.Module) -> list[ast.AST]:
    violations: list[ast.AST] = []
    forbidden_calls = {
        "OpenAI",
        "AsyncOpenAI",
        "Client",
        "AsyncClient",
        "with_options",
        "sleep",
        "create",
        "open",
        "print",
    }
    forbidden_aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if (module == "openai" and alias.name in forbidden_calls) or (
                    module == "time" and alias.name == "sleep"
                ):
                    forbidden_aliases.add(alias.asname or alias.name)
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }

    def enclosing_function(node: ast.AST) -> str | None:
        parent = parents.get(node)
        while parent is not None:
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return parent.name
            parent = parents.get(parent)
        return None

    bounded_calls = {
        "isfinite",
        "parsedate_to_datetime",
        "random",
        "sleep",
        "time",
    }
    bounded_functions = {
        "_retry_delay",
        "execute_openai_responses_with_transport_retry",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            dotted = _dotted(node.func)
            if dotted == "client.responses.create":
                continue
            target = _dotted(node.args[0]) if node.args else None
            indirect_create = (
                dotted == "getattr"
                and len(node.args) >= 2
                and target is not None
                and target.endswith(".responses")
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value == "create"
            )
            if (
                dotted
                and (
                    (dotted.startswith("_openai.") and dotted != "_openai.__version__")
                    or (
                        dotted.rsplit(".", 1)[-1] in forbidden_calls
                        and not (
                            dotted in bounded_calls
                            and enclosing_function(node) in bounded_functions
                        )
                    )
                    or (
                        dotted in forbidden_aliases
                        and not (
                            dotted in bounded_calls
                            and enclosing_function(node) in bounded_functions
                        )
                    )
                    or dotted.endswith(".responses.create")
                )
                or indirect_create
            ):
                violations.append(node)
        elif isinstance(node, ast.Attribute):
            dotted = _dotted(node)
            if (
                dotted
                and dotted.startswith("_openai.")
                and dotted.rsplit(".", 1)[-1] not in _ALLOWED_OPENAI_ATTRIBUTES
            ):
                violations.append(node)
            elif dotted and dotted.endswith(".responses.create"):
                parent = parents.get(node)
                if not (
                    isinstance(parent, ast.Call)
                    and parent.func is node
                    and dotted == "client.responses.create"
                ):
                    violations.append(node)
    return violations


def _module_effects(tree: ast.Module) -> list[ast.AST]:
    values: list[ast.AST] = []

    def expression(node: ast.AST) -> None:
        values.extend(
            candidate for candidate in ast.walk(node) if isinstance(candidate, ast.Call)
        )

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    values.append(decorator)
                else:
                    expression(decorator)
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default:
                    expression(default)
            annotations = [
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            ]
            if node.args.vararg:
                annotations.append(node.args.vararg)
            if node.args.kwarg:
                annotations.append(node.args.kwarg)
            for argument in annotations:
                if argument.annotation:
                    expression(argument.annotation)
            if node.returns:
                expression(node.returns)
            return
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    values.append(decorator)
                else:
                    expression(decorator)
            for child in node.body:
                statement(child)
            return
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Pass)):
            return
        expression(node)

    for node in tree.body:
        statement(node)
    return values


def _mutable_globals(tree: ast.Module) -> list[str]:
    values: list[str] = []

    def mutable(value: ast.AST) -> bool:
        return isinstance(
            value,
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

    def target_name(target: ast.AST) -> str | None:
        return target.id if isinstance(target, ast.Name) else None

    def expression(node: ast.AST) -> None:
        for candidate in ast.walk(node):
            if isinstance(candidate, ast.NamedExpr) and mutable(candidate.value):
                name = target_name(candidate.target)
                if name and name != "__all__":
                    values.append(name)

    def statement(node: ast.stmt) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return
        if isinstance(node, ast.Assign) and mutable(node.value):
            for target in node.targets:
                name = target_name(target)
                if name and name != "__all__":
                    values.append(name)
            return
        if isinstance(node, ast.AnnAssign) and node.value and mutable(node.value):
            name = target_name(node.target)
            if name and name != "__all__":
                values.append(name)
            return
        if isinstance(node, (ast.For, ast.AsyncFor)):
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
    return values


def test_inventory_and_path_specific_imports() -> None:
    assert sorted(path.name for path in _PACKAGE.glob("*.py")) == [
        "__init__.py",
        "_execution.py",
        "_response_mapping.py",
        "_schema_compatibility.py",
        "request_preparation.py",
    ]
    for path in _PRODUCTION_FILES:
        for kind, module in _imports(_tree(path)):
            allowed: set[str] = (
                _ALLOWED_STDLIB if path.name == "_execution.py" else set()
            )
            absolute: set[str] = (
                _ALLOWED_ABSOLUTE if path.name == "_execution.py" else set()
            )
            if path.name != "_execution.py":
                continue
            if kind == "absolute" and module in (*allowed, *absolute):
                continue
            if kind == "relative" and module in _ALLOWED_RELATIVE[path.name]:
                continue
            pytest.fail(f"unexpected import in {path.name}: {kind}:{module}")


def test_executor_has_exact_single_sdk_call_and_no_runtime_escape() -> None:
    tree = _tree(_EXECUTION)
    create_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and _dotted(node.func) == "client.responses.create"
    ]
    assert len(create_calls) == 1
    owner = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and any(call is create_calls[0] for call in ast.walk(node))
    )
    assert owner.name == "_transport_attempt"
    retry_function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "execute_openai_responses_with_transport_retry"
    )
    assert not any(
        isinstance(node, (ast.For, ast.AsyncFor, ast.While))
        for node in ast.walk(retry_function)
    )
    assert not _runtime_violations(tree)
    assert not _module_effects(tree)
    assert not _mutable_globals(tree)


def test_controlled_calls_have_exact_private_owners_and_attempt_counts() -> None:
    tree = _tree(_EXECUTION)
    owners = _controlled_call_owners(tree)
    assert owners == {
        "isfinite": (
            "_retry_delay",
            "_retry_delay.positive",
            "execute_openai_responses_with_transport_retry",
            "execute_openai_responses_with_transport_retry",
        ),
        "monotonic": (
            "_transport_attempt",
            "_transport_attempt",
            "_transport_attempt",
            "execute_openai_responses_with_transport_retry",
            "execute_openai_responses_with_transport_retry",
            "execute_openai_responses_with_transport_retry",
        ),
        "parsedate_to_datetime": ("_retry_delay",),
        "random": ("_retry_delay",),
        "sleep": ("execute_openai_responses_with_transport_retry",),
        "time": ("_retry_delay",),
    }
    functions = {
        node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    assert (
        _transport_attempt_call_count(functions["execute_openai_responses_attempt"])
        == 1
    )
    assert (
        _transport_attempt_call_count(
            functions["execute_openai_responses_with_transport_retry"]
        )
        == 2
    )
    third_attempt = ast.parse(
        "def execute_openai_responses_with_transport_retry():\n"
        "    _transport_attempt()\n"
        "    _transport_attempt()\n"
        "    _transport_attempt()\n"
    )
    mutated = next(
        node for node in ast.walk(third_attempt) if isinstance(node, ast.FunctionDef)
    )
    assert _transport_attempt_call_count(mutated) == 3
    assert _transport_attempt_call_count(mutated) != 2


@pytest.mark.parametrize(
    ("name", "source"),
    [
        ("monotonic", "def leaked():\n    return monotonic()\n"),
        ("isfinite", "def leaked():\n    return isfinite(1.0)\n"),
        (
            "parsedate_to_datetime",
            "def leaked():\n    return parsedate_to_datetime('x')\n",
        ),
        ("random", "def leaked():\n    return random()\n"),
        ("sleep", "def leaked():\n    return sleep(0.5)\n"),
        ("time", "def leaked():\n    return time()\n"),
    ],
)
def test_controlled_call_wrong_owner_is_rejected(name: str, source: str) -> None:
    owners = _controlled_call_owners(ast.parse(source))
    assert owners[name] == ("leaked",)
    assert owners[name] not in {
        ("_retry_delay",),
        ("_retry_delay.positive",),
        ("_transport_attempt",),
        ("execute_openai_responses_with_transport_retry",),
    }


def test_executor_import_aliases_are_exact_and_call_is_private_only() -> None:
    tree = _tree(_EXECUTION)
    assert _import_bindings(tree) == _EXPECTED_EXECUTION_IMPORTS
    imports = [
        node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    assert any(
        isinstance(node, ast.Import)
        and [(alias.name, alias.asname) for alias in node.names]
        == [("openai", "_openai")]
        for node in imports
    )
    assert not any(
        isinstance(node, ast.Import)
        and alias.name == "openai"
        and alias.asname != "_openai"
        for node in imports
        for alias in node.names
    )
    assert _runtime_violations(ast.parse("import openai as sdk\nsdk.OpenAI()"))
    assert _runtime_violations(
        ast.parse("import openai as sdk\nsdk.responses.create({})")
    )
    assert _runtime_violations(
        ast.parse("from openai import OpenAI as Factory\nFactory()")
    )
    assert (
        not _import_bindings(ast.parse("from time import sleep as monotonic\n"))
        == _EXPECTED_EXECUTION_IMPORTS
    )


def test_only_executor_calls_responses_create_across_production() -> None:
    consumers: set[Path] = set()
    for path in _SOURCE.rglob("*.py"):
        for node in ast.walk(_tree(path)):
            if isinstance(node, ast.Call) and (_dotted(node.func) or "").endswith(
                ".responses.create"
            ):
                consumers.add(path)
    assert consumers == {_EXECUTION}
    create_calls = [
        node
        for node in ast.walk(_tree(_EXECUTION))
        if isinstance(node, ast.Call)
        and _dotted(node.func) == "client.responses.create"
    ]
    assert len(create_calls) == 1


@pytest.mark.parametrize(
    "source",
    [
        "@print\ndef leaked():\n    return 1\n",
        "def leaked(value=open('x')):\n    return value\n",
        "class Leaked:\n    value = open('x')\n",
        "if True:\n    _CACHE = []\n",
        "if (_CACHE := []):\n    pass\n",
        "client.responses.create(payload={})\n",
        "_openai.OpenAI()\n",
        "sleep(0.5)\n",
    ],
)
def test_single_mutation_probes_are_rejected(source: str) -> None:
    tree = ast.parse(source)
    assert (
        _module_effects(tree)
        or _mutable_globals(tree)
        or any(
            isinstance(node, ast.Call)
            and _dotted(node.func)
            and _dotted(node.func) != "_openai.__version__"
            for node in ast.walk(tree)
        )
    )


@pytest.mark.parametrize(
    "source",
    [
        "def leaked():\n    return sdk.OpenAI()\n",
        "def leaked():\n    return sdk.responses.create({})\n",
        "def leaked():\n    return sdk.with_options(timeout=1)\n",
    ],
)
def test_runtime_provider_alias_mutations_are_rejected(source: str) -> None:
    baseline = ast.parse("import openai as sdk\ndef execute():\n    return 1\n")
    assert _runtime_violations(baseline) == []
    assert _runtime_violations(ast.parse("import openai as sdk\n" + source))


def _production_shaped_source() -> str:
    return """\
from __future__ import annotations
from time import monotonic
from typing import cast
import openai as _openai

def execute(*, client: _openai.OpenAI, payload: object) -> object:
    request_body = cast(object, payload)
    start = monotonic()
    response = client.responses.create(**request_body)
    finish = monotonic()
    return response
"""


@pytest.mark.parametrize(
    "mutation",
    [
        "\nfrom openai import OpenAI as Factory\nFactory()\n",
        "\ngetattr(client.responses, 'create')()\n",
        "\ncreate = client.responses.create\n",
        "\ndef leaked(value: _openai.OpenAI()):\n    return value\n",
        "\ndef leaked(value: factory()):\n    return value\n",
        "\ndef leaked(value=open('x')):\n    return value\n",
        "\nfrom time import sleep as monotonic\n",
        "\ndef leaked():\n    return sleep(0.5)\n",
    ],
)
def test_production_shaped_single_mutations_are_rejected(mutation: str) -> None:
    baseline = ast.parse(_production_shaped_source())
    assert _runtime_violations(baseline) == []
    assert _module_effects(baseline) == []
    assert _mutable_globals(baseline) == []

    mutated = ast.parse(_production_shaped_source() + mutation)
    assert (
        _runtime_violations(mutated)
        or _module_effects(mutated)
        or _mutable_globals(mutated)
        or _import_bindings(mutated) != _import_bindings(baseline)
    )
