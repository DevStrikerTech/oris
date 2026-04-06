"""Hook protocols for pipeline and step execution."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeAlias

from oris.runtime.context import ExecutionContext

ExecutionHook: TypeAlias = Callable[[dict[str, Any], ExecutionContext], dict[str, Any]]

PreExecutionHook: TypeAlias = ExecutionHook
PostExecutionHook: TypeAlias = ExecutionHook
PipelineHook: TypeAlias = ExecutionHook
