"""Tracing tests."""

from __future__ import annotations

import logging

import pytest

from oris.tracing.audit import AuditLogger
from oris.tracing.models import RunTrace, StepTrace, utc_now


def test_run_trace_defaults() -> None:
    trace = RunTrace(run_id="run-1", started_at=utc_now())
    assert trace.status == "pending"
    assert trace.steps == []


def test_step_trace_latency_field() -> None:
    t0 = utc_now()
    t1 = utc_now()
    step = StepTrace(
        step_id="step_0",
        component_name="c",
        started_at=t0,
        finished_at=t1,
        status="succeeded",
        latency_ms=1.5,
        flags={"kind": "pipeline_step"},
    )
    assert step.latency_ms == 1.5
    assert step.flags["kind"] == "pipeline_step"


def test_audit_logger_redacts_sensitive_fields(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("oris.audit.test")
    caplog.set_level(logging.INFO, logger=logger.name)
    audit = AuditLogger(logger=logger)
    audit.log_event("event", {"token": "secret-token", "query": "hello"})
    assert "***REDACTED***" in caplog.text
    assert "secret-token" not in caplog.text
