"""Architecture boundaries for private Durable Dispatch application ports."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ai_ecommerce_agent.modules.durable_dispatch import public

pytestmark = pytest.mark.architecture

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_APPLICATION_ROOT = (
    _BACKEND_ROOT
    / "src"
    / "ai_ecommerce_agent"
    / "modules"
    / "durable_dispatch"
    / "application"
)
_PRODUCTION_FILES = (
    _APPLICATION_ROOT / "__init__.py",
    _APPLICATION_ROOT / "ports.py",
    _APPLICATION_ROOT / "lease_commands.py",
    _APPLICATION_ROOT / "lease_protocols.py",
    _APPLICATION_ROOT / "lease_errors.py",
    _APPLICATION_ROOT / "lease_services.py",
    _APPLICATION_ROOT / "control_queries.py",
    _APPLICATION_ROOT / "control_commands.py",
    _APPLICATION_ROOT / "control_results.py",
    _APPLICATION_ROOT / "control_protocols.py",
    _APPLICATION_ROOT / "control_errors.py",
)
_ALLOWED_RELATIVE_IMPORTS: dict[Path, frozenset[tuple[int, str | None]]] = {
    _APPLICATION_ROOT / "__init__.py": frozenset({(1, "ports")}),
    _APPLICATION_ROOT / "ports.py": frozenset(
        {
            (1, "lease_commands"),
            (2, "domain.identity"),
            (2, "domain.snapshots"),
        }
    ),
    _APPLICATION_ROOT / "lease_commands.py": frozenset(
        {(2, "domain.identity"), (2, "domain.ownership")}
    ),
    _APPLICATION_ROOT / "lease_protocols.py": frozenset(
        {(1, "lease_commands"), (2, "domain.snapshots")}
    ),
    _APPLICATION_ROOT / "lease_errors.py": frozenset(
        {(2, "domain.identity"), (2, "domain.status")}
    ),
    _APPLICATION_ROOT / "lease_services.py": frozenset(
        {
            (1, "lease_commands"),
            (1, "lease_errors"),
            (1, "lease_protocols"),
            (1, "ports"),
            (2, "domain.identity"),
            (2, "domain.snapshots"),
        }
    ),
    _APPLICATION_ROOT / "control_queries.py": frozenset(
        {(2, "domain.identity"), (2, "domain.ownership")}
    ),
    _APPLICATION_ROOT / "control_commands.py": frozenset(
        {
            (2, "domain.envelope"),
            (2, "domain.identity"),
            (2, "domain.ownership"),
        }
    ),
    _APPLICATION_ROOT / "control_results.py": frozenset(
        {(2, "domain.snapshots"), (2, "domain.status")}
    ),
    _APPLICATION_ROOT / "control_protocols.py": frozenset(
        {
            (1, "control_commands"),
            (1, "control_queries"),
            (1, "control_results"),
            (2, "domain.snapshots"),
        }
    ),
    _APPLICATION_ROOT / "control_errors.py": frozenset(
        {(2, "domain.identity"), (2, "domain.status")}
    ),
}
_ALLOWED_STDLIB_IMPORTS: dict[Path, frozenset[str]] = {
    _APPLICATION_ROOT / "__init__.py": frozenset(),
    _APPLICATION_ROOT / "ports.py": frozenset({"__future__", "typing"}),
    _APPLICATION_ROOT / "lease_commands.py": frozenset(
        {"__future__", "dataclasses", "datetime"}
    ),
    _APPLICATION_ROOT / "lease_protocols.py": frozenset({"__future__", "typing"}),
    _APPLICATION_ROOT / "lease_errors.py": frozenset({"__future__", "dataclasses"}),
    _APPLICATION_ROOT / "lease_services.py": frozenset({"__future__", "typing"}),
    _APPLICATION_ROOT / "control_queries.py": frozenset(
        {"__future__", "dataclasses", "datetime"}
    ),
    _APPLICATION_ROOT / "control_commands.py": frozenset(
        {"__future__", "dataclasses", "datetime"}
    ),
    _APPLICATION_ROOT / "control_results.py": frozenset(
        {"__future__", "dataclasses", "enum"}
    ),
    _APPLICATION_ROOT / "control_protocols.py": frozenset({"__future__", "typing"}),
    _APPLICATION_ROOT / "control_errors.py": frozenset({"__future__", "dataclasses"}),
}
_ALLOWED_ABSOLUTE_IMPORTS: dict[Path, frozenset[str]] = {
    _APPLICATION_ROOT / "__init__.py": frozenset(),
    _APPLICATION_ROOT / "ports.py": frozenset(
        {
            "ai_ecommerce_agent.application.ports",
            "ai_ecommerce_agent.shared_kernel",
        }
    ),
    _APPLICATION_ROOT / "lease_commands.py": frozenset(
        {"ai_ecommerce_agent.shared_kernel"}
    ),
    _APPLICATION_ROOT / "lease_protocols.py": frozenset(),
    _APPLICATION_ROOT / "lease_errors.py": frozenset(
        {"ai_ecommerce_agent.shared_kernel"}
    ),
    _APPLICATION_ROOT / "lease_services.py": frozenset(
        {
            "ai_ecommerce_agent.modules.durable_dispatch.application.errors",
            "ai_ecommerce_agent.shared_kernel",
        }
    ),
    _APPLICATION_ROOT / "control_queries.py": frozenset(
        {"ai_ecommerce_agent.shared_kernel"}
    ),
    _APPLICATION_ROOT / "control_commands.py": frozenset(
        {"ai_ecommerce_agent.shared_kernel"}
    ),
    _APPLICATION_ROOT / "control_results.py": frozenset(
        {"ai_ecommerce_agent.shared_kernel"}
    ),
    _APPLICATION_ROOT / "control_protocols.py": frozenset(),
    _APPLICATION_ROOT / "control_errors.py": frozenset(
        {"ai_ecommerce_agent.shared_kernel"}
    ),
}
_FORBIDDEN_IMPORT_PREFIXES = (
    "sqlalchemy",
    "psycopg",
    "fastapi",
    "starlette",
    "langgraph",
    "openai",
    "anthropic",
    "os",
    "pathlib",
    "socket",
    "subprocess",
    "dotenv",
)


def _dotted_name(node: ast.AST) -> str | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def _trees() -> list[tuple[Path, ast.Module]]:
    return [
        (path, ast.parse(path.read_text(encoding="utf-8")))
        for path in _PRODUCTION_FILES
    ]


def test_application_ports_have_only_framework_neutral_allowlisted_imports() -> None:
    for path, tree in _trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    assert (node.level, node.module) in _ALLOWED_RELATIVE_IMPORTS[path]
                    continue
                imported_names = [node.module or ""]
            else:
                continue
            for imported in imported_names:
                if imported in _ALLOWED_ABSOLUTE_IMPORTS[path]:
                    continue
                root_name = imported.split(".", 1)[0]
                assert root_name in _ALLOWED_STDLIB_IMPORTS[path], (
                    f"{path} imports disallowed module {imported!r}"
                )
                assert not imported.startswith(_FORBIDDEN_IMPORT_PREFIXES), (
                    f"{path} imports forbidden module {imported!r}"
                )


def _import_time_effects(
    tree: ast.Module,
) -> tuple[list[ast.Call], list[tuple[str, str | None, bool]]]:
    """Collect calls and decorator applications executed at import time.

    Function and method bodies are intentionally skipped. Their decorators,
    defaults, annotations, and return annotations are still visited because
    those expressions execute while the definition is created.
    """

    calls: list[ast.Call] = []
    decorators: list[tuple[str, str | None, bool]] = []

    def visit_decorator(node: ast.AST, scope: str) -> None:
        if isinstance(node, ast.Call):
            decorators.append((scope, _dotted_name(node.func), True))
        else:
            decorators.append((scope, _dotted_name(node), False))
        visit(node)

    def visit(node: ast.AST, *, class_name: str | None = None) -> None:
        if isinstance(node, ast.Call):
            calls.append(node)
            visit(node.func)
            for argument in node.args:
                visit(argument)
            for keyword in node.keywords:
                visit(keyword.value)
            return

        if isinstance(node, ast.Module):
            for statement in node.body:
                visit(statement)
            return

        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                visit_decorator(decorator, f"class:{node.name}")
            for base in node.bases:
                visit(base)
            for keyword in node.keywords:
                visit(keyword.value)
            for statement in node.body:
                visit(statement, class_name=node.name)
            return

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scope = (
                f"method:{class_name}.{node.name}"
                if class_name is not None
                else f"function:{node.name}"
            )
            for decorator in node.decorator_list:
                visit_decorator(decorator, scope)
            for default in node.args.defaults:
                visit(default)
            for default in node.args.kw_defaults:
                if default is not None:
                    visit(default)
            arguments = [
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            ]
            if node.args.vararg is not None:
                arguments.append(node.args.vararg)
            if node.args.kwarg is not None:
                arguments.append(node.args.kwarg)
            for argument in arguments:
                if argument.annotation is not None:
                    visit(argument.annotation)
            if node.returns is not None:
                visit(node.returns)
            return

        if isinstance(node, ast.Lambda):
            for default in node.args.defaults:
                visit(default)
            for default in node.args.kw_defaults:
                if default is not None:
                    visit(default)
            return

        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return calls, decorators


def test_protocols_use_only_exact_bare_runtime_checkable_decorators() -> None:
    expected_protocols = {
        _APPLICATION_ROOT / "ports.py": [
            "WorkIntentRepositoryPort",
            "WorkIntentLeaseRepositoryPort",
            "DurableDispatchUnitOfWork",
            "DurableDispatchUnitOfWorkFactory",
        ],
        _APPLICATION_ROOT / "lease_protocols.py": ["DurableDispatchLeaseApplication"],
        _APPLICATION_ROOT / "control_protocols.py": [
            "DurableDispatchControlApplication"
        ],
    }
    for path, expected_names in expected_protocols.items():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        protocol_classes = [
            node for node in tree.body if isinstance(node, ast.ClassDef)
        ]
        assert [node.name for node in protocol_classes] == expected_names
        for protocol_class in protocol_classes:
            assert len(protocol_class.decorator_list) == 1
            decorator = protocol_class.decorator_list[0]
            assert isinstance(decorator, ast.Name)
            assert decorator.id == "runtime_checkable"


def test_application_ports_allow_only_the_frozen_decorator_applications() -> None:
    expected_decorators = {
        _APPLICATION_ROOT / "__init__.py": [],
        _APPLICATION_ROOT / "ports.py": [
            ("class:WorkIntentRepositoryPort", "runtime_checkable", False),
            ("class:WorkIntentLeaseRepositoryPort", "runtime_checkable", False),
            ("class:DurableDispatchUnitOfWork", "runtime_checkable", False),
            ("method:DurableDispatchUnitOfWork.work_intents", "property", False),
            (
                "method:DurableDispatchUnitOfWork.work_intent_leases",
                "property",
                False,
            ),
            ("class:DurableDispatchUnitOfWorkFactory", "runtime_checkable", False),
        ],
        _APPLICATION_ROOT / "lease_commands.py": [
            ("class:ClaimNextWorkIntent", "dataclass", True),
            ("class:HeartbeatWorkIntentLease", "dataclass", True),
        ],
        _APPLICATION_ROOT / "lease_protocols.py": [
            ("class:DurableDispatchLeaseApplication", "runtime_checkable", False),
        ],
        _APPLICATION_ROOT / "lease_errors.py": [
            ("class:DurableDispatchLeaseError", "dataclass", True),
        ],
        _APPLICATION_ROOT / "lease_services.py": [],
        _APPLICATION_ROOT / "control_queries.py": [
            ("class:CheckOwnedWorkIntentControl", "dataclass", True),
        ],
        _APPLICATION_ROOT / "control_commands.py": [
            ("class:RequestWorkIntentCancellation", "dataclass", True),
            ("class:SupersedeWorkIntent", "dataclass", True),
            ("class:AcknowledgeWorkIntentStop", "dataclass", True),
        ],
        _APPLICATION_ROOT / "control_results.py": [
            ("class:OwnedWorkIntentControlCheck", "dataclass", True),
            ("class:WorkIntentSupersessionResult", "dataclass", True),
        ],
        _APPLICATION_ROOT / "control_protocols.py": [
            ("class:DurableDispatchControlApplication", "runtime_checkable", False),
        ],
        _APPLICATION_ROOT / "control_errors.py": [
            ("class:DurableDispatchControlError", "dataclass", True),
        ],
    }
    expected_calls = {
        _APPLICATION_ROOT / "__init__.py": [],
        _APPLICATION_ROOT / "ports.py": [],
        _APPLICATION_ROOT / "lease_commands.py": ["dataclass", "dataclass"],
        _APPLICATION_ROOT / "lease_protocols.py": [],
        _APPLICATION_ROOT / "lease_errors.py": ["dataclass"],
        _APPLICATION_ROOT / "lease_services.py": [],
        _APPLICATION_ROOT / "control_queries.py": ["dataclass"],
        _APPLICATION_ROOT / "control_commands.py": [
            "dataclass",
            "dataclass",
            "dataclass",
        ],
        _APPLICATION_ROOT / "control_results.py": ["dataclass", "dataclass"],
        _APPLICATION_ROOT / "control_protocols.py": [],
        _APPLICATION_ROOT / "control_errors.py": ["dataclass"],
    }
    for path, tree in _trees():
        calls, decorators = _import_time_effects(tree)
        assert [_dotted_name(call.func) for call in calls] == expected_calls[path]
        assert decorators == expected_decorators[path]


def test_application_modules_have_only_frozen_import_time_calls() -> None:
    for path, tree in _trees():
        calls, _ = _import_time_effects(tree)
        expected = {
            _APPLICATION_ROOT / "lease_commands.py": ["dataclass", "dataclass"],
            _APPLICATION_ROOT / "lease_errors.py": ["dataclass"],
            _APPLICATION_ROOT / "control_queries.py": ["dataclass"],
            _APPLICATION_ROOT / "control_commands.py": [
                "dataclass",
                "dataclass",
                "dataclass",
            ],
            _APPLICATION_ROOT / "control_results.py": ["dataclass", "dataclass"],
            _APPLICATION_ROOT / "control_errors.py": ["dataclass"],
        }.get(path, [])
        assert [_dotted_name(call.func) for call in calls] == expected, path


def test_import_time_guard_rejects_calls_and_bare_behavior_decorators() -> None:
    tree = ast.parse(
        """
