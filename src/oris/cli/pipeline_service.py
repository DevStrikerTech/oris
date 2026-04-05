"""CLI-facing pipeline operations (thin orchestration, no argparse)."""

from __future__ import annotations

from typing import Any

from oris.pipeline import Pipeline
from oris.runtime.models import PipelineResult


def run_pipeline_from_path(pipeline_path: str, input_data: dict[str, Any]) -> PipelineResult:
    """Load a pipeline from disk and run it with the given input mapping."""
    pipeline = Pipeline.from_yaml(pipeline_path)
    return pipeline.run(input_data)


def validate_pipeline_path(pipeline_path: str) -> None:
    """Parse and validate a pipeline file; raises on invalid configuration."""
    _ = Pipeline.from_yaml(pipeline_path)
