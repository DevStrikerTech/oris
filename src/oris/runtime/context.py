"""Mutable execution context for a single pipeline run.

``ExecutionContext`` is intentionally small: run identity, plan metadata, shared
``RunTrace`` and ``PolicyEnforcer``, and the current step pointer updated by the
executor. Do not use it as a generic bag for arbitrary runtime state; pass
explicit parameters or extend ``metadata`` with documented keys if needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from oris.tracing.models import RunTrace

if TYPE_CHECKING:
    from oris.rai.policy import PolicyEnforcer


@dataclass(slots=True)
class ExecutionContext:
    """Scoped state for one pipeline run (executor, components, hooks share one instance)."""

    run_id: str
    metadata: dict[str, Any]
    trace: RunTrace
    policy: PolicyEnforcer
    current_step_id: str | None = None
    step_index: int | None = None
