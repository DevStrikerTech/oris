"""Strict pipeline schema and validation tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from oris import Pipeline
from oris.core.exceptions import ConfigurationError
from oris.pipeline.loader import load_yaml_config
from oris.pipeline.schema import parse_pipeline_dict
from oris.pipeline.validation import validate_pipeline_config


def test_parse_rejects_top_level_unknown_key() -> None:
    with pytest.raises(ConfigurationError, match="unsupported top-level keys"):
        parse_pipeline_dict(
            {
                "components": [{"type": "passthrough", "name": "n"}],
                "unexpected": 1,
            },
        )


def test_parse_rejects_both_steps_and_components() -> None:
    with pytest.raises(ConfigurationError, match="only one of 'steps' or 'components'"):
        parse_pipeline_dict(
            {
                "steps": [{"id": "a", "type": "passthrough"}],
                "components": [{"type": "passthrough", "name": "n"}],
            },
        )


def test_parse_rejects_neither_steps_nor_components() -> None:
    with pytest.raises(ConfigurationError, match="require a non-empty"):
        parse_pipeline_dict({"name": "x"})


def test_steps_missing_id() -> None:
    with pytest.raises(ConfigurationError, match="missing required field 'id'"):
        parse_pipeline_dict({"steps": [{"type": "passthrough"}]})


def test_steps_missing_type() -> None:
    with pytest.raises(ConfigurationError, match="missing required field 'type'"):
        parse_pipeline_dict({"steps": [{"id": "a"}]})


def test_steps_unknown_field() -> None:
    with pytest.raises(ConfigurationError, match="unknown fields"):
        parse_pipeline_dict(
            {"steps": [{"id": "a", "type": "passthrough", "extra": 1}]},
        )


def test_steps_duplicate_ids() -> None:
    with pytest.raises(ConfigurationError, match="duplicate step id"):
        parse_pipeline_dict(
            {
                "steps": [
                    {"id": "same", "type": "passthrough"},
                    {"id": "same", "type": "passthrough"},
                ],
            },
        )


def test_legacy_duplicate_explicit_id() -> None:
    with pytest.raises(ConfigurationError, match="duplicate step id"):
        parse_pipeline_dict(
            {
                "components": [
                    {"id": "dup", "type": "passthrough", "name": "a"},
                    {"id": "dup", "type": "passthrough", "name": "b"},
                ],
            },
        )


def test_legacy_unknown_component_field() -> None:
    with pytest.raises(ConfigurationError, match="unknown fields"):
        parse_pipeline_dict(
            {
                "components": [
                    {"type": "passthrough", "name": "n", "bogus": True},
                ],
            },
        )


def test_settings_unknown_key() -> None:
    with pytest.raises(ConfigurationError, match="unknown keys in settings"):
        parse_pipeline_dict(
            {
                "components": [{"type": "passthrough", "name": "n"}],
                "settings": {"device": "auto", "foo": 1},
            },
        )


def test_settings_tracing_must_be_bool() -> None:
    with pytest.raises(ConfigurationError, match="settings.tracing must be a boolean"):
        parse_pipeline_dict(
            {
                "components": [{"type": "passthrough", "name": "n"}],
                "settings": {"tracing": "yes"},
            },
        )


def test_settings_device_non_empty_string() -> None:
    with pytest.raises(ConfigurationError, match="settings.device must be a non-empty string"):
        parse_pipeline_dict(
            {
                "components": [{"type": "passthrough", "name": "n"}],
                "settings": {"device": ""},
            },
        )


def test_provider_field_conflict() -> None:
    with pytest.raises(ConfigurationError, match="conflicting 'provider'"):
        parse_pipeline_dict(
            {
                "steps": [
                    {
                        "id": "s",
                        "type": "generate",
                        "provider": "p1",
                        "config": {"provider": "p2"},
                    },
                ],
                "providers": {
                    "p1": {"type": "openai", "model": "m", "api_key_env": "E"},
                    "p2": {"type": "openai", "model": "m", "api_key_env": "E"},
                },
            },
        )


def test_generate_resolves_to_llm_echo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("E", "x")
    p = parse_pipeline_dict(
        {
            "steps": [{"id": "g", "type": "generate", "provider": "o"}],
            "providers": {"o": {"type": "openai", "model": "m", "api_key_env": "E"}},
        },
    )
    assert p.steps[0].component_type == "llm_echo"


def test_pipeline_plan_includes_default_settings() -> None:
    pl = Pipeline.from_config(
        {"components": [{"type": "passthrough", "name": "n"}]},
    )
    assert pl.plan.metadata["settings"]["device"] == "auto"
    assert pl.plan.metadata["settings"]["tracing"] is True


def test_steps_pipeline_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    pl = Pipeline.from_config(
        {
            "name": "steps_run",
            "steps": [
                {
                    "id": "gen",
                    "type": "generate",
                    "provider": "openai",
                },
            ],
            "providers": {
                "openai": {
                    "type": "openai",
                    "model": "gpt-4",
                    "api_key_env": "OPENAI_API_KEY",
                },
            },
        },
    )
    assert pl.plan.steps[0].step_id == "gen"
    out = pl.run({"query": "hi"})
    assert "[openai:gpt-4]" in out.output["output"]


def test_unknown_component_type_in_steps() -> None:
    with pytest.raises(ConfigurationError, match="not registered"):
        Pipeline.from_config(
            {"steps": [{"id": "x", "type": "not_a_real_component_type"}]},
        )


def test_load_yaml_invalid_syntax(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("steps: [unclosed", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Invalid pipeline YAML syntax"):
        load_yaml_config(bad)


def test_validate_pipeline_config_accepts_steps() -> None:
    validate_pipeline_config(
        {"steps": [{"id": "a", "type": "passthrough"}]},
    )


def test_examples_parse() -> None:
    root = Path(__file__).resolve().parents[1]
    for name in ("simple_generation.yaml", "provider_pipeline.yaml"):
        path = root / "examples" / name
        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        parse_pipeline_dict(cfg)


def test_instantiate_components_rejects_non_list() -> None:
    from oris.components.builtin import create_builtin_registry
    from oris.pipeline.builder import instantiate_components

    reg = create_builtin_registry()
    with pytest.raises(ConfigurationError, match="expected a 'components' list"):
        instantiate_components({"components": None}, reg, {})


def test_instantiate_components_rejects_non_mapping_item() -> None:
    from oris.components.builtin import create_builtin_registry
    from oris.pipeline.builder import instantiate_components

    reg = create_builtin_registry()
    with pytest.raises(ConfigurationError, match="must be a mapping"):
        instantiate_components(
            {"components": ["not-a-dict"]},
            reg,
            {},
            step_ids=["s0"],
        )
