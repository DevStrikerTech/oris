"""Component registry for dynamic pipeline construction."""

from __future__ import annotations

from typing import Any

from oris.core.exceptions import ConfigurationError
from oris.providers.base import LLMProvider

from .base import Component, LLMComponent


class ComponentRegistry:
    """Stores and resolves component implementations by name."""

    def __init__(self) -> None:
        self._components: dict[str, type[Component]] = {}

    def register(self, key: str, component_cls: type[Component]) -> None:
        normalized = key.strip().lower()
        if not normalized:
            msg = "Component key cannot be empty."
            raise ConfigurationError(msg)
        self._components[normalized] = component_cls

    def create(
        self,
        key: str,
        name: str,
        config: dict[str, Any] | None = None,
        *,
        llm_provider: LLMProvider | None = None,
    ) -> Component:
        component_cls = self.get(key)
        cfg = config or {}
        if issubclass(component_cls, LLMComponent):
            if llm_provider is None:
                msg = f"Component '{name}' (type '{key}') requires an LLM provider."
                raise ConfigurationError(msg)
            return component_cls(name=name, config=cfg, provider=llm_provider)
        if llm_provider is not None:
            msg = f"Component '{name}' (type '{key}') does not accept an LLM provider."
            raise ConfigurationError(msg)
        return component_cls(name=name, config=cfg)

    def get(self, key: str) -> type[Component]:
        normalized = key.strip().lower()
        component_cls = self._components.get(normalized)
        if component_cls is None:
            msg = f"Component '{key}' is not registered."
            raise ConfigurationError(msg)
        return component_cls

    def keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._components.keys()))
