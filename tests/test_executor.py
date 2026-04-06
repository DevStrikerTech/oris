"""RuntimeExecutor / PipelineExecutor tests."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import pytest

from oris.components.base import Component
from oris.core.enums import ExecutionStatus
from oris.core.exceptions import (
    ComponentExecutionError,
    GuardViolationError,
    PipelineExecutionError,
)
from oris.pipeline.plan import ExecutionPlan, ExecutionStep
from oris.rai.factory import build_default_guards
from oris.runtime.executor import PipelineExecutor, RuntimeExecutor


class AddFieldComponent(Component):
    def run(self, data: dict[str, object]) -> dict[str, object]:
        out = dict(data)
        out["output"] = "done"
        return out


class ExplodingComponent(Component):
    def run(self, data: dict[str, object]) -> dict[str, object]:
        _ = data
        raise RuntimeError("boom")


def _plan_from_components(components: list[Component]) -> ExecutionPlan:
    return ExecutionPlan(
        steps=[
            ExecutionStep(step_id=f"step_{index}", component=component)
            for index, component in enumerate(components)
        ],
        metadata={},
    )


def _executor(
    components: list[Component],
    *,
    rai_pre_hooks: Sequence[Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
    rai_post_hooks: Sequence[Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
) -> RuntimeExecutor:
    ig, og = build_default_guards()
    return RuntimeExecutor(
        plan=_plan_from_components(components),
        input_guard=ig,
        output_guard=og,
        rai_pre_hooks=rai_pre_hooks,
        rai_post_hooks=rai_post_hooks,
    )


def test_runtime_executor_alias_matches_runtime_executor() -> None:
    assert PipelineExecutor is RuntimeExecutor


def test_executor_runs_sequentially() -> None:
    executor = _executor([AddFieldComponent(name="add", config={})])
    result = executor.run({"query": "hello"})
    assert result.output["output"] == "done"
    assert result.trace.status == ExecutionStatus.SUCCEEDED.value
    assert len(result.trace.steps) >= 3
    assert all(s.latency_ms >= 0 for s in result.trace.steps)
    pipeline_steps = [s for s in result.trace.steps if s.flags.get("kind") == "pipeline_step"]
    assert pipeline_steps[0].step_id == "step_0"


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
    executor = RuntimeExecutor(
        plan=_plan_from_components([AddFieldComponent(name="add", config={})]),
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


def test_hook_failure_records_failed_trace() -> None:
    def bad_hook(_: dict[str, object]) -> dict[str, object]:
        raise RuntimeError("hook failed")

    executor = _executor(
        [AddFieldComponent(name="add", config={})],
        rai_pre_hooks=(bad_hook,),
    )
    with pytest.raises(PipelineExecutionError):
        executor.run({"query": "x"})


def test_run_summary_shape() -> None:
    executor = _executor([AddFieldComponent(name="add", config={})])
    result = executor.run({"query": "hello"})
    summary = result.to_run_summary()
    assert summary["run_id"] == result.trace.run_id
    assert summary["status"] == "success"
    assert "output" in summary
    assert isinstance(summary["trace"], list)
    assert all("step_id" in entry and "latency_ms" in entry for entry in summary["trace"])
