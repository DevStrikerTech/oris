"""Pipeline integration tests for provider injection."""

from __future__ import annotations

import pytest

from oris import Pipeline
from oris.components.base import LLMComponent
from oris.components.registry import ComponentRegistry
from oris.components.standard import PassthroughComponent
from oris.core.exceptions import ConfigurationError
from oris.pipeline.validation import validate_pipeline_config


def test_pipeline_llm_echo_injects_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-logged")
    pipeline = Pipeline.from_config(
        {
            "name": "p",
            "providers": {
                "default": {
                    "type": "openai",
                    "model": "gpt-4",
                    "api_key_env": "OPENAI_API_KEY",
                }
            },
            "components": [
                {
                    "type": "llm_echo",
                    "name": "gen",
                    "config": {"provider": "default"},
                },
            ],
        }
    )
    assert "default" in pipeline.plan.providers
    step = pipeline.plan.steps[0]
    comp = step.component
    assert isinstance(comp, LLMComponent)
    assert comp.provider is pipeline.plan.providers["default"]
    result = pipeline.run({"query": "hello"})
    assert result.output["output"].startswith("[openai:gpt-4]")


def test_pipeline_same_provider_instance_two_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("K", "v")
    pipeline = Pipeline.from_config(
        {
            "name": "p",
            "providers": {
                "shared": {"type": "openai", "model": "m", "api_key_env": "K"},
            },
            "components": [
                {"type": "llm_echo", "name": "a", "config": {"provider": "shared"}},
                {"type": "llm_echo", "name": "b", "config": {"provider": "shared"}},
            ],
        }
    )
    c0 = pipeline.plan.steps[0].component
    c1 = pipeline.plan.steps[1].component
    assert isinstance(c0, LLMComponent) and isinstance(c1, LLMComponent)
    assert c0.provider is c1.provider


def test_pipeline_unknown_provider_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("K", "v")
    with pytest.raises(ConfigurationError, match="unknown provider id"):
        Pipeline.from_config(
            {
                "name": "p",
                "providers": {
                    "only": {"type": "openai", "model": "m", "api_key_env": "K"},
                },
                "components": [
                    {"type": "llm_echo", "name": "x", "config": {"provider": "missing"}},
                ],
            }
        )


def test_pipeline_missing_env_at_build(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NO_SUCH_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="NO_SUCH_KEY"):
        Pipeline.from_config(
            {
                "name": "p",
                "providers": {
                    "x": {"type": "openai", "model": "m", "api_key_env": "NO_SUCH_KEY"},
                },
                "components": [{"type": "passthrough", "name": "n"}],
            }
        )


def test_validate_pipeline_providers_not_mapping() -> None:
    with pytest.raises(ConfigurationError, match="providers"):
        validate_pipeline_config({"components": [{"type": "x", "name": "n"}], "providers": []})


def test_registry_rejects_llm_provider_for_passthrough() -> None:
    from oris.providers.openai import OpenAIProvider

    reg = ComponentRegistry()
    reg.register("passthrough", PassthroughComponent)
    p = OpenAIProvider(config={"model": "m", "api_key_env": "E"})
    with pytest.raises(ConfigurationError, match="does not accept"):
        reg.create("passthrough", name="n", config={}, llm_provider=p)


def test_registry_llm_without_provider_raises() -> None:
    from oris.components.builtin import create_builtin_registry

    reg = create_builtin_registry()
    with pytest.raises(ConfigurationError, match="requires an LLM provider"):
        reg.create("llm_echo", name="n", config={"provider": "x"})


def test_custom_component_registry_without_llm_echo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("K", "v")
    reg = ComponentRegistry()
    reg.register("passthrough", PassthroughComponent)
    with pytest.raises(ConfigurationError, match="not registered"):
        Pipeline.from_config(
            {
                "name": "p",
                "providers": {"o": {"type": "openai", "model": "m", "api_key_env": "K"}},
                "components": [{"type": "llm_echo", "name": "x", "config": {"provider": "o"}}],
            },
            registry=reg,
        )
