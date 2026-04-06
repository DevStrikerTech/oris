"""Runtime executor: sequential steps, mandatory RAI, tracing, and context."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any
from uuid import uuid4

from oris.components.base import Component
from oris.core.enums import ExecutionStatus
from oris.core.exceptions import PipelineExecutionError
from oris.pipeline.plan import ExecutionPlan, ExecutionStep
from oris.runtime.context import ExecutionContext
from oris.runtime.models import PipelineResult
from oris.runtime.orchestrator import PipelineOrchestrator
from oris.tracing.audit import AuditLogger
from oris.tracing.models import RunTrace, StepTrace, utc_now


def _latency_ms(started_at: datetime, finished_at: datetime) -> float:
    return (finished_at - started_at).total_seconds() * 1000.0


def _append_step_trace(
    traces: list[StepTrace],
    *,
    step_id: str,
    component_name: str,
    started_at: datetime,
    finished_at: datetime,
    status: str,
    flags: dict[str, Any],
) -> None:
    traces.append(
        StepTrace(
            step_id=step_id,
            component_name=component_name,
            started_at=started_at,
            finished_at=finished_at,
            status=status,
            latency_ms=_latency_ms(started_at, finished_at),
            flags=dict(flags),
        ),
    )


class RuntimeExecutor:
    """Core engine: executes an ``ExecutionPlan`` sequentially with mandatory RAI and tracing."""

    def __init__(
        self,
        plan: ExecutionPlan,
        *,
        input_guard: Component,
        output_guard: Component,
        orchestrator: PipelineOrchestrator | None = None,
        audit_logger: AuditLogger | None = None,
        rai_pre_hooks: Sequence[Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
        rai_post_hooks: Sequence[Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
    ) -> None:
        self._plan = plan
        self._input_guard = input_guard
        self._output_guard = output_guard
        self._orchestrator = orchestrator or PipelineOrchestrator()
        self._audit_logger = audit_logger or AuditLogger()
        self._rai_pre_hooks = tuple(rai_pre_hooks or ())
        self._rai_post_hooks = tuple(rai_post_hooks or ())

    def run(self, input_data: dict[str, object]) -> PipelineResult:
        run_trace = RunTrace(
            run_id=str(uuid4()),
            started_at=utc_now(),
            status=ExecutionStatus.RUNNING.value,
        )
        context = ExecutionContext(
            run_id=run_trace.run_id,
            pipeline_metadata=dict(self._plan.metadata),
            run_trace=run_trace,
        )
        self._audit_logger.log_event("pipeline_started", {"run_id": run_trace.run_id})

        try:
            payload: dict[str, Any] = dict(input_data)
            payload = self._run_input_guard(payload, run_trace.steps)
            payload = self._apply_hook_chain(
                payload,
                self._rai_pre_hooks,
                run_trace.steps,
                hook_prefix="rai_pre_hook",
            )
            payload = self._execute_plan_steps(payload, run_trace.steps)
            payload = self._apply_hook_chain(
                payload,
                self._rai_post_hooks,
                run_trace.steps,
                hook_prefix="rai_post_hook",
            )
            payload = self._run_output_guard(payload, run_trace.steps)
        except Exception as exc:
            run_trace.status = ExecutionStatus.FAILED.value
            run_trace.finished_at = utc_now()
            self._audit_logger.log_event(
                "pipeline_failed",
                {"run_id": run_trace.run_id, "error_type": type(exc).__name__},
            )
            if isinstance(exc, PipelineExecutionError):
                raise
            msg = "Pipeline execution failed."
            raise PipelineExecutionError(msg) from exc

        run_trace.status = ExecutionStatus.SUCCEEDED.value
        run_trace.finished_at = utc_now()
        run_trace.metadata.setdefault("pipeline_metadata", dict(context.pipeline_metadata))
        self._audit_logger.log_event("pipeline_succeeded", {"run_id": run_trace.run_id})

        return PipelineResult(
            output=payload,
            trace=run_trace,
            metadata={
                "run_id": context.run_id,
                "pipeline_metadata": dict(context.pipeline_metadata),
            },
        )

    def _run_input_guard(
        self,
        payload: dict[str, Any],
        step_traces: list[StepTrace],
    ) -> dict[str, Any]:
        return self._run_guard_component(
            self._input_guard,
            payload,
            step_traces,
            step_id="rai_input",
            flags={"kind": "rai_input"},
        )

    def _run_output_guard(
        self,
        payload: dict[str, Any],
        step_traces: list[StepTrace],
    ) -> dict[str, Any]:
        return self._run_guard_component(
            self._output_guard,
            payload,
            step_traces,
            step_id="rai_output",
            flags={"kind": "rai_output"},
        )

    def _run_guard_component(
        self,
        guard: Component,
        payload: dict[str, Any],
        step_traces: list[StepTrace],
        *,
        step_id: str,
        flags: dict[str, Any],
    ) -> dict[str, Any]:
        started_at = utc_now()
        try:
            result = guard.run(payload)
        except Exception:
            finished_at = utc_now()
            _append_step_trace(
                step_traces,
                step_id=step_id,
                component_name=guard.name,
                started_at=started_at,
                finished_at=finished_at,
                status=ExecutionStatus.FAILED.value,
                flags=flags,
            )
            raise
        finished_at = utc_now()
        _append_step_trace(
            step_traces,
            step_id=step_id,
            component_name=guard.name,
            started_at=started_at,
            finished_at=finished_at,
            status=ExecutionStatus.SUCCEEDED.value,
            flags=flags,
        )
        return result

    def _apply_hook_chain(
        self,
        payload: dict[str, Any],
        hooks: tuple[Callable[[dict[str, Any]], dict[str, Any]], ...],
        step_traces: list[StepTrace],
        *,
        hook_prefix: str,
    ) -> dict[str, Any]:
        current = dict(payload)
        for index, hook in enumerate(hooks):
            step_id = f"{hook_prefix}_{index}"
            name = step_id
            started_at = utc_now()
            try:
                current = dict(hook(current))
            except Exception:
                finished_at = utc_now()
                _append_step_trace(
                    step_traces,
                    step_id=step_id,
                    component_name=name,
                    started_at=started_at,
                    finished_at=finished_at,
                    status=ExecutionStatus.FAILED.value,
                    flags={"kind": "rai_hook"},
                )
                raise
            finished_at = utc_now()
            _append_step_trace(
                step_traces,
                step_id=step_id,
                component_name=name,
                started_at=started_at,
                finished_at=finished_at,
                status=ExecutionStatus.SUCCEEDED.value,
                flags={"kind": "rai_hook"},
            )
        return current

    def _execute_plan_steps(
        self,
        input_data: dict[str, Any],
        step_traces: list[StepTrace],
    ) -> dict[str, Any]:
        payload = dict(input_data)
        steps = self._plan.steps
        for index, step in enumerate(steps):
            payload = self._run_pipeline_step(step, index, len(steps), payload, step_traces)
        return payload

    def _run_pipeline_step(
        self,
        step: ExecutionStep,
        index: int,
        total: int,
        payload: dict[str, Any],
        step_traces: list[StepTrace],
    ) -> dict[str, Any]:
        component = step.component
        started_at = utc_now()
        flags: dict[str, Any] = {"kind": "pipeline_step", "step_index": index, "total_steps": total}
        try:
            payload = self._orchestrator.run(components=[component], input_data=payload)
        except Exception:
            finished_at = utc_now()
            _append_step_trace(
                step_traces,
                step_id=step.step_id,
                component_name=component.name,
                started_at=started_at,
                finished_at=finished_at,
                status=ExecutionStatus.FAILED.value,
                flags=flags,
            )
            raise
        finished_at = utc_now()
        _append_step_trace(
            step_traces,
            step_id=step.step_id,
            component_name=component.name,
            started_at=started_at,
            finished_at=finished_at,
            status=ExecutionStatus.SUCCEEDED.value,
            flags=flags,
        )
        return payload


PipelineExecutor = RuntimeExecutor
