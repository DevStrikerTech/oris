"""Pipeline executor with mandatory RAI guards, optional hooks, and tracing."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any
from uuid import uuid4

from oris.components.base import Component
from oris.core.enums import ExecutionStatus
from oris.core.exceptions import PipelineExecutionError
from oris.runtime.models import PipelineResult
from oris.runtime.orchestrator import PipelineOrchestrator
from oris.tracing.audit import AuditLogger
from oris.tracing.models import RunTrace, StepTrace, utc_now


def _latency_ms(started_at: datetime, finished_at: datetime) -> float:
    return (finished_at - started_at).total_seconds() * 1000.0


class PipelineExecutor:
    """Executes a pipeline in sequence with mandatory guard components."""

    def __init__(
        self,
        components: list[Component],
        *,
        input_guard: Component,
        output_guard: Component,
        orchestrator: PipelineOrchestrator | None = None,
        audit_logger: AuditLogger | None = None,
        rai_pre_hooks: Sequence[Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
        rai_post_hooks: Sequence[Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
    ) -> None:
        self._components = components
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
        self._audit_logger.log_event("pipeline_started", {"run_id": run_trace.run_id})

        try:
            guarded_input = self._apply_guard(
                self._input_guard,
                dict(input_data),
                run_trace.steps,
                flags={"kind": "rai_input"},
            )
            after_pre = self._apply_hook_chain(
                guarded_input, self._rai_pre_hooks, run_trace.steps, hook_prefix="rai_pre_hook"
            )
            output = self._execute_components(after_pre, run_trace.steps)
            after_post = self._apply_hook_chain(
                output, self._rai_post_hooks, run_trace.steps, hook_prefix="rai_post_hook"
            )
            guarded_output = self._apply_guard(
                self._output_guard,
                after_post,
                run_trace.steps,
                flags={"kind": "rai_output"},
            )
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
        self._audit_logger.log_event("pipeline_succeeded", {"run_id": run_trace.run_id})

        return PipelineResult(output=guarded_output, trace=run_trace)

    def _apply_guard(
        self,
        guard: Component,
        payload: dict[str, Any],
        step_traces: list[StepTrace],
        *,
        flags: dict[str, Any],
    ) -> dict[str, Any]:
        started_at = utc_now()
        try:
            result = guard.run(payload)
        except Exception:
            finished_at = utc_now()
            step_traces.append(
                StepTrace(
                    component_name=guard.name,
                    started_at=started_at,
                    finished_at=finished_at,
                    status=ExecutionStatus.FAILED.value,
                    latency_ms=_latency_ms(started_at, finished_at),
                    flags=dict(flags),
                )
            )
            raise
        finished_at = utc_now()
        step_traces.append(
            StepTrace(
                component_name=guard.name,
                started_at=started_at,
                finished_at=finished_at,
                status=ExecutionStatus.SUCCEEDED.value,
                latency_ms=_latency_ms(started_at, finished_at),
                flags=dict(flags),
            )
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
            name = f"{hook_prefix}_{index}"
            started_at = utc_now()
            try:
                current = dict(hook(current))
            except Exception:
                finished_at = utc_now()
                step_traces.append(
                    StepTrace(
                        component_name=name,
                        started_at=started_at,
                        finished_at=finished_at,
                        status=ExecutionStatus.FAILED.value,
                        latency_ms=_latency_ms(started_at, finished_at),
                        flags={"kind": "rai_hook"},
                    )
                )
                raise
            finished_at = utc_now()
            step_traces.append(
                StepTrace(
                    component_name=name,
                    started_at=started_at,
                    finished_at=finished_at,
                    status=ExecutionStatus.SUCCEEDED.value,
                    latency_ms=_latency_ms(started_at, finished_at),
                    flags={"kind": "rai_hook"},
                )
            )
        return current

    def _execute_components(
        self,
        input_data: dict[str, Any],
        step_traces: list[StepTrace],
    ) -> dict[str, Any]:
        payload = dict(input_data)
        for component in self._components:
            started_at = utc_now()
            try:
                payload = self._orchestrator.run(components=[component], input_data=payload)
            except Exception:
                finished_at = utc_now()
                step_traces.append(
                    StepTrace(
                        component_name=component.name,
                        started_at=started_at,
                        finished_at=finished_at,
                        status=ExecutionStatus.FAILED.value,
                        latency_ms=_latency_ms(started_at, finished_at),
                        flags={"kind": "pipeline_step"},
                    )
                )
                raise
            finished_at = utc_now()
            step_traces.append(
                StepTrace(
                    component_name=component.name,
                    started_at=started_at,
                    finished_at=finished_at,
                    status=ExecutionStatus.SUCCEEDED.value,
                    latency_ms=_latency_ms(started_at, finished_at),
                    flags={"kind": "pipeline_step"},
                )
            )
        return payload
