"""Unit tests for CLI output helpers."""

from __future__ import annotations

import io

from oris.cli.output import build_run_summary_for_cli, emit_run_debug, redact_mapping_tree
from oris.core.enums import ExecutionStatus
from oris.runtime.models import PipelineResult
from oris.tracing.models import RunTrace, StepTrace, utc_now


def test_redact_mapping_tree_nested() -> None:
    data = {
        "safe": "visible",
        "openai_api_key": "hide-me",
        "nested": {"inner_token": "x", "ok": 1},
    }
    out = redact_mapping_tree(data)
    assert out["safe"] == "visible"
    assert out["openai_api_key"] == "[REDACTED]"
    assert out["nested"]["inner_token"] == "[REDACTED]"  # noqa: S105
    assert out["nested"]["ok"] == 1


def test_redact_mapping_tree_list_of_dicts() -> None:
    data = {"items": [{"api_key": "x"}, {"plain": "y"}]}
    out = redact_mapping_tree(data)
    assert out["items"][0]["api_key"] == "[REDACTED]"  # noqa: S105
    assert out["items"][1]["plain"] == "y"


def test_redact_mapping_tree_scalar_unchanged() -> None:
    assert redact_mapping_tree(42) == 42
    assert redact_mapping_tree("x") == "x"


def test_build_run_summary_for_cli_redacts_output_only() -> None:
    trace = RunTrace(run_id="rid", started_at=utc_now(), status=ExecutionStatus.SUCCEEDED.value)
    result = PipelineResult(
        output={"api_key": "secret", "text": "hello"},
        trace=trace,
    )
    summary = build_run_summary_for_cli(result, redact=True)
    assert summary["output"]["api_key"] == "[REDACTED]"
    assert summary["output"]["text"] == "hello"
    assert summary["run_id"] == "rid"


def test_build_run_summary_for_cli_no_redact() -> None:
    trace = RunTrace(run_id="rid", started_at=utc_now(), status=ExecutionStatus.SUCCEEDED.value)
    result = PipelineResult(output={"api_key": "secret"}, trace=trace)
    summary = build_run_summary_for_cli(result, redact=False)
    assert summary["output"]["api_key"] == "secret"


def test_emit_run_debug_includes_metadata_when_present() -> None:
    started = utc_now()
    step = StepTrace(
        step_id="s1",
        component_name="c",
        started_at=started,
        finished_at=started,
        status=ExecutionStatus.SUCCEEDED.value,
        flags={"kind": "pipeline_step"},
        metadata={"extra": 1},
    )
    trace = RunTrace(run_id="r1", started_at=started, status=ExecutionStatus.SUCCEEDED.value)
    trace.steps.append(step)
    result = PipelineResult(output={}, trace=trace)
    buf = io.StringIO()
    emit_run_debug(result, stream=buf)
    assert "metadata=" in buf.getvalue()
