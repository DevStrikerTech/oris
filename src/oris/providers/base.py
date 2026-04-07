"""Provider abstraction for framework-agnostic model calls."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract LLM provider contract; credentials come from config/env only."""

    __slots__ = ("_config",)

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    @property
    def config(self) -> dict[str, Any]:
        """Validated, non-secret configuration (``api_key_env`` holds the env var name)."""
        return self._config

    @property
    def model_name(self) -> str:
        """Resolved model identifier from configuration."""
        return str(self._config["model"])

    def credential_from_env(self, config_key: str = "api_key_env") -> str | None:
        """Resolve ``os.environ[env_name]`` when ``config[config_key]`` names a variable."""
        env_name = self._config.get(config_key)
        if not isinstance(env_name, str) or not env_name.strip():
            return None
        return os.environ.get(env_name.strip())

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a text response for a prompt."""
