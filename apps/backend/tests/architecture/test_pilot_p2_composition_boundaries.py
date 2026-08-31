"""Static boundaries for the isolated P2 DeepSeek bootstrap."""

from __future__ import annotations

import inspect
from pathlib import Path

from ai_ecommerce_agent.bootstrap import local_demo, pilot_p2


def test_p2_bootstrap_does_not_import_or_select_scripted_runtime() -> None:
    source = inspect.getsource(pilot_p2)

    assert "build_scripted_runtime" not in source
    assert "platform.model_runtime.scripted" not in source
    assert (
        "runtime_factory"
        not in inspect.signature(pilot_p2.compose_pilot_p2_pipeline).parameters
    )


def test_default_local_demo_does_not_import_p2_bootstrap() -> None:
    source = Path(inspect.getfile(local_demo)).read_text()

    assert "pilot_p2" not in source
    assert "compose_pilot_p2_pipeline" not in source
