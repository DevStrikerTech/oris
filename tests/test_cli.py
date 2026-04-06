"""CLI tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oris.cli.main import main


def _write_pipeline(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "name: sample",
                "components:",
                "  - type: template_response",
                "    name: responder",
                "    config:",
                "      template: 'Hello: {query}'",
            ]
        ),
        encoding="utf-8",
    )


def test_cli_validate(tmp_path: Path) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    code = main(["validate", str(pipeline_path)])
    assert code == 0


def test_cli_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    code = main(["run", str(pipeline_path), "--input-json", '{"query":"hi"}'])
    assert code == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["status"] == "success"
    assert "run_id" in payload
    assert "trace" in payload
    assert payload["output"]["output"] == "Hello: hi"
