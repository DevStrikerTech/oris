"""Provider tests."""

from __future__ import annotations

import pytest

from oris.providers.huggingface import HuggingFaceProvider
from oris.providers.openai import OpenAIProvider


def test_openai_provider_stub_response() -> None:
    provider = OpenAIProvider(model_name="gpt-test")
    response = provider.generate("hello")
    assert response.startswith("[openai:gpt-test]")


def test_huggingface_provider_stub_response() -> None:
    provider = HuggingFaceProvider(model_name="hf-test")
    response = provider.generate("hello")
    assert response.startswith("[huggingface:hf-test]")


def test_provider_reads_credential_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORIS_TEST_KEY", "secret-value")
    provider = OpenAIProvider(model_name="m", config={"api_key_env": "ORIS_TEST_KEY"})
    assert provider.credential_from_env() == "secret-value"


def test_provider_missing_env_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ORIS_MISSING", raising=False)
    provider = HuggingFaceProvider(model_name="m", config={"api_key_env": "ORIS_MISSING"})
    assert provider.credential_from_env() is None


def test_provider_blank_env_key_config() -> None:
    provider = OpenAIProvider(model_name="m", config={"api_key_env": ""})
    assert provider.credential_from_env() is None
