"""Hook types and default RAI hook behavior."""

from __future__ import annotations

import pytest

from oris.core.exceptions import GuardViolationError
from oris.rai.factory import build_default_guards
from oris.rai.hooks import InputPolicyHook, OutputPolicyHook
from oris.rai.policy import PolicyEnforcer
from tests.helpers import trivial_execution_context


def test_input_policy_hook_validates_like_guard() -> None:
    policy = PolicyEnforcer()
    hook = InputPolicyHook(policy)
    ctx = trivial_execution_context(policy=policy)
    assert hook({"query": "ok"}, ctx) == {"query": "ok"}


def test_input_policy_hook_raises_on_violation() -> None:
    policy = PolicyEnforcer()
    hook = InputPolicyHook(policy)
    ctx = trivial_execution_context(policy=policy)
    with pytest.raises(GuardViolationError):
        hook({"token": "x"}, ctx)


def test_output_policy_hook_validates() -> None:
    policy = PolicyEnforcer()
    hook = OutputPolicyHook(policy)
    ctx = trivial_execution_context(policy=policy)
    payload = {"output": "safe"}
    assert hook(payload, ctx) == payload


def test_build_default_guards_shares_policy() -> None:
    policy = PolicyEnforcer()
    input_guard, output_guard = build_default_guards(policy)
    ctx = trivial_execution_context(policy=policy)
    mid = input_guard.run({"query": "x"}, ctx)
    mid["output"] = "safe"
    assert output_guard.run(mid, ctx)["output"] == "safe"


def test_output_policy_hook_raises_on_blocked_term() -> None:
    policy = PolicyEnforcer()
    hook = OutputPolicyHook(policy)
    ctx = trivial_execution_context(policy=policy)
    with pytest.raises(GuardViolationError):
        hook({"output": "malware here"}, ctx)
