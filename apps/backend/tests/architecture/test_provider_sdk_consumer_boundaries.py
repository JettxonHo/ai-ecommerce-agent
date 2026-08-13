"""Repository-wide provider SDK consumer boundary."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.architecture

_BACKEND = Path(__file__).resolve().parents[2]
_SOURCE = _BACKEND / "src"
_DEEPSEEK_PACKAGE = _SOURCE / "ai_ecommerce_agent/platform/model_runtime/deepseek"


def _imports(tree: ast.Module) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.extend(("absolute", alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            values.append(("relative" if node.level else "absolute", module))
    return values


def _expected_sdk_consumers() -> set[Path]:
    return {
        _DEEPSEEK_PACKAGE / "_response_mapping.py",
        _DEEPSEEK_PACKAGE / "_runtime.py",
    }


def _sdk_consumers() -> set[Path]:
    consumers: set[Path] = set()
    for path in _SOURCE.rglob("*.py"):
        if "tests" in path.parts:
            continue
        for kind, module in _imports(ast.parse(path.read_text(encoding="utf-8"))):
            if kind == "absolute" and (
                module == "openai" or module.startswith("openai.")
            ):
                consumers.add(path)
    return consumers


def _assert_exact_sdk_consumers(consumers: set[Path]) -> None:
    assert consumers == _expected_sdk_consumers()


def test_repository_has_exact_private_sdk_consumers() -> None:
    _assert_exact_sdk_consumers(_sdk_consumers())


def test_sdk_consumer_inventory_rejects_one_synthetic_extra_consumer() -> None:
    synthetic = _DEEPSEEK_PACKAGE / "_synthetic_provider_consumer.py"
    with pytest.raises(AssertionError):
        _assert_exact_sdk_consumers(_expected_sdk_consumers() | {synthetic})
