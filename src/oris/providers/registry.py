"""Registry mapping provider ``type`` strings to factories and schema metadata."""

from __future__ import annotations

import difflib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from oris.core.exceptions import ConfigurationError

from .base import LLMProvider


@dataclass(frozen=True, slots=True)
class ProviderTypeSpec:
    """Allowlisted YAML keys and factory for one provider ``type``."""

    allowed_keys: frozenset[str]
    expandible_keys: frozenset[str]
    factory: Callable[[str, dict[str, Any]], LLMProvider]


class ProviderRegistry:
    """Maps provider type strings (case-insensitive) to construction specs."""

    def __init__(self) -> None:
        self._specs: dict[str, ProviderTypeSpec] = {}

    def register(self, type_key: str, spec: ProviderTypeSpec) -> None:
        normalized = type_key.strip().lower()
        if not normalized:
            msg = "Provider type key cannot be empty."
            raise ConfigurationError(msg)
        self._specs[normalized] = spec

    def get_spec(self, type_key: str) -> ProviderTypeSpec:
        normalized = type_key.strip().lower()
        spec = self._specs.get(normalized)
        if spec is None:
            available = sorted(self._specs)
            close = difflib.get_close_matches(normalized, available, n=3, cutoff=0.5)
            hint = f" Similar types: {close}." if close else ""
            msg = f"Unknown provider type '{type_key}'. Known types: {available}.{hint}"
            raise ConfigurationError(msg)
        return spec

    def registered_types(self) -> tuple[str, ...]:
        return tuple(sorted(self._specs))


_DEFAULT_REGISTRY = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Return the process-wide default provider registry."""
    return _DEFAULT_REGISTRY


def register_builtin_providers(registry: ProviderRegistry | None = None) -> None:
    """Register built-in provider types (idempotent for the default registry)."""
    from .huggingface import (
        HUGGINGFACE_PROVIDER_ALLOWED_KEYS,
        HUGGINGFACE_PROVIDER_EXPANDIBLE_KEYS,
        build_huggingface_provider,
    )
    from .openai import (
        OPENAI_PROVIDER_ALLOWED_KEYS,
        OPENAI_PROVIDER_EXPANDIBLE_KEYS,
        build_openai_provider,
    )

    reg = registry or _DEFAULT_REGISTRY
    if "openai" in reg._specs:
        return
    reg.register(
        "openai",
        ProviderTypeSpec(
            allowed_keys=OPENAI_PROVIDER_ALLOWED_KEYS,
            expandible_keys=OPENAI_PROVIDER_EXPANDIBLE_KEYS,
            factory=build_openai_provider,
        ),
    )
    reg.register(
        "huggingface",
        ProviderTypeSpec(
            allowed_keys=HUGGINGFACE_PROVIDER_ALLOWED_KEYS,
            expandible_keys=HUGGINGFACE_PROVIDER_EXPANDIBLE_KEYS,
            factory=build_huggingface_provider,
        ),
    )
