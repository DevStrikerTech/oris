"""CLI output formatting, redaction, and debug trace emission."""

from __future__ import annotations

import json
import sys
from typing import Any, TextIO

from oris.core.enums import ExecutionStatus
from oris.pipeline.pipeline import Pipeline
from oris.runtime.models import PipelineResult
from oris.tracing.models import StepTrace

_SENSITIVE_KEY_FRAGMENTS: frozenset[str] = frozenset(
    {
        "api_key",
        "apikey",
        "token",
        "secret",
        "password",
        "authorization",
        "bearer",
        "credential",
        "private_key",
        "access_key",
        "client_secret",
    },
)


def _key_is_sensitive(key: str) -> bool:
    lower = key.lower().replace("-", "_")
    return any(fragment in lower for fragment in _SENSITIVE_KEY_FRAGMENTS)


def redact_mapping_tree(obj: Any) -> Any:
    """Deep-copy dict/list structures, redacting values for sensitive-looking keys."""
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if _key_is_sensitive(str(k)):
                out[str(k)] = "[REDACTED]"
            elif isinstance(v, dict):
                out[str(k)] = redact_mapping_tree(v)
            elif isinstance(v, list):
                out[str(k)] = redact_mapping_tree(v)
            else:
                out[str(k)] = v
        return out
    if isinstance(obj, list):
        return [redact_mapping_tree(item) for item in obj]
    return obj


def build_run_summary_for_cli(result: PipelineResult, *, redact: bool = True) -> dict[str, Any]:
    summary = result.to_run_summary()
    if not redact:
        return summary
    out = dict(summary)
    if "output" in out:
        out["output"] = redact_mapping_tree(out["output"])
    return out


def emit_run_debug(result: PipelineResult, *, stream: TextIO | None = None) -> None:
    err = sys.stderr if stream is None else stream
    trace = result.trace
    print(f"[oris debug] run_id={trace.run_id}", file=err)
    print(f"[oris debug] trace_status={trace.status}", file=err)
    success = ExecutionStatus.SUCCEEDED.value
    for step in trace.steps:
        _emit_step_debug(step, success_value=success, stream=err)


def _emit_step_debug(step: StepTrace, *, success_value: str, stream: TextIO) -> None:
    ok = step.status == success_value
    status_label = "ok" if ok else "fail"
    started = step.started_at.isoformat()
    finished = step.finished_at.isoformat()
    print(
        f"[oris debug] step {step.step_id!r} component={step.component_name!r} "
        f"status={status_label} latency_ms={step.latency_ms:.3f}",
        file=stream,
    )
    print(f"[oris debug]   started_at={started} finished_at={finished}", file=stream)
    if step.flags:
        print(f"[oris debug]   flags={json.dumps(step.flags, sort_keys=True)}", file=stream)
    if step.metadata:
        print(
            f"[oris debug]   metadata={json.dumps(step.metadata, sort_keys=True)}",
            file=stream,
        )


def emit_validate_debug(pipeline: Pipeline, *, stream: TextIO | None = None) -> None:
    err = sys.stderr if stream is None else stream
    meta = pipeline.plan.metadata
    name = meta.get("pipeline_name", meta.get("name", "(unnamed)"))
    print(f"[oris debug] validated pipeline name={name!r}", file=err)
    print(f"[oris debug] step_count={len(pipeline.plan.steps)}", file=err)
    for step in pipeline.plan.steps:
        comp_name = step.component.name
        print(
            f"[oris debug]   step_id={step.step_id!r} component={comp_name!r}",
            file=err,
        )
