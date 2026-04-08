"""Load pipeline definitions from YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from oris.core.exceptions import ConfigurationError


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    """Read and parse a pipeline YAML file into a mapping."""
    file_path = Path(path)
    if not file_path.exists():
        msg = f"Pipeline file does not exist: {file_path}"
        raise ConfigurationError(msg)
    raw_text = file_path.read_text(encoding="utf-8")
    try:
        loaded = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        msg = f"Invalid pipeline YAML syntax: {exc}"
        raise ConfigurationError(msg) from exc
    if not isinstance(loaded, dict):
        msg = "Pipeline YAML must parse to a mapping."
        raise ConfigurationError(msg)
    return loaded
