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
    *,
    step_ids: list[str] | None = None,
) -> list[Component]:
    """Create ordered component instances from a validated config mapping."""
    raw_list = config.get("components")
    if not isinstance(raw_list, list):
        msg = "Invalid pipeline config: expected a 'components' list for instantiation."
        raise ConfigurationError(msg)
    components: list[Component] = []
    declared = ", ".join(sorted(providers_by_id.keys())) if providers_by_id else "(none)"
    for index, item in enumerate(raw_list):
        if not isinstance(item, dict):
            sid = step_ids[index] if step_ids and index < len(step_ids) else f"step_{index}"
            msg = f"Invalid pipeline config: step '{sid}' must be a mapping."
            raise ConfigurationError(msg)
        name = str(item.get("name", f"component_{index}"))
        trace_step = step_ids[index] if step_ids is not None and index < len(step_ids) else name
        if "type" not in item:
            msg = f"Invalid pipeline config: missing required field 'type' for step '{trace_step}'."
            raise ConfigurationError(msg)
        component_type = str(item["type"])
        component_config = item.get("config", {})
        if component_config is None:
            component_config = {}
        if not isinstance(component_config, dict):
            msg = (
                f"Invalid pipeline config: 'config' for step '{trace_step}' "
                f"(component '{name}') must be a mapping."
            )
            raise ConfigurationError(msg)
        try:
            component_cls = registry.get(component_type)
        except ConfigurationError as exc:
            msg = f"Invalid pipeline config: step '{trace_step}' ({exc})"
            raise ConfigurationError(msg) from exc
        if issubclass(component_cls, LLMComponent):
            pid = component_config.get("provider")
            if not isinstance(pid, str) or not pid.strip():
                msg = (
                    f"Invalid pipeline config: step '{trace_step}' (component '{name}', "
                    "type requires a string 'provider' in config referencing "
                    "a logical id under top-level 'providers')."
                )
                raise ConfigurationError(msg)
            pid_key = pid.strip()
            if pid_key not in providers_by_id:
                msg = (
                    f"Invalid pipeline config: step '{trace_step}' references unknown "
                    f"provider '{pid_key}' (declared providers: {declared})."
                )
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
