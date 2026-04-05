"""Input guard component."""

from __future__ import annotations

from typing import Any

from oris.components.base import Component

from .policy import PolicyEnforcer


class InputGuard(Component):
    """Validates input payloads before component execution."""

    _policy: PolicyEnforcer

    def __init__(
        self,
        name: str = "input_guard",
        config: dict[str, Any] | None = None,
        *,
        policy: PolicyEnforcer | None = None,
    ) -> None:
        super().__init__(name=name, config=config or {})
        self._policy = policy or PolicyEnforcer()

    def run(self, data: dict[str, Any]) -> dict[str, Any]:
        self._policy.validate_input(data)
        return data
