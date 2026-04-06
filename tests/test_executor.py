"""RuntimeExecutor / PipelineExecutor tests."""

from __future__ import annotations

from collections.abc import Sequence
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
from oris.rai.policy import PolicyEnforcer
from oris.runtime.context import ExecutionContext
from oris.runtime.executor import PipelineExecutor, RuntimeExecutor
from oris.runtime.hooks import (
    PipelinePostHookLike,
    PipelinePreHookLike,
    PostStepHookLike,
    PreStepHookLike,
)


class AddFieldComponent(Component):
    def run(self, data: dict[str, object], context: ExecutionContext) -> dict[str, object]:
        _ = context
        out = dict(data)
        out["output"] = "done"
        return out


class ExplodingComponent(Component):
    def run(self, data: dict[str, object], context: ExecutionContext) -> dict[str, object]:
        _ = data
        _ = context
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
    policy: PolicyEnforcer | None = None,
    rai_pre_hooks: Sequence[PipelinePreHookLike] | None = None,
    rai_post_hooks: Sequence[PipelinePostHookLike] | None = None,
    pre_step_hooks: Sequence[PreStepHookLike] | None = None,
    post_step_hooks: Sequence[PostStepHookLike] | None = None,
) -> RuntimeExecutor:
    return RuntimeExecutor(
        plan=_plan_from_components(components),
        policy=policy or PolicyEnforcer(),
        rai_pre_hooks=rai_pre_hooks,
        rai_post_hooks=rai_post_hooks,
        pre_step_hooks=pre_step_hooks,
        post_step_hooks=post_step_hooks,
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
    def pre(d: dict[str, object], _ctx: ExecutionContext) -> dict[str, object]:
        out = dict(d)
        out["pre"] = True
        return out

    def post(d: dict[str, object], _ctx: ExecutionContext) -> dict[str, object]:
        out = dict(d)
        out["post"] = True
        return out

    executor = RuntimeExecutor(
        plan=_plan_from_components([AddFieldComponent(name="add", config={})]),
        policy=PolicyEnforcer(),
        rai_pre_hooks=(pre,),
        rai_post_hooks=(post,),
    )
    result = executor.run({"query": "x"})
    assert result.output["pre"] is True
    assert result.output["post"] is True
    hook_steps = [s for s in result.trace.steps if s.flags.get("kind") == "rai_hook"]
    assert len(hook_steps) == 2


def test_hook_failure_records_failed_trace() -> None:
    def bad_hook(_: dict[str, object], __: ExecutionContext) -> dict[str, object]:
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


def test_executor_uses_injected_policy_instance() -> None:
    custom = PolicyEnforcer(blocked_input_keys={"nope"})
    executor = _executor([AddFieldComponent(name="add", config={})], policy=custom)
    with pytest.raises(GuardViolationError):
        executor.run({"nope": "x"})


def test_custom_pipeline_hooks_replace_builtin_policy_hooks() -> None:
    """Full ``pipeline_pre_hooks`` / ``pipeline_post_hooks`` override skips default RAI hooks."""

    def passthrough(data: dict[str, Any], _ctx: ExecutionContext) -> dict[str, Any]:
        return dict(data)

    executor = RuntimeExecutor(
        plan=_plan_from_components([AddFieldComponent(name="add", config={})]),
        policy=PolicyEnforcer(),
        pipeline_pre_hooks=(passthrough,),
        pipeline_post_hooks=(passthrough,),
    )
    # Default input policy would reject ``secret``; overridden pre hook allows it.
    result = executor.run({"secret": "x", "query": "ok"})
    assert result.output["output"] == "done"


def test_pre_and_post_step_hooks() -> None:
    def pre(
        data: dict[str, Any],
        ctx: ExecutionContext,
    ) -> dict[str, Any]:
        out = dict(data)
        out["seen_index_pre"] = ctx.step_index
        return out

    def post(
        data: dict[str, Any],
        ctx: ExecutionContext,
    ) -> dict[str, Any]:
        out = dict(data)
        out["seen_index_post"] = ctx.step_index
        return out

    executor = _executor(
        [AddFieldComponent(name="add", config={})],
        pre_step_hooks=(pre,),
        post_step_hooks=(post,),
    )
    result = executor.run({"query": "z"})
    assert result.output["seen_index_pre"] == 0
    assert result.output["seen_index_post"] == 0
    kinds = [s.flags.get("kind") for s in result.trace.steps]
    assert "step_pre_hook" in kinds
    assert "step_post_hook" in kinds
