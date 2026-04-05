"""Safe runner wrapper for external pipelines."""

from __future__ import annotations

from typing import Any, Protocol

from oris.core.exceptions import PipelineExecutionError
from oris.rai.policy import PolicyEnforcer


class ExternalRunnable(Protocol):
    """Protocol for framework-agnostic external runners."""

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute a pipeline and return a mapping."""


class SafeRunner:
    """Wraps an external runner with guard checks."""

    def __init__(self, external_pipeline: ExternalRunnable) -> None:
        self._external_pipeline = external_pipeline
        self._policy = PolicyEnforcer()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        self._policy.validate_input(input_data)
        result = self._external_pipeline.run(input_data)
        if not isinstance(result, dict):
            msg = "External pipeline must return a dictionary payload."
            raise PipelineExecutionError(msg)
        self._policy.validate_output(result)
        return result
