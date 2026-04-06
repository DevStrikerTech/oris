"""Default RAI guard construction (used at composition boundaries)."""

from __future__ import annotations

from oris.components.base import Component
from oris.rai.input_guard import InputGuard
from oris.rai.output_guard import OutputGuard
from oris.rai.policy import PolicyEnforcer


def build_default_guards(
    policy: PolicyEnforcer,
) -> tuple[Component, Component]:
    """Return input and output guard components sharing one policy instance."""
    return (
        InputGuard(policy=policy),
        OutputGuard(policy=policy),
    )
