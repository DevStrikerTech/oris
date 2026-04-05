"""RAI guard and policy tests."""

from __future__ import annotations

import pytest

from oris.core.exceptions import GuardViolationError
from oris.rai.input_guard import InputGuard
from oris.rai.output_guard import OutputGuard
from oris.rai.policy import PolicyEnforcer


def test_input_guard_allows_clean_data() -> None:
    guard = InputGuard()
    payload = {"query": "safe text"}
    assert guard.run(payload) == payload


def test_input_guard_blocks_prohibited_keys() -> None:
    guard = InputGuard()
    with pytest.raises(GuardViolationError):
        guard.run({"password": "123"})


def test_output_guard_blocks_prohibited_terms() -> None:
    guard = OutputGuard()
    with pytest.raises(GuardViolationError):
        guard.run({"output": "this contains malware references"})


def test_policy_enforcer_allows_safe_output() -> None:
    policy = PolicyEnforcer()
    policy.validate_output({"output": "safe output"})


def test_guards_share_policy_instance() -> None:
    policy = PolicyEnforcer(blocked_terms={"banned"})
    input_g = InputGuard(policy=policy)
    output_g = OutputGuard(policy=policy)
    payload = {"query": "ok"}
    mid = input_g.run(payload)
    mid["output"] = "clean"
    assert output_g.run(mid)["output"] == "clean"
