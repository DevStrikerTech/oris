"""Strict pipeline YAML schema: parse and normalize to builder-ready structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from oris.core.exceptions import ConfigurationError

TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {"providers", "steps", "components", "name", "metadata", "settings"},
)

# Legacy component list items (strict allowlist).
LEGACY_STEP_KEYS: frozenset[str] = frozenset({"id", "name", "type", "provider", "config"})

# Canonical steps list items.
STEPS_FORMAT_KEYS: frozenset[str] = frozenset({"id", "type", "provider", "config", "name"})

SETTINGS_KEYS: frozenset[str] = frozenset({"device", "tracing"})

# Declared YAML component type -> registry key (builtin aliases).
COMPONENT_TYPE_ALIASES: dict[str, str] = {
    "generate": "llm_echo",
}


def _err(msg: str) -> None:
    raise ConfigurationError(msg)


def _resolve_component_type(declared: str) -> str:
    key = declared.strip().lower()
    return COMPONENT_TYPE_ALIASES.get(key, key)


@dataclass(frozen=True, slots=True)
class PipelineSettings:
    """Global pipeline settings with explicit defaults (no silent critical defaults)."""

    device: str
    tracing: bool


@dataclass(frozen=True, slots=True)
class StepSpec:
    """One validated step: trace id, registry type, component name, and config for the builder."""

    step_id: str
    component_type: str
    component_name: str
    config: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ParsedPipeline:
    """Validated pipeline document."""

    steps: list[StepSpec]
    providers: dict[str, Any] | None
    name: Any
    metadata: dict[str, Any] | None
    settings: PipelineSettings


def _validate_providers_block(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        _err("Invalid pipeline config: top-level 'providers' must be a mapping.")
    providers_raw: dict[str, Any] = raw
    for logical_id, block in providers_raw.items():
        if not isinstance(logical_id, str) or not logical_id.strip():
            _err("Invalid pipeline config: provider ids must be non-empty strings.")
        path = f"providers.{logical_id.strip()}"
        if not isinstance(block, dict):
            _err(f"Invalid pipeline config: provider declaration at {path} must be a mapping.")
        ptype = block.get("type")
        if not isinstance(ptype, str) or not ptype.strip():
            _err(f"Invalid pipeline config: missing required field 'type' at {path}.")
    return providers_raw


def _parse_settings(raw: Any) -> PipelineSettings:
    if raw is None:
        return PipelineSettings(device="auto", tracing=True)
    if not isinstance(raw, dict):
        _err("Invalid pipeline config: top-level 'settings' must be a mapping.")
    unknown = set(raw.keys()) - SETTINGS_KEYS
    if unknown:
        _err(
            f"Invalid pipeline config: unknown keys in settings: {sorted(unknown)}.",
        )
    device = raw.get("device", "auto")
    if not isinstance(device, str) or not device.strip():
        _err("Invalid pipeline config: settings.device must be a non-empty string.")
    tracing = raw.get("tracing", True)
    if not isinstance(tracing, bool):
        _err("Invalid pipeline config: settings.tracing must be a boolean.")
    return PipelineSettings(device=device.strip(), tracing=tracing)


def _parse_metadata(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        _err("Invalid pipeline config: top-level 'metadata' must be a mapping.")
    meta: dict[str, Any] = raw
    return meta


def _strict_step_unknown(
    item: dict[str, Any],
    *,
    path_prefix: str,
    allowed: frozenset[str],
) -> None:
    unknown = set(item.keys()) - allowed
    if unknown:
        _err(
            f"Invalid pipeline config: unknown fields {sorted(unknown)} at {path_prefix}.",
        )


def _merge_provider_into_config(
    base_config: dict[str, Any],
    provider: str | None,
    *,
    path: str,
) -> dict[str, Any]:
    out = dict(base_config)
    if provider is None:
        return out
    pid = provider.strip()
    if not pid:
        _err(f"Invalid pipeline config: 'provider' must be a non-empty string at {path}.")
    if "provider" in out and out["provider"] != pid:
        _err(
            f"Invalid pipeline config: conflicting 'provider' at {path} "
            "(set either top-level 'provider' or config.provider, not both).",
        )
    out["provider"] = pid
    return out


def _parse_steps_format(raw_steps: list[Any]) -> list[StepSpec]:
    if not raw_steps:
        _err("Invalid pipeline config: 'steps' must be a non-empty list.")
    seen_ids: set[str] = set()
    result: list[StepSpec] = []
    for index, raw in enumerate(raw_steps):
        path = f"steps[{index}]"
        if not isinstance(raw, dict):
            _err(f"Invalid pipeline config: each step must be a mapping at {path}.")
        _strict_step_unknown(raw, path_prefix=path, allowed=STEPS_FORMAT_KEYS)
        sid = raw.get("id")
        if not isinstance(sid, str) or not sid.strip():
            _err(f"Invalid pipeline config: missing required field 'id' at {path}.")
        step_id = sid.strip()
        if step_id in seen_ids:
            _err(f"Invalid pipeline config: duplicate step id '{step_id}'.")
        seen_ids.add(step_id)
        typ = raw.get("type")
        if not isinstance(typ, str) or not typ.strip():
            _err(f"Invalid pipeline config: missing required field 'type' at {path}.")
        cfg = raw.get("config", {})
        if cfg is None:
            cfg = {}
        if not isinstance(cfg, dict):
            _err(f"Invalid pipeline config: field 'config' must be a mapping at {path}.")
        top_provider = raw.get("provider")
        if top_provider is not None and not isinstance(top_provider, str):
            _err(f"Invalid pipeline config: field 'provider' must be a string at {path}.")
        merged = _merge_provider_into_config(cfg, top_provider, path=path)
        name_raw = raw.get("name")
        if name_raw is not None:
            if not isinstance(name_raw, str) or not name_raw.strip():
                _err(f"Invalid pipeline config: field 'name' must be a non-empty string at {path}.")
            component_name = name_raw.strip()
        else:
            component_name = step_id
        resolved_type = _resolve_component_type(typ)
        result.append(
            StepSpec(
                step_id=step_id,
                component_type=resolved_type,
                component_name=component_name,
                config=merged,
            ),
        )
    return result


def _parse_components_format(raw_components: list[Any]) -> list[StepSpec]:
    if not raw_components:
        _err("Invalid pipeline config: 'components' must be a non-empty list.")
    seen_explicit_ids: set[str] = set()
    result: list[StepSpec] = []
    for index, raw in enumerate(raw_components):
        path = f"components[{index}]"
        if not isinstance(raw, dict):
            _err(f"Invalid pipeline config: each component must be a mapping at {path}.")
        _strict_step_unknown(raw, path_prefix=path, allowed=LEGACY_STEP_KEYS)
        typ = raw.get("type")
        if not isinstance(typ, str) or not typ.strip():
            _err(f"Invalid pipeline config: missing required field 'type' at {path}.")
        cfg = raw.get("config", {})
        if cfg is None:
            cfg = {}
        if not isinstance(cfg, dict):
            _err(f"Invalid pipeline config: field 'config' must be a mapping at {path}.")
        top_provider = raw.get("provider")
        if top_provider is not None and not isinstance(top_provider, str):
            _err(f"Invalid pipeline config: field 'provider' must be a string at {path}.")
        merged = _merge_provider_into_config(cfg, top_provider, path=path)
        id_raw = raw.get("id")
        name_raw = raw.get("name")
        explicit_id: str | None = None
        if id_raw is not None:
            if not isinstance(id_raw, str) or not id_raw.strip():
                _err(f"Invalid pipeline config: field 'id' must be a non-empty string at {path}.")
            explicit_id = id_raw.strip()
            if explicit_id in seen_explicit_ids:
                _err(f"Invalid pipeline config: duplicate step id '{explicit_id}'.")
            seen_explicit_ids.add(explicit_id)
        if name_raw is not None and not isinstance(name_raw, str):
            _err(f"Invalid pipeline config: field 'name' must be a string at {path}.")
        component_name = (
            name_raw.strip()
            if isinstance(name_raw, str) and name_raw.strip()
            else (explicit_id if explicit_id is not None else f"component_{index}")
        )
        step_id = explicit_id if explicit_id is not None else f"step_{index}"
        resolved_type = _resolve_component_type(typ)
        result.append(
            StepSpec(
                step_id=step_id,
                component_type=resolved_type,
                component_name=component_name,
                config=merged,
            ),
        )
    return result


def parse_pipeline_dict(raw: dict[str, Any]) -> ParsedPipeline:
    """Parse and strictly validate a pipeline mapping; raise ``ConfigurationError`` on failure."""
    unknown = set(raw.keys()) - TOP_LEVEL_KEYS
    if unknown:
        _err(
            f"Invalid pipeline config: unsupported top-level keys: {sorted(unknown)}.",
        )

    has_steps = "steps" in raw and raw["steps"] is not None
    has_components = "components" in raw and raw["components"] is not None
    if has_steps and has_components:
        _err(
            "Invalid pipeline config: specify only one of 'steps' or 'components'.",
        )
    if not has_steps and not has_components:
        _err(
            "Invalid pipeline config: require a non-empty 'steps' or 'components' list.",
        )

    providers = _validate_providers_block(raw.get("providers"))
    settings = _parse_settings(raw.get("settings"))
    metadata = _parse_metadata(raw.get("metadata"))

    if has_steps:
        rs = raw["steps"]
        if not isinstance(rs, list):
            _err("Invalid pipeline config: 'steps' must be a list.")
        steps = _parse_steps_format(rs)
    else:
        rc = raw["components"]
        if not isinstance(rc, list):
            _err("Invalid pipeline config: 'components' must be a list.")
        steps = _parse_components_format(rc)

    return ParsedPipeline(
        steps=steps,
        providers=providers,
        name=raw.get("name"),
        metadata=metadata,
        settings=settings,
    )


def parsed_pipeline_to_build_config(parsed: ParsedPipeline) -> dict[str, Any]:
    """Build the mapping expected by ``build_provider_instances`` / ``instantiate_components``."""
    components: list[dict[str, Any]] = []
    for step in parsed.steps:
        components.append(
            {
                "type": step.component_type,
                "name": step.component_name,
                "config": dict(step.config),
            },
        )
    out: dict[str, Any] = {"components": components}
    if parsed.providers is not None:
        out["providers"] = parsed.providers
    if parsed.name is not None:
        out["name"] = parsed.name
    if parsed.metadata is not None:
        out["metadata"] = dict(parsed.metadata)
    return out
