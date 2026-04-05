"""Pipeline API tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from oris import Pipeline
from oris.core.exceptions import ConfigurationError
from oris.pipeline.loader import load_yaml_config
from oris.pipeline.validation import validate_pipeline_config


def test_package_exports_pipeline() -> None:
    assert Pipeline.__name__ == "Pipeline"


def test_pipeline_from_config_and_run() -> None:
    pipeline = Pipeline.from_config(
        {
            "name": "test",
            "components": [
                {"type": "passthrough", "name": "noop"},
                {
                    "type": "template_response",
                    "name": "answer",
                    "config": {"template": "Echo: {query}"},
                },
            ],
        }
    )
    result = pipeline.run({"query": "What is AI?"})
    assert result.output["output"] == "Echo: What is AI?"


def test_pipeline_rejects_unknown_keys() -> None:
    with pytest.raises(ConfigurationError):
        Pipeline.from_config({"components": [{"type": "passthrough"}], "bad": 1})


def test_pipeline_rejects_empty_components() -> None:
    with pytest.raises(ConfigurationError):
        Pipeline.from_config({"components": []})


def test_validate_pipeline_config_accepts_minimal() -> None:
    validate_pipeline_config({"components": [{"type": "passthrough", "name": "n"}]})


def test_load_yaml_config_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "p.yaml"
    p.write_text("name: x\ncomponents:\n  - type: passthrough\n    name: a\n", encoding="utf-8")
    cfg = load_yaml_config(p)
    assert cfg["name"] == "x"
    assert len(cfg["components"]) == 1
