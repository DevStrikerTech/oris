"""Hook normalization rejects wrong hook kinds with clear errors."""

from __future__ import annotations

from typing import cast

import pytest

from oris.rai.hooks import InputPolicyHook, OutputPolicyHook
from oris.rai.policy import PolicyEnforcer
from oris.runtime.hooks import (
    CallablePipelinePostHook,
    CallablePipelinePreHook,
    CallablePostStepHook,
    CallablePreStepHook,
    PipelinePostHookLike,
    PipelinePreHookLike,
    PostStepHookLike,
    PreStepHookLike,
    as_pipeline_post_hook,
    as_pipeline_pre_hook,
    as_post_step_hook,
    as_pre_step_hook,
)

_policy = PolicyEnforcer()


def test_as_pre_step_hook_rejects_pipeline_pre_hook() -> None:
    with pytest.raises(TypeError, match="PreStepHook"):
        as_pre_step_hook(cast(PreStepHookLike, InputPolicyHook(_policy)))


def test_as_post_step_hook_rejects_pipeline_post_hook() -> None:
    with pytest.raises(TypeError, match="PostStepHook"):
        as_post_step_hook(cast(PostStepHookLike, OutputPolicyHook(_policy)))


def test_as_pipeline_pre_hook_rejects_post_step_only() -> None:
    post_only = CallablePostStepHook(lambda d, c: d)
    with pytest.raises(TypeError, match="PipelinePreHook"):
        as_pipeline_pre_hook(cast(PipelinePreHookLike, post_only))


def test_as_pipeline_post_hook_rejects_input_policy_hook() -> None:
    with pytest.raises(TypeError, match="PipelinePostHook"):
        as_pipeline_post_hook(cast(PipelinePostHookLike, InputPolicyHook(_policy)))


def test_hook_normalizers_return_same_instance_when_already_typed() -> None:
    pre = CallablePreStepHook(lambda d, c: d)
    post = CallablePostStepHook(lambda d, c: d)
    ppre = CallablePipelinePreHook(lambda d, c: d)
    ppost = CallablePipelinePostHook(lambda d, c: d)
    assert as_pre_step_hook(pre) is pre
    assert as_post_step_hook(post) is post
    assert as_pipeline_pre_hook(ppre) is ppre
    assert as_pipeline_post_hook(ppost) is ppost
