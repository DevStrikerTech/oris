"""Policy logic for responsible input/output filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from oris.core.exceptions import GuardViolationError


@dataclass(slots=True)
class PolicyEnforcer:
    """Simple policy enforcer for blocked keys and terms."""

    blocked_input_keys: set[str] = field(default_factory=lambda: {"password", "secret", "token"})
    blocked_terms: set[str] = field(default_factory=lambda: {"exploit", "malware"})

    def validate_input(self, data: dict[str, Any]) -> None:
        for key in data:
            if key.lower() in self.blocked_input_keys:
                msg = f"Input contains prohibited key '{key}'."
                raise GuardViolationError(msg)

    def validate_output(self, data: dict[str, Any]) -> None:
        for value in data.values():
            if isinstance(value, str):
                lowered = value.lower()
                if any(term in lowered for term in self.blocked_terms):
                    msg = "Output contains blocked policy terms."
                    raise GuardViolationError(msg)
