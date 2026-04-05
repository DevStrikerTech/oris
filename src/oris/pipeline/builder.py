"""Construct component instances from validated config."""

from __future__ import annotations

from typing import Any

from oris.components.base import Component
from oris.components.registry import ComponentRegistry
from oris.core.exceptions import ConfigurationError


def instantiate_components(config: dict[str, Any], registry: ComponentRegistry) -> list[Component]:
    """Create ordered component instances from a validated config mapping."""
    components: list[Component] = []
    raw_list = config["components"]
    for index, item in enumerate(raw_list):
        if not isinstance(item, dict):
            msg = f"Component at index {index} must be a mapping."
            raise ConfigurationError(msg)
        name = str(item.get("name", f"component_{index}"))
        if "type" not in item:
            msg = f"Component '{name}' is missing required 'type'."
            raise ConfigurationError(msg)
        component_type = str(item["type"])
        component_config = item.get("config", {})
        if not isinstance(component_config, dict):
            msg = f"Component '{name}' config must be a mapping."
            raise ConfigurationError(msg)
        component = registry.create(component_type, name=name, config=component_config)
        components.append(component)
    return components
