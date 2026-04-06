"""TraceManager behavior: hooks, component tracing, run metadata."""

from __future__ import annotations

import pytest

from oris.core.enums import ExecutionStatus
from oris.rai.hooks import InputPolicyHook, OutputPolicyHook
from oris.rai.policy import PolicyEnforcer
from oris.runtime.context import ExecutionContext
from oris.runtime.hooks import CallablePreStepHook, PipelinePostHook, PipelinePreHook
from oris.runtime.trace_manager import TraceManager
from tests.helpers import trivial_execution_context


def test_traced_hook_records_success_and_failure() -> None:
    tm = TraceManager()
    trace = tm.begin_run()
    ctx = trivial_execution_context(run_id=trace.run_id, policy=PolicyEnforcer())
    ctx.trace = trace

    class OkHook(PipelinePreHook):
        def invoke(self, data: dict[str, object], context: ExecutionContext) -> dict[str, object]:
            return dict(data)

    out = tm.traced_hook(
        trace,
        step_id="h0",
        component_name="h0",
        flags={"kind": "pipeline_hook"},
        data={"a": 1},
        context=ctx,
        hook=OkHook(),
    )
    assert out == {"a": 1}
    assert len(trace.steps) == 1
    assert trace.steps[0].status == ExecutionStatus.SUCCEEDED.value

    class BadHook(PipelinePreHook):
        def invoke(self, data: dict[str, object], context: ExecutionContext) -> dict[str, object]:
            raise RuntimeError("nope")

    with pytest.raises(RuntimeError):
        tm.traced_hook(
            trace,
            step_id="h1",
            component_name="h1",
            flags={"kind": "pipeline_hook"},
            data={},
            context=ctx,
            hook=BadHook(),
        )
    assert len(trace.steps) == 2
    assert trace.steps[1].status == ExecutionStatus.FAILED.value


def test_traced_component_records_orchestrator_style_success() -> None:
    tm = TraceManager()
    trace = tm.begin_run()

    def execute() -> dict[str, object]:
        return {"out": True}

    result = tm.traced_component(
        trace,
        step_id="step_0",
        component_name="c1",
        flags={"kind": "pipeline_step", "step_index": 0, "total_steps": 1},
        execute=execute,
    )
    assert result == {"out": True}
    assert len(trace.steps) == 1
    assert trace.steps[0].latency_ms >= 0


def test_traced_component_records_failure() -> None:
    tm = TraceManager()
    trace = tm.begin_run()

    def boom() -> dict[str, object]:
        raise ValueError("component error")

    with pytest.raises(ValueError, match="component error"):
        tm.traced_component(
            trace,
            step_id="step_0",
            component_name="c1",
            flags={"kind": "pipeline_step"},
            execute=boom,
        )
    assert len(trace.steps) == 1
    assert trace.steps[0].status == ExecutionStatus.FAILED.value


def test_finalize_success_attaches_pipeline_metadata() -> None:
    tm = TraceManager()
    trace = tm.begin_run()
    tm.finalize_success(trace, pipeline_metadata={"env": "test"})
    assert trace.metadata.get("metadata") == {"env": "test"}
    assert trace.status == ExecutionStatus.SUCCEEDED.value
    assert trace.finished_at is not None


def test_default_policy_hooks_are_pipeline_phase_hooks() -> None:
    policy = PolicyEnforcer()
    assert isinstance(InputPolicyHook(policy), PipelinePreHook)
    assert isinstance(OutputPolicyHook(policy), PipelinePostHook)


def test_executor_context_fields_match_trace_and_plan_metadata() -> None:
    """ExecutionContext carries run_id, plan metadata, shared trace and policy."""
    from oris.components.base import Component
    from oris.pipeline.plan import ExecutionPlan, ExecutionStep

    class Echo(Component):
        def run(self, data: dict[str, object], context: ExecutionContext) -> dict[str, object]:
            assert context.run_id == context.trace.run_id
            assert context.metadata == {"k": "v"}
            assert context.current_step_id == "only"
            assert context.step_index == 0
            assert context.policy is not None
            return dict(data)

    plan = ExecutionPlan(
        steps=[ExecutionStep(step_id="only", component=Echo(name="e", config={}))],
        metadata={"k": "v"},
    )
    from oris.runtime.executor import RuntimeExecutor

    result = RuntimeExecutor(plan, policy=PolicyEnforcer()).run({"query": "x"})
    assert result.metadata["metadata"] == {"k": "v"}


def test_pre_step_hook_sees_step_index_via_context() -> None:
    tm = TraceManager()
    trace = tm.begin_run()
    ctx = trivial_execution_context(run_id=trace.run_id)
    ctx.trace = trace
    ctx.step_index = 2
    seen: list[int | None] = []

    def pre(data: dict[str, object], context: ExecutionContext) -> dict[str, object]:
        seen.append(context.step_index)
        return dict(data)

    tm.traced_hook(
        trace,
        step_id="pre",
        component_name="pre",
        flags={"kind": "step_pre_hook"},
        data={},
        context=ctx,
        hook=CallablePreStepHook(pre),
    )
    assert seen == [2]
