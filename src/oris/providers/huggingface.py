"""Hugging Face provider stub."""

from __future__ import annotations

from typing import Any

from .base import LLMProvider


class HuggingFaceProvider(LLMProvider):
    """Provider stub for Hugging Face-compatible deployments (no network I/O)."""

    def generate(self, prompt: str, **kwargs: Any) -> str:
        _ = kwargs
        _ = self.credential_from_env()
        return f"[huggingface:{self.model_name}] {prompt}"