from typing import Protocol, runtime_checkable

@runtime_checkable
class Allowed(Protocol):
    @property
    def value(self):
        pass

@runtime_checkable()
class RejectedDecorator(Protocol):
    pass

@print
def leaked():
    pass

class RejectedClass:
    @print
    def method(self):
        pass

    token = runtime_checkable()

@print
class RejectedClassDecorator:
    pass

value = runtime_checkable()

def rejected_function(default=runtime_checkable()):
    pass
"""
    )
    calls, decorators = _import_time_effects(tree)
    assert [_dotted_name(call.func) for call in calls] == [
        "runtime_checkable",
        "runtime_checkable",
        "runtime_checkable",
        "runtime_checkable",
    ]
    assert ("class:Allowed", "runtime_checkable", False) in decorators
    assert ("method:Allowed.value", "property", False) in decorators
    assert {
        ("class:RejectedDecorator", "runtime_checkable", True),
        ("function:leaked", "print", False),
        ("method:RejectedClass.method", "print", False),
        ("class:RejectedClassDecorator", "print", False),
    }.issubset(set(decorators))


def test_application_ports_remain_private_to_durable_dispatch() -> None:
    for name in (
        "DurableDispatchUnitOfWork",
        "DurableDispatchUnitOfWorkFactory",
        "WorkIntentRepositoryPort",
        "DurableDispatchLeaseApplicationService",
    ):
        assert not hasattr(public, name)
