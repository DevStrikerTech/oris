"""Orchestrator tests."""

from __future__ import annotations

import pytest

from oris.components.base import Component
from oris.core.exceptions import ComponentExecutionError
from oris.runtime.orchestrator import PipelineOrchestrator


class IncrementComponent(Component):
    def run(self, data: dict[str, object]) -> dict[str, object]:
        out = dict(data)
        raw_count = out.get("count", 0)
        count = raw_count if isinstance(raw_count, int) else 0
        out["count"] = count + 1
        return out


class FailingComponent(Component):
    def run(self, data: dict[str, object]) -> dict[str, object]:
        _ = data
        raise ValueError("fail")


def test_orchestrator_runs_components() -> None:
    orchestrator = PipelineOrchestrator()
    result = orchestrator.run(
        components=[IncrementComponent(name="inc"), IncrementComponent(name="inc2")],
        input_data={"count": 0},
    )
    assert result["count"] == 2


def test_orchestrator_wraps_component_errors() -> None:
    orchestrator = PipelineOrchestrator()
    with pytest.raises(ComponentExecutionError):
        orchestrator.run(components=[FailingComponent(name="bad")], input_data={})
