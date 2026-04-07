"""Eager provider validation, env expansion, and instance construction."""

from __future__ import annotations

from typing import Any

from oris.core.exceptions import ConfigurationError
from oris.providers.base import LLMProvider
from oris.providers.registry import (
    ProviderRegistry,
    get_provider_registry,
    register_builtin_providers,
)

from .env_expand import expand_mapping_keys


def build_provider_instances(
    config: dict[str, Any],
    *,
    registry: ProviderRegistry | None = None,
) -> dict[str, LLMProvider]:
    """Validate ``providers``, expand env placeholders, construct all instances."""
    register_builtin_providers(registry)
    reg = registry or get_provider_registry()
    raw = config.get("providers")
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        msg = "Top-level 'providers' must be a mapping."
        raise ConfigurationError(msg)

    instances: dict[str, LLMProvider] = {}
    for logical_id, block in raw.items():
        if not isinstance(logical_id, str) or not logical_id.strip():
            msg = "Provider ids must be non-empty strings."
            raise ConfigurationError(msg)
        lid = logical_id.strip()
        path = f"providers.{lid}"
        if not isinstance(block, dict):
            msg = f"Provider declaration at {path} must be a mapping."
            raise ConfigurationError(msg)
        ptype = block.get("type")
        if not isinstance(ptype, str) or not ptype.strip():
            msg = f"Provider at {path} requires non-empty string 'type'."
            raise ConfigurationError(msg)

        spec = reg.get_spec(ptype)
        unknown = set(block) - spec.allowed_keys
        if unknown:
            msg = f"Unknown keys for provider at {path}: {sorted(unknown)}."
            raise ConfigurationError(msg)

        expanded = expand_mapping_keys(
            dict(block),
            expandible_keys=spec.expandible_keys,
            path_prefix=path,
        )
        instances[lid] = spec.factory(lid, expanded)
    return instances
