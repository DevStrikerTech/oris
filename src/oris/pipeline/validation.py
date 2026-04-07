"""Validate pipeline configuration mappings."""

from __future__ import annotations

from typing import Any

from oris.core.exceptions import ConfigurationError


def validate_pipeline_config(config: dict[str, Any]) -> None:
    """Ensure top-level pipeline config shape is supported."""
    allowed_top_keys = {"name", "components", "metadata", "providers"}
    unknown_keys = set(config.keys()) - allowed_top_keys
    if unknown_keys:
        msg = f"Unsupported top-level config keys: {sorted(unknown_keys)}"
        raise ConfigurationError(msg)
    components = config.get("components")
    if not isinstance(components, list) or not components:
        msg = "Pipeline config requires a non-empty 'components' list."
        raise ConfigurationError(msg)
    raw_providers = config.get("providers")
    if raw_providers is None:
        return
    if not isinstance(raw_providers, dict):
        msg = "Top-level 'providers' must be a mapping."
        raise ConfigurationError(msg)
    for logical_id, block in raw_providers.items():
        if not isinstance(logical_id, str) or not logical_id.strip():
            msg = "Provider ids must be non-empty strings."
            raise ConfigurationError(msg)
        path = f"providers.{logical_id.strip()}"
        if not isinstance(block, dict):
            msg = f"Provider declaration at {path} must be a mapping."
            raise ConfigurationError(msg)
        ptype = block.get("type")
        if not isinstance(ptype, str) or not ptype.strip():
            msg = f"Provider at {path} requires non-empty string 'type'."
            raise ConfigurationError(msg)
