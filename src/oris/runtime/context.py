"""Mutable execution context for a single pipeline run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from oris.tracing.models import RunTrace


@dataclass
class ExecutionContext:
    """Holds run identifiers, pipeline metadata, and the live run trace."""

    run_id: str
    pipeline_metadata: dict[str, Any]
    run_trace: RunTrace
    extra: dict[str, Any] = field(default_factory=dict)
