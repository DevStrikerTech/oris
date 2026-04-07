"""Built-in components for simple pipeline composition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from oris.core.exceptions import ConfigurationError
from oris.runtime.context import ExecutionContext

from .base import Component, LLMComponent


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


@dataclass(slots=True)
class LLMEchoComponent(LLMComponent):
    """Calls the injected ``LLMProvider`` with ``query`` from the payload (stub-friendly)."""

    def validate_config(self, config: dict[str, Any]) -> None:
        provider_id = config.get("provider")
        if not isinstance(provider_id, str) or not provider_id.strip():
            msg = "Component 'llm_echo' requires string config 'provider' (logical provider id)."
            raise ConfigurationError(msg)

    def run(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        _ = context
        query = str(data.get("query", "")).strip()
        text = self.provider.generate(query)
        out = dict(data)
        out["output"] = text
        return out
