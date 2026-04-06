"""Shared helpers for Oris tests."""

from __future__ import annotations

from typing import Any

from oris.rai.policy import PolicyEnforcer
from oris.runtime.context import ExecutionContext
from oris.tracing.models import RunTrace, utc_now


def trivial_execution_context(
    *,
    policy: PolicyEnforcer | None = None,
    run_id: str = "test-run",
    metadata: dict[str, Any] | None = None,
) -> ExecutionContext:
    p = policy or PolicyEnforcer()
    trace = RunTrace(run_id=run_id, started_at=utc_now())
    return ExecutionContext(
        run_id=run_id,
        metadata=dict(metadata or {}),
        trace=trace,
        policy=p,
    )
