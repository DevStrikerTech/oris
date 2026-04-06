"""Runtime executor: sequential steps, hooks-based RAI, tracing, and context."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from oris.core.exceptions import PipelineExecutionError
from oris.pipeline.plan import ExecutionPlan
from oris.rai.hooks import InputPolicyHook, OutputPolicyHook
from oris.rai.policy import PolicyEnforcer
from oris.runtime.context import ExecutionContext
from oris.runtime.hooks import (
    Hook,
    PipelinePostHookLike,
    PipelinePreHookLike,
    PostStepHookLike,
    PreStepHookLike,
    as_pipeline_post_hook,
    as_pipeline_pre_hook,
    as_post_step_hook,
    as_pre_step_hook,
)
from oris.runtime.models import PipelineResult
from oris.runtime.orchestrator import PipelineOrchestrator
from oris.runtime.step_runner import StepRunner
from oris.runtime.trace_manager import TraceManager
from oris.tracing.audit import AuditLogger

HookWithTrace = tuple[Hook, dict[str, Any]]


class RuntimeExecutor:
    """Core engine: executes an ``ExecutionPlan`` with hooks, tracing, and policy on context."""

    def __init__(
        self,
        plan: ExecutionPlan,
        *,
        policy: PolicyEnforcer | None = None,
        orchestrator: PipelineOrchestrator | None = None,
        audit_logger: AuditLogger | None = None,
        trace_manager: TraceManager | None = None,
        pipeline_pre_hooks: Sequence[PipelinePreHookLike] | None = None,
        pipeline_post_hooks: Sequence[PipelinePostHookLike] | None = None,
        rai_pre_hooks: Sequence[PipelinePreHookLike] | None = None,
        rai_post_hooks: Sequence[PipelinePostHookLike] | None = None,
        pre_step_hooks: Sequence[PreStepHookLike] | None = None,
        post_step_hooks: Sequence[PostStepHookLike] | None = None,
    ) -> None:
        self._plan = plan
        self._policy = policy or PolicyEnforcer()
        self._orchestrator = orchestrator or PipelineOrchestrator()
        self._audit_logger = audit_logger or AuditLogger()
        self._trace_manager = trace_manager or TraceManager()
        self._step_runner = StepRunner(self._orchestrator, self._trace_manager)
        self._pre_step_hooks = tuple(as_pre_step_hook(h) for h in (pre_step_hooks or ()))
        self._post_step_hooks = tuple(as_post_step_hook(h) for h in (post_step_hooks or ()))

        self._pipeline_pre_specs: list[HookWithTrace] = []
        if pipeline_pre_hooks is not None:
            for j, pre_hook in enumerate(pipeline_pre_hooks):
                flags = {"kind": "pipeline_hook", "phase": "pre", "index": j}
                self._pipeline_pre_specs.append((as_pipeline_pre_hook(pre_hook), flags))
        else:
            self._pipeline_pre_specs.append(
                (
                    InputPolicyHook(self._policy),
                    {"kind": "pipeline_hook", "phase": "pre", "index": 0},
                ),
            )
            for j, rai_pre in enumerate(rai_pre_hooks or ()):
                flags = {"kind": "rai_hook", "phase": "pre", "index": j}
                self._pipeline_pre_specs.append((as_pipeline_pre_hook(rai_pre), flags))

        self._pipeline_post_specs: list[HookWithTrace] = []
        if pipeline_post_hooks is not None:
            for j, post_hook in enumerate(pipeline_post_hooks):
                flags = {"kind": "pipeline_hook", "phase": "post", "index": j}
                self._pipeline_post_specs.append((as_pipeline_post_hook(post_hook), flags))
        else:
            rai_post = tuple(rai_post_hooks or ())
            for j, rai_post_hook in enumerate(rai_post):
                flags = {"kind": "rai_hook", "phase": "post", "index": j}
                self._pipeline_post_specs.append((as_pipeline_post_hook(rai_post_hook), flags))
            self._pipeline_post_specs.append(
                (
                    OutputPolicyHook(self._policy),
                    {
                        "kind": "pipeline_hook",
                        "phase": "post",
                        "index": len(rai_post),
                    },
                ),
            )

    def run(self, input_data: dict[str, object]) -> PipelineResult:
        trace = self._trace_manager.begin_run()
        policy = self._policy
        context = ExecutionContext(
            run_id=trace.run_id,
            metadata=dict(self._plan.metadata),
            trace=trace,
            policy=policy,
        )
        self._audit_logger.log_event("pipeline_started", {"run_id": trace.run_id})

        try:
            payload: dict[str, Any] = dict(input_data)
            for index, (hook, flags) in enumerate(self._pipeline_pre_specs):
                payload = self._trace_manager.traced_hook(
                    trace,
                    step_id=f"pipeline_pre_{index}",
                    component_name=f"pipeline_pre_{index}",
                    flags=dict(flags),
                    data=payload,
                    context=context,
                    hook=hook,
                )

            steps = self._plan.steps
            for index, step in enumerate(steps):
                context.current_step_id = step.step_id
                context.step_index = index
                payload = self._step_runner.run_step(
                    step,
                    index,
                    len(steps),
                    payload,
                    context,
                    self._pre_step_hooks,
                    self._post_step_hooks,
                )

            context.current_step_id = None
            context.step_index = None

            for index, (hook, flags) in enumerate(self._pipeline_post_specs):
                payload = self._trace_manager.traced_hook(
                    trace,
                    step_id=f"pipeline_post_{index}",
                    component_name=f"pipeline_post_{index}",
                    flags=dict(flags),
                    data=payload,
                    context=context,
                    hook=hook,
                )

            self._trace_manager.finalize_success(trace, pipeline_metadata=dict(context.metadata))
            self._audit_logger.log_event("pipeline_succeeded", {"run_id": trace.run_id})

            return PipelineResult(
                output=payload,
                trace=trace,
                metadata={
                    "run_id": context.run_id,
                    "metadata": dict(context.metadata),
                },
            )
        except Exception as exc:
            self._trace_manager.finalize_failure(trace)
            self._audit_logger.log_event(
                "pipeline_failed",
                {"run_id": trace.run_id, "error_type": type(exc).__name__},
            )
            if isinstance(exc, PipelineExecutionError):
                raise
            msg = "Pipeline execution failed."
            raise PipelineExecutionError(msg) from exc


PipelineExecutor = RuntimeExecutor
