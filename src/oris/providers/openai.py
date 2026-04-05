"""OpenAI provider stub."""

from __future__ import annotations

from typing import Any

from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """Provider stub for OpenAI-compatible deployments (no network I/O)."""

    def generate(self, prompt: str, **kwargs: Any) -> str:
        _ = kwargs
        _ = self.credential_from_env()
        return f"[openai:{self.model_name}] {prompt}"
