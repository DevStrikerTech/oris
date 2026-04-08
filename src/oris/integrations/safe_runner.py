"""Safe runner wrapper for external pipelines.

Uses the same ``PolicyEnforcer`` validation entry points as the default
``RuntimeExecutor`` pipeline hooks (``validate_input`` / ``validate_output``),
so policy behavior stays aligned when mixing in-framework and external runs.

Accepts a callable ``(dict) -> Any`` or an object with ``run(dict) -> Any``.
Return values are coerced to ``dict[str, Any]`` when they are ``dict``-like
or expose a duck-typed ``model_dump()`` returning a mapping.

Optional tracing reuses ``TraceManager.traced_component`` for a single external
step (status, flags, latency) without changing core executor behavior.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, Protocol, overload

from oris.core.exceptions import PipelineExecutionError
from oris.rai.policy import PolicyEnforcer
from oris.runtime.models import PipelineResult
from oris.runtime.trace_manager import TraceManager


class ExternalRunnable(Protocol):
    """Protocol for framework-agnostic external runners."""

    def run(self, input_data: dict[str, Any]) -> Any:
        """Execute a pipeline and return a mapping or mapping-like result."""


def _coerce_input(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        return dict(data)
    if isinstance(data, Mapping):
        return dict(data)
    msg = "Input must be a dictionary-compatible mapping."
    raise PipelineExecutionError(msg)


def _coerce_output(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return dict(result)
    if isinstance(result, Mapping):
        return dict(result)
    model_dump = getattr(result, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, Mapping):
            return dict(dumped)
    msg = "External pipeline must return a dictionary-compatible payload."
    raise PipelineExecutionError(msg)


_EXTERNAL_FLAGS: dict[str, Any] = {"kind": "external_pipeline"}
_EXTERNAL_STEP_ID = "external_pipeline"


class SafeRunner:
    """Wraps an external runner with the same policy checks as pipeline execution."""

    def __init__(self, external_pipeline: object, *, policy: PolicyEnforcer) -> None:
        self._external_pipeline = external_pipeline
        self._policy = policy

    def _dispatch(self, inp: dict[str, Any]) -> Any:
        target = self._external_pipeline
        run_method = getattr(target, "run", None)
        if run_method is not None and callable(run_method):
            return run_method(inp)
        if callable(target):
            return target(inp)
        msg = "External target must be callable or provide a run(dict) method."
        raise PipelineExecutionError(msg)

    def _execute_body(self, inp: dict[str, Any]) -> dict[str, Any]:
        self._policy.validate_input(inp)
        try:
            raw = self._dispatch(inp)
        except Exception as exc:
            if isinstance(exc, PipelineExecutionError):
                raise
            raise PipelineExecutionError("External pipeline execution failed.") from None
        normalized = _coerce_output(raw)
        self._policy.validate_output(normalized)
        return normalized

    @overload
    def run(
        self,
        input_data: dict[str, Any],
        *,
        include_trace: Literal[False] = False,
    ) -> dict[str, Any]: ...

    @overload
    def run(
        self,
        input_data: dict[str, Any],
        *,
        include_trace: Literal[True],
    ) -> PipelineResult: ...

    def run(
        self,
        input_data: dict[str, Any],
        *,
        include_trace: bool = False,
    ) -> dict[str, Any] | PipelineResult:
        inp = _coerce_input(input_data)
        if not include_trace:
            return self._execute_body(inp)

        trace_manager = TraceManager()
        trace = trace_manager.begin_run()
        try:

            def execute() -> dict[str, Any]:
                return self._execute_body(inp)

            output = trace_manager.traced_component(
                trace,
                step_id=_EXTERNAL_STEP_ID,
                component_name=_EXTERNAL_STEP_ID,
                flags=_EXTERNAL_FLAGS,
                execute=execute,
            )
            trace_manager.finalize_success(
                trace,
                pipeline_metadata={"source": "external"},
            )
        except Exception:
            trace_manager.finalize_failure(trace)
            raise

        return PipelineResult(
            output=output,
            trace=trace,
            metadata={
                "run_id": trace.run_id,
                "source": "external",
            },
        )
