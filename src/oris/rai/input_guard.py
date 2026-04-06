"""Input guard component."""

from __future__ import annotations

from typing import Any

from oris.components.base import Component
from oris.runtime.context import ExecutionContext

from .policy import PolicyEnforcer


class InputGuard(Component):
    """Validates input payloads before component execution."""

    _policy: PolicyEnforcer

    def __init__(
        self,
        name: str = "input_guard",
        config: dict[str, Any] | None = None,
        *,
        policy: PolicyEnforcer,
    ) -> None:
        super().__init__(name=name, config=config or {})
        self._policy = policy

    def run(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        _ = context
        self._policy.validate_input(data)
        return data
