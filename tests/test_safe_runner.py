"""SafeRunner integration wrapper tests."""

from __future__ import annotations

from collections import UserDict
from typing import Any, cast

import pytest

from oris.core.enums import ExecutionStatus
from oris.core.exceptions import GuardViolationError, PipelineExecutionError
from oris.integrations.safe_runner import SafeRunner
from oris.rai.policy import PolicyEnforcer


class ExternalPipeline:
    def run(self, input_data: dict[str, str]) -> dict[str, str]:
        return {"output": f"ok: {input_data.get('query', '')}"}


class InvalidExternalPipeline:
    def run(self, input_data: dict[str, str]) -> str:
        _ = input_data
        return "not-a-dict"


class MappingOutputPipeline:
    def run(self, input_data: dict[str, str]) -> UserDict[str, str]:
        _ = input_data
        return UserDict([("out", "mapped")])


class PreferRunOverCall:
    """`.run` must win when both exist."""

    def run(self, input_data: dict[str, str]) -> dict[str, str]:
        return {"via": "run", "q": input_data.get("query", "")}

    def __call__(self, input_data: dict[str, str]) -> dict[str, str]:
        return {"via": "call"}


class FakeModel:
    def model_dump(self) -> dict[str, str]:
        return {"from_model": "yes"}


class BadModelDump:
    def model_dump(self) -> str:
        return "not-a-mapping"


def test_safe_runner_wraps_external_pipeline() -> None:
    runner = SafeRunner(ExternalPipeline(), policy=PolicyEnforcer())
    result = runner.run({"query": "hello"})
    assert result["output"] == "ok: hello"


def test_safe_runner_wraps_plain_callable() -> None:
    runner = SafeRunner(lambda d: {"echo": d["q"]}, policy=PolicyEnforcer())
    assert runner.run({"q": "hi"}) == {"echo": "hi"}


def test_safe_runner_prefers_run_over_call() -> None:
    runner = SafeRunner(PreferRunOverCall(), policy=PolicyEnforcer())
    assert runner.run({"query": "x"}) == {"via": "run", "q": "x"}


def test_safe_runner_accepts_mapping_input() -> None:
    runner = SafeRunner(lambda d: {"k": d["a"]}, policy=PolicyEnforcer())
    ud: UserDict[str, str] = UserDict([("a", "1")])
    assert runner.run(cast(Any, ud)) == {"k": "1"}


def test_safe_runner_rejects_non_mapping_input() -> None:
    runner = SafeRunner(lambda d: d, policy=PolicyEnforcer())
    with pytest.raises(PipelineExecutionError, match="dictionary-compatible mapping"):
        runner.run(cast(Any, "not-a-mapping"))


def test_safe_runner_blocks_unsafe_input() -> None:
    runner = SafeRunner(ExternalPipeline(), policy=PolicyEnforcer())
    with pytest.raises(GuardViolationError):
        runner.run({"secret": "abc"})


def test_safe_runner_requires_mapping_output() -> None:
    runner = SafeRunner(cast(Any, InvalidExternalPipeline()), policy=PolicyEnforcer())
    with pytest.raises(PipelineExecutionError):
        runner.run({"query": "hello"})


def test_safe_runner_coerces_mapping_output() -> None:
    runner = SafeRunner(MappingOutputPipeline(), policy=PolicyEnforcer())
    assert runner.run({"query": "hello"}) == {"out": "mapped"}


def test_safe_runner_coerces_model_dump_output() -> None:
    runner = SafeRunner(lambda _d: FakeModel(), policy=PolicyEnforcer())
    assert runner.run({"query": "hello"}) == {"from_model": "yes"}


def test_safe_runner_rejects_bad_model_dump() -> None:
    runner = SafeRunner(lambda _d: BadModelDump(), policy=PolicyEnforcer())
    with pytest.raises(PipelineExecutionError, match="dictionary-compatible"):
        runner.run({"query": "hello"})


def test_safe_runner_rejects_invalid_target() -> None:
    runner = SafeRunner(object(), policy=PolicyEnforcer())
    with pytest.raises(PipelineExecutionError, match="callable or provide a run"):
        runner.run({"query": "hello"})


def test_safe_runner_wraps_external_exception() -> None:
    def boom(_d: dict[str, str]) -> dict[str, str]:
        raise ValueError("sensitive internals")

    runner = SafeRunner(boom, policy=PolicyEnforcer())
    with pytest.raises(
        PipelineExecutionError,
        match="External pipeline execution failed",
    ) as exc_info:
        runner.run({"query": "hello"})
    assert exc_info.value.__cause__ is None


def test_safe_runner_propagates_pipeline_execution_error() -> None:
    def user_defined(_d: dict[str, str]) -> dict[str, str]:
        raise PipelineExecutionError("user boundary")

    runner = SafeRunner(user_defined, policy=PolicyEnforcer())
    with pytest.raises(PipelineExecutionError, match="user boundary"):
        runner.run({"query": "hello"})


def test_safe_runner_output_policy_blocked_term() -> None:
    runner = SafeRunner(lambda _d: {"text": "exploit payload"}, policy=PolicyEnforcer())
    with pytest.raises(GuardViolationError, match="blocked policy"):
        runner.run({"query": "ok"})


def test_safe_runner_output_toxicity_stub() -> None:
    policy = PolicyEnforcer()
    runner = SafeRunner(
        lambda _d: {"x": policy.toxicity_stub_marker},
        policy=policy,
    )
    with pytest.raises(GuardViolationError, match="toxicity"):
        runner.run({"query": "ok"})


def test_safe_runner_include_trace_success() -> None:
    runner = SafeRunner(ExternalPipeline(), policy=PolicyEnforcer())
    result = runner.run({"query": "hello"}, include_trace=True)
    assert result.output["output"] == "ok: hello"
    assert result.trace.status == ExecutionStatus.SUCCEEDED.value
    assert len(result.trace.steps) == 1
    step = result.trace.steps[0]
    assert step.flags["kind"] == "external_pipeline"
    assert step.latency_ms >= 0.0
    summary = result.to_run_summary()
    assert summary["status"] == "success"
    assert summary["trace"][0]["flags"]["kind"] == "external_pipeline"
    assert result.metadata.get("source") == "external"


def test_safe_runner_include_trace_on_failure() -> None:
    runner = SafeRunner(ExternalPipeline(), policy=PolicyEnforcer())
    with pytest.raises(GuardViolationError):
        runner.run({"secret": "no"}, include_trace=True)
