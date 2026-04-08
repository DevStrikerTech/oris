"""CLI tests."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def _write_passthrough_pipeline(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "name: passthrough_sample",
                "steps:",
                "  - id: pas",
                "    type: passthrough",
                "    name: p",
            ]
        ),
        encoding="utf-8",
    )


def test_cli_missing_subcommand() -> None:
    assert main([]) == 2


def test_cli_help_exits_zero() -> None:
    assert main(["--help"]) == 0


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


def test_cli_invalid_pipeline_path(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["validate", "/nonexistent/oris/pipeline.yaml"])
    assert code == 1
    err = capsys.readouterr().err
    assert err.startswith("Error:")
    assert "Traceback" not in err


def test_cli_invalid_yaml(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("foo: [unclosed", encoding="utf-8")
    code = main(["validate", str(bad)])
    assert code == 1
    err = capsys.readouterr().err
    assert "Error:" in err
    assert "Traceback" not in err


def test_cli_bad_input_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    code = main(["run", str(pipeline_path), "--input-json", "not-json"])
    assert code == 1
    err = capsys.readouterr().err
    assert "Error:" in err
    assert "Traceback" not in err


def test_cli_input_json_must_be_object(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    code = main(["run", str(pipeline_path), "--input-json", "[]"])
    assert code == 1
    err = capsys.readouterr().err
    assert "object" in err.lower()


def test_cli_run_debug(tmp_path: Path) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    buf = io.StringIO()
    with redirect_stderr(buf):
        code = main(["run", str(pipeline_path), "--input-json", '{"query":"hi"}', "--debug"])
    assert code == 0
    err = buf.getvalue()
    assert "run_id=" in err
    assert "responder" in err or "step" in err


def test_cli_validate_debug(tmp_path: Path) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    buf = io.StringIO()
    with redirect_stderr(buf):
        code = main(["validate", str(pipeline_path), "--debug"])
    assert code == 0
    err = buf.getvalue()
    assert "step_count=" in err
    assert "responder" in err


def test_cli_run_redacts_secrets_in_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_passthrough_pipeline(pipeline_path)
    leaked = "super-secret-token-value"
    code = main(
        [
            "run",
            str(pipeline_path),
            "--input-json",
            json.dumps({"openai_api_key": leaked, "ok": "visible"}),
        ],
    )
    assert code == 0
    out = capsys.readouterr().out
    assert leaked not in out
    payload = json.loads(out.strip())
    assert payload["output"]["openai_api_key"] == "[REDACTED]"
    assert payload["output"]["ok"] == "visible"


def test_cli_run_format_pretty(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    code = main(["run", str(pipeline_path), "--input-json", '{"query":"x"}', "--format", "pretty"])
    assert code == 0
    out = capsys.readouterr().out
    assert "\n" in out
    payload = json.loads(out)
    assert payload["status"] == "success"


def test_cli_unexpected_error_no_traceback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    with patch("oris.cli.main.run_pipeline_from_path", side_effect=RuntimeError("internal")):
        code = main(["run", str(pipeline_path)])
    assert code == 1
    err = capsys.readouterr().err
    assert "unexpected error" in err.lower()
    assert "Traceback" not in err


def test_main_system_exit_without_code() -> None:
    with patch("oris.cli.main.build_parser") as build_parser:
        parser = MagicMock()
        parser.parse_args.side_effect = SystemExit()
        build_parser.return_value = parser
        assert main([]) == 0


def test_cli_unexpected_error_debug_shows_exception(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pipeline_path = tmp_path / "pipeline.yaml"
    _write_pipeline(pipeline_path)
    with patch("oris.cli.main.run_pipeline_from_path", side_effect=RuntimeError("internal")):
        code = main(["run", str(pipeline_path), "--debug"])
    assert code == 1
    err = capsys.readouterr().err
    assert "RuntimeError" in err
    assert "internal" in err
    assert "Traceback" not in err
