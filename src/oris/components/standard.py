"""Built-in components for simple pipeline composition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from oris.core.exceptions import ConfigurationError
from oris.runtime.context import ExecutionContext

from .base import Component


@dataclass(slots=True)
class PassthroughComponent(Component):
    """No-op component useful for smoke tests and scaffolding."""

    def run(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        _ = context
        return data


@dataclass(slots=True)
class TemplateResponseComponent(Component):
    """Formats an output response from the input payload."""

    def validate_config(self, config: dict[str, Any]) -> None:
        template = config.get("template", "Received query: {query}")
        if not isinstance(template, str):
            msg = "Component 'template' config must be a string."
            raise ConfigurationError(msg)
        try:
            template.format(query="")
        except (KeyError, ValueError) as exc:
            msg = "Template must be a format string using only the {query} field."
            raise ConfigurationError(msg) from exc

    def run(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        _ = context
        query = str(data.get("query", "")).strip()
        template = str(self.config.get("template", "Received query: {query}"))
        out = dict(data)
        out["output"] = template.format(query=query)
        return out
