"""Trace models for pipeline observability."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class StepTrace:
    """Execution trace data for one component step."""

    component_name: str
    started_at: datetime
    finished_at: datetime
    status: str
    latency_ms: float = 0.0
    flags: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RunTrace:
    """Top-level trace for a pipeline run."""

    run_id: str
    started_at: datetime
    finished_at: datetime | None = None
    status: str = "pending"
    steps: list[StepTrace] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
