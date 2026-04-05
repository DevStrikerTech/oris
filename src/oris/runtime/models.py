"""Runtime data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from oris.tracing.models import RunTrace


@dataclass(slots=True)
class PipelineResult:
    """Canonical pipeline output object."""

    output: dict[str, Any]
    trace: RunTrace
    metadata: dict[str, Any] = field(default_factory=dict)
