"""Pipeline aggregate: load config, validate, build plan, delegate execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from oris.components.builtin import create_builtin_registry
from oris.components.registry import ComponentRegistry
from oris.rai.policy import PolicyEnforcer
from oris.runtime.executor import RuntimeExecutor
from oris.runtime.models import PipelineResult

from .loader import load_yaml_config
from .plan import ExecutionPlan, build_execution_plan
from .schema import parse_pipeline_dict


@dataclass(slots=True)
class Pipeline:
    """Pipeline: YAML/config → validated plan → ``RuntimeExecutor`` (no inline execution logic)."""

    plan: ExecutionPlan
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
        parsed = parse_pipeline_dict(config)
        reg = registry or create_builtin_registry()
        plan = build_execution_plan(parsed, reg)
        return cls(plan=plan)

    def run(self, input_data: dict[str, object]) -> PipelineResult:
        policy = self.policy_enforcer or PolicyEnforcer()
        executor = RuntimeExecutor(
            plan=self.plan,
            policy=policy,
        )
        return executor.run(input_data)
