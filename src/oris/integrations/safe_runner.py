"""Safe runner wrapper for external pipelines.

Uses the same ``PolicyEnforcer`` validation entry points as the default
``RuntimeExecutor`` pipeline hooks (``validate_input`` / ``validate_output``),
so policy behavior stays aligned when mixing in-framework and external runs.

Tracing is intentionally out of scope here to keep this adapter minimal; a
future enhancement could accept an optional trace sink without coupling to
``TraceManager``.
"""

from __future__ import annotations

from typing import Any, Protocol

from oris.core.exceptions import PipelineExecutionError
from oris.rai.policy import PolicyEnforcer


class ExternalRunnable(Protocol):
    """Protocol for framework-agnostic external runners."""

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute a pipeline and return a mapping."""


class SafeRunner:
    """Wraps an external runner with the same policy checks as pipeline execution."""

    def __init__(self, external_pipeline: ExternalRunnable, *, policy: PolicyEnforcer) -> None:
        self._external_pipeline = external_pipeline
        self._policy = policy

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        self._policy.validate_input(input_data)
        result = self._external_pipeline.run(input_data)
        if not isinstance(result, dict):
            msg = "External pipeline must return a dictionary payload."
            raise PipelineExecutionError(msg)
        self._policy.validate_output(result)
        return result
