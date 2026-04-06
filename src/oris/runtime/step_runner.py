"""Runs a single execution plan step with pre/post hooks and tracing."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from oris.pipeline.plan import ExecutionStep
from oris.runtime.context import ExecutionContext
from oris.runtime.hooks import PostStepHook, PreStepHook
from oris.runtime.orchestrator import PipelineOrchestrator
from oris.runtime.trace_manager import TraceManager


class StepRunner:
    """Per-step execution: pre hooks → component → post hooks, via TraceManager."""

    def __init__(
        self,
        orchestrator: PipelineOrchestrator,
        trace_manager: TraceManager,
    ) -> None:
        self._orchestrator = orchestrator
        self._trace_manager = trace_manager

    def run_step(
        self,
        step: ExecutionStep,
        index: int,
        total: int,
        payload: dict[str, Any],
        context: ExecutionContext,
        pre_hooks: Sequence[PreStepHook],
        post_hooks: Sequence[PostStepHook],
    ) -> dict[str, Any]:
        data = dict(payload)
        trace = context.trace
        for hook_index, pre_hook in enumerate(pre_hooks):
            step_id = f"{step.step_id}_pre_{hook_index}"
            data = self._trace_manager.traced_hook(
                trace,
                step_id=step_id,
                component_name=step_id,
                flags={
                    "kind": "step_pre_hook",
                    "step_index": index,
                    "total_steps": total,
                },
                data=data,
                context=context,
                hook=pre_hook,
            )

        flags_step: dict[str, Any] = {
            "kind": "pipeline_step",
            "step_index": index,
            "total_steps": total,
        }

        def _run_component() -> dict[str, Any]:
            return self._orchestrator.run(
                components=[step.component],
                input_data=data,
                context=context,
            )

        data = self._trace_manager.traced_component(
            trace,
            step_id=step.step_id,
            component_name=step.component.name,
            flags=flags_step,
            execute=_run_component,
        )

        for hook_index, post_hook in enumerate(post_hooks):
            step_id = f"{step.step_id}_post_{hook_index}"
            data = self._trace_manager.traced_hook(
                trace,
                step_id=step_id,
                component_name=step_id,
                flags={
                    "kind": "step_post_hook",
                    "step_index": index,
                    "total_steps": total,
                },
                data=data,
                context=context,
                hook=post_hook,
            )
        return data
