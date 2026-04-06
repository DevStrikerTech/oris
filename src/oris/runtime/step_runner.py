"""Runs a single execution plan step with pre/post hooks and tracing."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from oris.core.enums import ExecutionStatus
from oris.pipeline.plan import ExecutionStep
from oris.runtime.context import ExecutionContext
from oris.runtime.hooks import PostExecutionHook, PreExecutionHook
from oris.runtime.orchestrator import PipelineOrchestrator
from oris.runtime.trace_manager import TraceManager
from oris.tracing.models import utc_now


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
        pre_hooks: Sequence[PreExecutionHook],
        post_hooks: Sequence[PostExecutionHook],
    ) -> dict[str, Any]:
        data = dict(payload)
        trace = context.trace
        for hook_index, hook in enumerate(pre_hooks):
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
                fn=hook,
            )

        flags_step: dict[str, Any] = {
            "kind": "pipeline_step",
            "step_index": index,
            "total_steps": total,
        }
        started_at = utc_now()
        try:
            data = self._orchestrator.run(
                components=[step.component],
                input_data=data,
                context=context,
            )
        except Exception:
            finished_at = utc_now()
            self._trace_manager.append_step(
                trace,
                step_id=step.step_id,
                component_name=step.component.name,
                started_at=started_at,
                finished_at=finished_at,
                status=ExecutionStatus.FAILED.value,
                flags=flags_step,
            )
            raise
        finished_at = utc_now()
        self._trace_manager.append_step(
            trace,
            step_id=step.step_id,
            component_name=step.component.name,
            started_at=started_at,
            finished_at=finished_at,
            status=ExecutionStatus.SUCCEEDED.value,
            flags=flags_step,
        )

        for hook_index, hook in enumerate(post_hooks):
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
                fn=hook,
            )
        return data
