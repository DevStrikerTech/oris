"""Whole-string environment variable expansion for provider declarations."""

from __future__ import annotations

import os
import re
from typing import Any

from oris.core.exceptions import ConfigurationError

# Entire scalar must be exactly ${VAR_NAME}; VAR_NAME is a shell-like identifier.
_WHOLE_ENV_REF = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")


def expand_scalar_if_eligible(value: Any, *, config_path: str) -> Any:
    """If value is a string matching exactly ``${VAR}``, return ``os.environ[VAR]``.

    Otherwise return ``value`` unchanged. Raises ``ConfigurationError`` if the
    variable is unset or empty (never includes the resolved value in messages).
    """
    if not isinstance(value, str):
        return value
    match = _WHOLE_ENV_REF.match(value.strip())
    if not match:
        return value
    var_name = match.group(1)
    raw = os.environ.get(var_name)
    if raw is None or raw == "":
        msg = f"Environment variable '{var_name}' is unset or empty (required at {config_path})."
        raise ConfigurationError(msg)
    return raw


def expand_mapping_keys(
    data: dict[str, Any],
    *,
    expandible_keys: frozenset[str],
    path_prefix: str,
) -> dict[str, Any]:
    """Return a shallow copy with ``${VAR}`` expansion applied only on ``expandible_keys``."""
    out = dict(data)
    for key in expandible_keys:
        if key not in out:
            continue
        out[key] = expand_scalar_if_eligible(
            out[key],
            config_path=f"{path_prefix}.{key}",
        )
    return out
