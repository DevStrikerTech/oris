"""Default component registrations (composition root helpers)."""

from __future__ import annotations

from oris.components.registry import ComponentRegistry
from oris.components.standard import (
    LLMEchoComponent,
    PassthroughComponent,
    TemplateResponseComponent,
)


def create_builtin_registry() -> ComponentRegistry:
    """Return a registry with built-in component types registered."""
    registry = ComponentRegistry()
    registry.register("passthrough", PassthroughComponent)
    registry.register("template_response", TemplateResponseComponent)
    registry.register("llm_echo", LLMEchoComponent)
    return registry
