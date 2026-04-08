"""Validate pipeline configuration mappings."""

from __future__ import annotations

from typing import Any

from .schema import parse_pipeline_dict


def validate_pipeline_config(config: dict[str, Any]) -> None:
    """Parse and strictly validate pipeline config; raise ``ConfigurationError`` if invalid."""
    parse_pipeline_dict(config)
