"""Built-in component registry tests."""

from oris.components.builtin import create_builtin_registry


def test_builtin_registry_has_standard_types() -> None:
    registry = create_builtin_registry()
    assert "passthrough" in registry.keys()
    assert "template_response" in registry.keys()
    assert "llm_echo" in registry.keys()
    assert "generate" in registry.keys()
