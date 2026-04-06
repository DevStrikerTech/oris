"""Execution plan: ordered steps resolved from validated pipeline config."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from oris.components.base import Component
from oris.components.registry import ComponentRegistry

from .builder import instantiate_components


@dataclass(slots=True)
class ExecutionStep:
    """One pipeline step: stable id and resolved component instance."""

    step_id: str
    component: Component


@dataclass(slots=True)
class ExecutionPlan:
    """Ordered steps and pipeline-level metadata (no execution logic)."""

    steps: list[ExecutionStep]
    metadata: dict[str, Any] = field(default_factory=dict)


def build_execution_plan(config: dict[str, Any], registry: ComponentRegistry) -> ExecutionPlan:
    """Instantiate components from config and wrap them as an execution plan."""
    components = instantiate_components(config, registry)
    steps = [
        ExecutionStep(step_id=f"step_{index}", component=component)
        for index, component in enumerate(components)
    ]
    metadata: dict[str, Any] = {}
    raw_meta = config.get("metadata")
    if isinstance(raw_meta, dict):
        metadata.update(raw_meta)
    name = config.get("name")
    if name is not None:
        metadata.setdefault("pipeline_name", name)
    return ExecutionPlan(steps=steps, metadata=metadata)
