"""Typed hook contracts for pipeline and step execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeAlias

from oris.runtime.context import ExecutionContext


class Hook(ABC):
    """Base contract: transform payload in place in the execution graph."""

    __slots__ = ()

    @abstractmethod
    def invoke(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Return the next payload (typically a copy of ``data`` with updates)."""


class PreStepHook(Hook):
    """Runs immediately before each plan step's component."""


class PostStepHook(Hook):
    """Runs immediately after each plan step's component."""


class PipelinePreHook(Hook):
    """Runs once after the run starts, before the step loop."""


class PipelinePostHook(Hook):
    """Runs once after the step loop, before success finalization."""


class CallablePreStepHook(PreStepHook):
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[[dict[str, Any], ExecutionContext], dict[str, Any]]) -> None:
        self._fn = fn

    def invoke(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        return self._fn(data, context)


class CallablePostStepHook(PostStepHook):
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[[dict[str, Any], ExecutionContext], dict[str, Any]]) -> None:
        self._fn = fn

    def invoke(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        return self._fn(data, context)


class CallablePipelinePreHook(PipelinePreHook):
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[[dict[str, Any], ExecutionContext], dict[str, Any]]) -> None:
        self._fn = fn

    def invoke(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        return self._fn(data, context)


class CallablePipelinePostHook(PipelinePostHook):
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[[dict[str, Any], ExecutionContext], dict[str, Any]]) -> None:
        self._fn = fn

    def invoke(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        return self._fn(data, context)


HookPayloadFn: TypeAlias = Callable[[dict[str, Any], ExecutionContext], dict[str, Any]]

PreStepHookLike: TypeAlias = PreStepHook | HookPayloadFn
PostStepHookLike: TypeAlias = PostStepHook | HookPayloadFn
PipelinePreHookLike: TypeAlias = PipelinePreHook | HookPayloadFn
PipelinePostHookLike: TypeAlias = PipelinePostHook | HookPayloadFn


def as_pre_step_hook(hook: PreStepHookLike) -> PreStepHook:
    """Normalize a hook instance or plain callable to ``PreStepHook``."""
    if isinstance(hook, PreStepHook):
        return hook
    if isinstance(hook, Hook):
        msg = f"pre_step_hooks expects PreStepHook, not {type(hook).__name__}."
        raise TypeError(msg)
    return CallablePreStepHook(hook)


def as_post_step_hook(hook: PostStepHookLike) -> PostStepHook:
    """Normalize a hook instance or plain callable to ``PostStepHook``."""
    if isinstance(hook, PostStepHook):
        return hook
    if isinstance(hook, Hook):
        msg = f"post_step_hooks expects PostStepHook, not {type(hook).__name__}."
        raise TypeError(msg)
    return CallablePostStepHook(hook)


def as_pipeline_pre_hook(hook: PipelinePreHookLike) -> PipelinePreHook:
    """Normalize a hook instance or plain callable to ``PipelinePreHook``."""
    if isinstance(hook, PipelinePreHook):
        return hook
    if isinstance(hook, Hook):
        msg = f"pipeline_pre_hooks expects PipelinePreHook, not {type(hook).__name__}."
        raise TypeError(msg)
    return CallablePipelinePreHook(hook)


def as_pipeline_post_hook(hook: PipelinePostHookLike) -> PipelinePostHook:
    """Normalize a hook instance or plain callable to ``PipelinePostHook``."""
    if isinstance(hook, PipelinePostHook):
        return hook
    if isinstance(hook, Hook):
        msg = f"pipeline_post_hooks expects PipelinePostHook, not {type(hook).__name__}."
        raise TypeError(msg)
    return CallablePipelinePostHook(hook)


# Backward-compatible names for existing call sites (same underlying ABCs).
ExecutionHook = Hook
PreExecutionHook = PreStepHook
PostExecutionHook = PostStepHook
# Legacy umbrella type: pipeline pre/post hooks are narrowed to PipelinePreHook / PipelinePostHook.
PipelineHook = Hook
