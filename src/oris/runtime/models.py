"""Runtime data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from oris.core.enums import ExecutionStatus
from oris.tracing.models import RunTrace, step_trace_to_dict


@dataclass(slots=True)
class PipelineResult:
    """Canonical pipeline output object."""

    output: dict[str, Any]
    trace: RunTrace
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_run_summary(self) -> dict[str, Any]:
        """Structured summary: run_id, status, output, and per-step trace entries."""
        ok = self.trace.status == ExecutionStatus.SUCCEEDED.value
        return {
            "run_id": self.trace.run_id,
            "status": "success" if ok else "failed",
            "output": dict(self.output),
            "trace": [
                step_trace_to_dict(step, status_success_value=ExecutionStatus.SUCCEEDED.value)
                for step in self.trace.steps
            ],
        }
