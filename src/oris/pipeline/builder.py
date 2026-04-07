"""Construct component instances from validated config."""

from __future__ import annotations

from typing import Any

from oris.components.base import Component, LLMComponent
from oris.components.registry import ComponentRegistry
from oris.core.exceptions import ConfigurationError
from oris.providers.base import LLMProvider


def instantiate_components(
    config: dict[str, Any],
    registry: ComponentRegistry,
    providers_by_id: dict[str, LLMProvider],
) -> list[Component]:
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
        component_cls = registry.get(component_type)
        if issubclass(component_cls, LLMComponent):
            pid = component_config.get("provider")
            if not isinstance(pid, str) or not pid.strip():
                msg = (
                    f"Component '{name}' requires string config 'provider' "
                    "(logical provider id declared under 'providers')."
                )
                raise ConfigurationError(msg)
            pid_key = pid.strip()
            if pid_key not in providers_by_id:
                msg = f"Component '{name}' references unknown provider id '{pid_key}'."
                raise ConfigurationError(msg)
            component = registry.create(
                component_type,
                name=name,
                config=component_config,
                llm_provider=providers_by_id[pid_key],
            )
        else:
            component = registry.create(component_type, name=name, config=component_config)
        components.append(component)
    return components
