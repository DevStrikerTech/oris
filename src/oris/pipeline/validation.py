"""Validate pipeline configuration mappings."""

from __future__ import annotations

from typing import Any

from oris.core.exceptions import ConfigurationError


def validate_pipeline_config(config: dict[str, Any]) -> None:
    """Ensure top-level pipeline config shape is supported."""
    allowed_top_keys = {"name", "components", "metadata"}
    unknown_keys = set(config.keys()) - allowed_top_keys
    if unknown_keys:
        msg = f"Unsupported top-level config keys: {sorted(unknown_keys)}"
        raise ConfigurationError(msg)
    components = config.get("components")
    if not isinstance(components, list) or not components:
        msg = "Pipeline config requires a non-empty 'components' list."
        raise ConfigurationError(msg)
