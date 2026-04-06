"""Default RAI behavior as pipeline hooks (policy validation)."""

from __future__ import annotations

from typing import Any

from oris.rai.policy import PolicyEnforcer
from oris.runtime.context import ExecutionContext


class InputPolicyHook:
    """Pipeline pre-hook: ``policy.validate_input``."""

    __slots__ = ("_policy",)

    def __init__(self, policy: PolicyEnforcer) -> None:
        self._policy = policy

    def __call__(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        _ = context
        self._policy.validate_input(data)
        return data


class OutputPolicyHook:
    """Pipeline post-hook: ``policy.validate_output``."""

    __slots__ = ("_policy",)

    def __init__(self, policy: PolicyEnforcer) -> None:
        self._policy = policy

    def __call__(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        _ = context
        self._policy.validate_output(data)
        return data
