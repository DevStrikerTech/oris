"""SafeRunner integration wrapper tests."""

from __future__ import annotations

from typing import Any, cast

import pytest

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


def test_safe_runner_wraps_external_pipeline() -> None:
    runner = SafeRunner(ExternalPipeline(), policy=PolicyEnforcer())
    result = runner.run({"query": "hello"})
    assert result["output"] == "ok: hello"


def test_safe_runner_blocks_unsafe_input() -> None:
    runner = SafeRunner(ExternalPipeline(), policy=PolicyEnforcer())
    with pytest.raises(GuardViolationError):
        runner.run({"secret": "abc"})


def test_safe_runner_requires_mapping_output() -> None:
    runner = SafeRunner(cast(Any, InvalidExternalPipeline()), policy=PolicyEnforcer())
    with pytest.raises(PipelineExecutionError):
        runner.run({"query": "hello"})
