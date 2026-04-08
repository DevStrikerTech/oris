"""Execution plan: ordered steps resolved from validated pipeline config."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from oris.components.base import Component
from oris.components.registry import ComponentRegistry
from oris.providers.base import LLMProvider

from .builder import instantiate_components
from .provider_build import build_provider_instances
from .schema import ParsedPipeline, parsed_pipeline_to_build_config


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
    providers: dict[str, LLMProvider] = field(default_factory=dict)


def build_execution_plan(parsed: ParsedPipeline, registry: ComponentRegistry) -> ExecutionPlan:
    """Instantiate components from a parsed pipeline and wrap them as an execution plan."""
    config = parsed_pipeline_to_build_config(parsed)
    providers_map = build_provider_instances(config)
    step_ids = [s.step_id for s in parsed.steps]
    components = instantiate_components(
        config,
        registry,
        providers_map,
        step_ids=step_ids,
    )
    steps = [
        ExecutionStep(step_id=sid, component=component)
        for sid, component in zip(step_ids, components, strict=True)
    ]
    metadata: dict[str, Any] = {}
    if parsed.metadata:
        metadata.update(parsed.metadata)
    if parsed.name is not None:
        metadata.setdefault("pipeline_name", parsed.name)
    metadata["settings"] = {
        "device": parsed.settings.device,
        "tracing": parsed.settings.tracing,
    }
    return ExecutionPlan(steps=steps, metadata=metadata, providers=providers_map)
