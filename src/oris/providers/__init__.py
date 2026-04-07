"""Provider interfaces, built-in stubs, and registry."""

from .base import LLMProvider
from .huggingface import HuggingFaceProvider, build_huggingface_provider
from .openai import OpenAIProvider, build_openai_provider
from .registry import (
    ProviderRegistry,
    ProviderTypeSpec,
    get_provider_registry,
    register_builtin_providers,
)

__all__ = [
    "HuggingFaceProvider",
    "LLMProvider",
    "OpenAIProvider",
    "ProviderRegistry",
    "ProviderTypeSpec",
    "build_huggingface_provider",
    "build_openai_provider",
    "get_provider_registry",
    "register_builtin_providers",
]
