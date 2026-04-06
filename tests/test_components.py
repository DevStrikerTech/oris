"""Component and registry tests."""

from __future__ import annotations

import pytest

from oris.components.base import Component
from oris.components.registry import ComponentRegistry
from oris.components.standard import PassthroughComponent, TemplateResponseComponent
from oris.core.exceptions import ConfigurationError
from oris.runtime.context import ExecutionContext
from tests.helpers import trivial_execution_context


class DummyComponent(Component):
    def run(self, data: dict[str, object], context: ExecutionContext) -> dict[str, object]:
        _ = context
        out = dict(data)
        out["dummy"] = True
        return out


def test_registry_register_and_create() -> None:
    registry = ComponentRegistry()
    registry.register("dummy", DummyComponent)
    instance = registry.create("dummy", name="dummy", config={})
    ctx = trivial_execution_context()
    result = instance.run({}, ctx)
    assert result["dummy"] is True


def test_registry_rejects_missing_component() -> None:
    registry = ComponentRegistry()
    with pytest.raises(ConfigurationError):
        registry.get("unknown")


def test_template_component_sets_output() -> None:
    component = TemplateResponseComponent(name="templater", config={"template": "Answer: {query}"})
    ctx = trivial_execution_context()
    result = component.run({"query": "What is AI?"}, ctx)
    assert result["output"] == "Answer: What is AI?"


def test_passthrough_component_no_change() -> None:
    component = PassthroughComponent(name="passthrough")
    payload = {"a": 1}
    ctx = trivial_execution_context()
    assert component.run(payload, ctx) == payload


def test_template_component_rejects_bad_template() -> None:
    with pytest.raises(ConfigurationError):
        TemplateResponseComponent(name="bad", config={"template": "{unknown}"})


def test_validate_config_validates_passed_dict_not_only_constructor() -> None:
    """``validate_config(config)`` is explicit so callers/tests can validate arbitrary mappings."""
    component = TemplateResponseComponent(
        name="t",
        config={"template": "Hello {query}"},
    )
    with pytest.raises(ConfigurationError):
        component.validate_config({"template": "{bad_field}"})


def test_validate_config_non_string_template_message() -> None:
    with pytest.raises(ConfigurationError, match="string"):
        TemplateResponseComponent(name="t", config={}).validate_config({"template": 123})
