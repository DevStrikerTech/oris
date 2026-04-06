"""Orchestrates sequential component execution."""

from __future__ import annotations

from typing import Any

from oris.components.base import Component
from oris.core.exceptions import ComponentExecutionError
from oris.runtime.context import ExecutionContext


class PipelineOrchestrator:
    """Simple sequential orchestrator with explicit error wrapping."""

    def run(
        self,
        *,
        components: list[Component],
        input_data: dict[str, Any],
        context: ExecutionContext,
    ) -> dict[str, Any]:
        payload = dict(input_data)
        for component in components:
            try:
                payload = component.run(payload, context)
            except Exception as exc:  # pragma: no cover - defensive wrapper
                msg = f"Component '{component.name}' failed."
                raise ComponentExecutionError(msg) from exc
        return payload
