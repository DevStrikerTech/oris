"""Provider unit tests."""

from __future__ import annotations

from typing import Any

import pytest

from oris.core.exceptions import ConfigurationError
from oris.pipeline.env_expand import expand_mapping_keys, expand_scalar_if_eligible
from oris.pipeline.provider_build import build_provider_instances
from oris.providers.huggingface import HuggingFaceProvider
from oris.providers.openai import OpenAIProvider
from oris.providers.registry import (
    ProviderRegistry,
    ProviderTypeSpec,
    get_provider_registry,
    register_builtin_providers,
)


def test_openai_provider_stub_response() -> None:
    provider = OpenAIProvider(config={"model": "gpt-test", "api_key_env": "ORIS_UNUSED"})
    response = provider.generate("hello")
    assert response.startswith("[openai:gpt-test]")


def test_huggingface_provider_stub_response() -> None:
    provider = HuggingFaceProvider(config={"model": "hf-test", "api_key_env": "ORIS_UNUSED"})
    response = provider.generate("hello")
    assert response.startswith("[huggingface:hf-test]")


def test_provider_reads_credential_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORIS_TEST_KEY", "secret-value")
    provider = OpenAIProvider(config={"model": "m", "api_key_env": "ORIS_TEST_KEY"})
    assert provider.credential_from_env() == "secret-value"


def test_provider_missing_env_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ORIS_MISSING", raising=False)
    provider = HuggingFaceProvider(config={"model": "m", "api_key_env": "ORIS_MISSING"})
    assert provider.credential_from_env() is None


def test_provider_blank_env_key_config() -> None:
    provider = OpenAIProvider(config={"model": "m", "api_key_env": ""})
    assert provider.credential_from_env() is None


def test_expand_scalar_whole_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORIS_MODEL", "gpt-4")
    assert expand_scalar_if_eligible("${ORIS_MODEL}", config_path="providers.x.model") == "gpt-4"


def test_expand_scalar_missing_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ORIS_ABSENT", raising=False)
    with pytest.raises(ConfigurationError, match="ORIS_ABSENT"):
        expand_scalar_if_eligible("${ORIS_ABSENT}", config_path="providers.x.model")


def test_expand_scalar_empty_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORIS_EMPTY", "")
    with pytest.raises(ConfigurationError, match="ORIS_EMPTY"):
        expand_scalar_if_eligible("${ORIS_EMPTY}", config_path="providers.x.model")


def test_expand_scalar_non_placeholder_unchanged() -> None:
    assert expand_scalar_if_eligible("gpt-4", config_path="p") == "gpt-4"
    assert expand_scalar_if_eligible("prefix-${VAR}", config_path="p") == "prefix-${VAR}"


def test_expand_mapping_keys_on_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("M", "resolved-model")
    out = expand_mapping_keys(
        {"type": "openai", "model": "${M}", "api_key_env": "K"},
        expandible_keys=frozenset({"model"}),
        path_prefix="providers.p",
    )
    assert out["model"] == "resolved-model"
    assert out["api_key_env"] == "K"


def test_build_provider_instances_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("K", "x")
    reg = ProviderRegistry()
    register_builtin_providers(reg)
    cfg = {
        "providers": {
            "o": {"type": "openai", "model": "gpt-4", "api_key_env": "K"},
        }
    }
    m = build_provider_instances(cfg, registry=reg)
    assert "o" in m
    assert m["o"].generate("hi").startswith("[openai:gpt-4]")


def test_build_provider_instances_expands_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("K", "keyval")
    monkeypatch.setenv("MYMODEL", "gpt-5")
    reg = ProviderRegistry()
    register_builtin_providers(reg)
    cfg = {
        "providers": {
            "o": {"type": "openai", "model": "${MYMODEL}", "api_key_env": "K"},
        }
    }
    m = build_provider_instances(cfg, registry=reg)
    assert m["o"].model_name == "gpt-5"


def test_build_provider_unknown_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("K", "x")
    reg = ProviderRegistry()
    register_builtin_providers(reg)
    cfg = {"providers": {"o": {"type": "openai", "model": "m", "api_key_env": "K", "extra": 1}}}
    with pytest.raises(ConfigurationError, match="Unknown keys"):
        build_provider_instances(cfg, registry=reg)


def test_build_provider_missing_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MISSING", raising=False)
    reg = ProviderRegistry()
    register_builtin_providers(reg)
    cfg = {"providers": {"o": {"type": "openai", "model": "m", "api_key_env": "MISSING"}}}
    with pytest.raises(ConfigurationError, match="MISSING"):
        build_provider_instances(cfg, registry=reg)


def test_build_provider_unknown_type() -> None:
    reg = ProviderRegistry()
    register_builtin_providers(reg)
    cfg = {"providers": {"o": {"type": "openaiii", "model": "m", "api_key_env": "K"}}}
    with pytest.raises(ConfigurationError, match="Unknown provider type"):
        build_provider_instances(cfg, registry=reg)


def _dummy_factory(_id: str, _d: dict[str, Any]) -> OpenAIProvider:
    return OpenAIProvider(config={"model": "m", "api_key_env": "E"})


def test_registry_register_empty_key() -> None:
    reg = ProviderRegistry()
    spec = ProviderTypeSpec(
        allowed_keys=frozenset({"type"}),
        expandible_keys=frozenset(),
        factory=_dummy_factory,
    )
    with pytest.raises(ConfigurationError, match="empty"):
        reg.register("  ", spec)


def test_get_provider_registry_has_builtins_after_register() -> None:
    register_builtin_providers()
    assert "openai" in get_provider_registry().registered_types()


def test_build_provider_empty_section() -> None:
    assert build_provider_instances({"providers": {}}) == {}


def test_build_provider_no_key() -> None:
    cfg = {"name": "n", "components": [{"type": "passthrough", "name": "a"}]}
    assert build_provider_instances(cfg) == {}
