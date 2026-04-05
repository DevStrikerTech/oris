"""Provider abstraction for framework-agnostic model calls."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LLMProvider(ABC):
    """Abstract LLM provider contract; credentials come from config/env only."""

    model_name: str
    config: dict[str, Any] = field(default_factory=dict)

    def credential_from_env(self, config_key: str = "api_key_env") -> str | None:
        """Resolve ``os.environ[env_name]`` when ``config[config_key]`` names a variable."""
        env_name = self.config.get(config_key)
        if not isinstance(env_name, str) or not env_name.strip():
            return None
        return os.environ.get(env_name.strip())

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a text response for a prompt."""
