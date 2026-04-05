"""Pipeline aggregate: config-driven construction and execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from oris.components.base import Component
from oris.components.builtin import create_builtin_registry
from oris.components.registry import ComponentRegistry
from oris.rai.factory import build_default_guards
from oris.rai.policy import PolicyEnforcer
from oris.runtime.executor import PipelineExecutor
from oris.runtime.models import PipelineResult

from .builder import instantiate_components
from .loader import load_yaml_config
from .validation import validate_pipeline_config


@dataclass(slots=True)
class Pipeline:
    """Pipeline aggregate built from YAML or an in-memory config."""

    components: list[Component]
    policy_enforcer: PolicyEnforcer | None = None

    @classmethod
    def from_yaml(cls, path: str | Path, *, registry: ComponentRegistry | None = None) -> Pipeline:
        config = load_yaml_config(path)
        return cls.from_config(config, registry=registry)

    @classmethod
    def from_config(
        cls,
        config: dict[str, Any],
        *,
        registry: ComponentRegistry | None = None,
    ) -> Pipeline:
        validate_pipeline_config(config)
        reg = registry or create_builtin_registry()
        components = instantiate_components(config, reg)
        return cls(components=components)

    def run(self, input_data: dict[str, object]) -> PipelineResult:
        policy = self.policy_enforcer or PolicyEnforcer()
        input_guard, output_guard = build_default_guards(policy)
        executor = PipelineExecutor(
            components=self.components,
            input_guard=input_guard,
            output_guard=output_guard,
        )
        return executor.run(input_data)
