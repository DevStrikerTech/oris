"""Centralized run and step trace creation and updates."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import uuid4

from oris.core.enums import ExecutionStatus
from oris.runtime.context import ExecutionContext
from oris.tracing.models import RunTrace, StepTrace, utc_now


def _latency_ms(started_at: datetime, finished_at: datetime) -> float:
    return (finished_at - started_at).total_seconds() * 1000.0


class TraceManager:
    """Owns RunTrace lifecycle and uniform StepTrace appends (latency, flags, metadata)."""

    def begin_run(self) -> RunTrace:
        """Create a new run trace in RUNNING state."""
        return RunTrace(
            run_id=str(uuid4()),
            started_at=utc_now(),
            status=ExecutionStatus.RUNNING.value,
        )

    def append_step(
        self,
        trace: RunTrace,
        *,
        step_id: str,
        component_name: str,
        started_at: datetime,
        finished_at: datetime,
        status: str,
        flags: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Append one step record; ``flags`` should set ``kind`` (e.g. pipeline_hook)."""
        meta = dict(metadata) if metadata else {}
        trace.steps.append(
            StepTrace(
                step_id=step_id,
                component_name=component_name,
                started_at=started_at,
                finished_at=finished_at,
                status=status,
                latency_ms=_latency_ms(started_at, finished_at),
                flags=dict(flags),
                metadata=meta,
            ),
        )

    def finalize_success(self, trace: RunTrace) -> None:
        trace.status = ExecutionStatus.SUCCEEDED.value
        trace.finished_at = utc_now()

    def finalize_failure(self, trace: RunTrace) -> None:
        trace.status = ExecutionStatus.FAILED.value
        trace.finished_at = utc_now()

    def traced_hook(
        self,
        trace: RunTrace,
        *,
        step_id: str,
        component_name: str,
        flags: dict[str, Any],
        data: dict[str, Any],
        context: ExecutionContext,
        fn: Callable[[dict[str, Any], ExecutionContext], dict[str, Any]],
    ) -> dict[str, Any]:
        """Run ``fn(data, context)`` and record a single step trace (success or failure)."""
        started_at = utc_now()
        try:
            result = dict(fn(data, context))
            finished_at = utc_now()
            self.append_step(
                trace,
                step_id=step_id,
                component_name=component_name,
                started_at=started_at,
                finished_at=finished_at,
                status=ExecutionStatus.SUCCEEDED.value,
                flags=flags,
            )
            return result
        except Exception:
            finished_at = utc_now()
            self.append_step(
                trace,
                step_id=step_id,
                component_name=component_name,
                started_at=started_at,
                finished_at=finished_at,
                status=ExecutionStatus.FAILED.value,
                flags=flags,
            )
            raise
