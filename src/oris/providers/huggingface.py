"""Hugging Face provider stub (no network I/O)."""

from __future__ import annotations

import os
from typing import Any

from oris.core.exceptions import ConfigurationError

from .base import LLMProvider

HUGGINGFACE_PROVIDER_ALLOWED_KEYS: frozenset[str] = frozenset({"type", "model", "api_key_env"})
HUGGINGFACE_PROVIDER_EXPANDIBLE_KEYS: frozenset[str] = frozenset({"model"})


def _validate_hf_declaration(logical_id: str, decl: dict[str, Any]) -> dict[str, Any]:
    path = f"providers.{logical_id}"
    model = decl.get("model")
    if not isinstance(model, str) or not model.strip():
        msg = f"Provider at {path} requires non-empty string 'model'."
        raise ConfigurationError(msg)
    api_key_env = decl.get("api_key_env")
    if not isinstance(api_key_env, str) or not api_key_env.strip():
        msg = f"Provider at {path} requires non-empty string 'api_key_env'."
        raise ConfigurationError(msg)
    env_name = api_key_env.strip()
    raw = os.environ.get(env_name)
    if raw is None or raw == "":
        msg = (
            f"Environment variable '{env_name}' is unset or empty "
            f"(required for credential at {path}.api_key_env)."
        )
        raise ConfigurationError(msg)
    return {k: v for k, v in decl.items() if k != "type"}


class HuggingFaceProvider(LLMProvider):
    """Provider stub for Hugging Face-style configurations (no network I/O)."""

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        _ = kwargs
        _ = self.credential_from_env()
        return f"[huggingface:{self.model_name}] {prompt}"


def build_huggingface_provider(logical_id: str, decl: dict[str, Any]) -> HuggingFaceProvider:
    """Construct a ``HuggingFaceProvider`` after declaration validation (eager build)."""
    cfg = _validate_hf_declaration(logical_id, decl)
    return HuggingFaceProvider(config=cfg)
