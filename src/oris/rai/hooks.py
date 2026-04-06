"""Default RAI behavior as pipeline hooks (policy validation)."""

from __future__ import annotations

from typing import Any

from oris.rai.policy import PolicyEnforcer
from oris.runtime.context import ExecutionContext
from oris.runtime.hooks import PipelinePostHook, PipelinePreHook


class InputPolicyHook(PipelinePreHook):
    """Pipeline pre-hook: ``policy.validate_input``."""

    __slots__ = ("_policy",)

    def __init__(self, policy: PolicyEnforcer) -> None:
        self._policy = policy

    def invoke(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        _ = context
        self._policy.validate_input(data)
        return data


class OutputPolicyHook(PipelinePostHook):
    """Pipeline post-hook: ``policy.validate_output``."""

    __slots__ = ("_policy",)

    def __init__(self, policy: PolicyEnforcer) -> None:
        self._policy = policy

    def invoke(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        _ = context
        self._policy.validate_output(data)
        return data
