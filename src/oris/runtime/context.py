"""Mutable execution context for a single pipeline run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from oris.tracing.models import RunTrace

if TYPE_CHECKING:
    from oris.rai.policy import PolicyEnforcer


@dataclass
class ExecutionContext:
    """Holds run identifiers, metadata, trace, policy, and optional step scope."""

    run_id: str
    metadata: dict[str, Any]
    trace: RunTrace
    policy: PolicyEnforcer
    current_step_id: str | None = None
    step_index: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)
