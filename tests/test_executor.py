"""PipelineExecutor tests."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import pytest

from oris.components.base import Component
from oris.core.enums import ExecutionStatus
from oris.core.exceptions import ComponentExecutionError, GuardViolationError
from oris.rai.factory import build_default_guards
from oris.runtime.executor import PipelineExecutor


class AddFieldComponent(Component):
    def run(self, data: dict[str, object]) -> dict[str, object]:
        out = dict(data)
        out["output"] = "done"
        return out


class ExplodingComponent(Component):
    def run(self, data: dict[str, object]) -> dict[str, object]:
        _ = data
        raise RuntimeError("boom")


def _executor(
    components: list[Component],
    *,
    rai_pre_hooks: Sequence[Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
    rai_post_hooks: Sequence[Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
) -> PipelineExecutor:
    ig, og = build_default_guards()
    return PipelineExecutor(
        components=components,
        input_guard=ig,
        output_guard=og,
        rai_pre_hooks=rai_pre_hooks,
        rai_post_hooks=rai_post_hooks,
    )


def test_executor_runs_sequentially() -> None:
    executor = _executor([AddFieldComponent(name="add", config={})])
    result = executor.run({"query": "hello"})
    assert result.output["output"] == "done"
    assert result.trace.status == ExecutionStatus.SUCCEEDED.value
    assert len(result.trace.steps) >= 3
    assert all(s.latency_ms >= 0 for s in result.trace.steps)


def test_executor_blocks_bad_input() -> None:
    executor = _executor([AddFieldComponent(name="add", config={})])
    with pytest.raises(GuardViolationError):
        executor.run({"token": "abc"})


def test_executor_wraps_component_error() -> None:
    executor = _executor([ExplodingComponent(name="explode", config={})])
    with pytest.raises(ComponentExecutionError):
        executor.run({"query": "hello"})


def test_executor_rai_pre_and_post_hooks() -> None:
    def pre(d: dict[str, object]) -> dict[str, object]:
        out = dict(d)
        out["pre"] = True
        return out

    def post(d: dict[str, object]) -> dict[str, object]:
        out = dict(d)
        out["post"] = True
        return out

    ig, og = build_default_guards()
    executor = PipelineExecutor(
        components=[AddFieldComponent(name="add", config={})],
        input_guard=ig,
        output_guard=og,
        rai_pre_hooks=(pre,),
        rai_post_hooks=(post,),
    )
    result = executor.run({"query": "x"})
    assert result.output["pre"] is True
    assert result.output["post"] is True
    hook_steps = [s for s in result.trace.steps if s.flags.get("kind") == "rai_hook"]
    assert len(hook_steps) == 2
