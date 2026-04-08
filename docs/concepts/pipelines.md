# Pipelines & YAML

Pipelines are described as YAML documents (or equivalent dicts via `Pipeline.from_config`). The schema enforces allowed keys and step shape before anything runs.

## Top-level keys

| Key | Purpose |
| :--- | :--- |
| `name` | Logical pipeline name (metadata). |
| `settings` | e.g. `device`, `tracing` (boolean). |
| `metadata` | Optional arbitrary metadata block. |
| `providers` | Named provider declarations for LLM-backed steps. |
| `steps` | Ordered list of steps (**canonical** format). |
| `components` | Legacy list form; prefer `steps` for new work. |

## Canonical `steps` item

Each step typically includes:

- **`id`** — Stable identifier for traces and debugging.  
- **`type`** — Component type key in the registry (e.g. `template_response`, `generate`).  
- **`provider`** — Logical provider id when the component needs a backend.  
- **`config`** — Component-specific configuration (validated per component).  

Example:

```yaml
name: demo
settings:
  tracing: true
steps:
  - id: answer
    type: template_response
    config:
      template: "Response: {query}"
```

## Safe loading

Configs are loaded with **`yaml.safe_load`** only—no arbitrary Python objects from YAML.

## Related

- [**Quickstart**](../get-started/quickstart.md) — minimal runnable file  
- [**Components & providers**](components.md) — how `type` and `provider` resolve  
- [**CLI reference**](../guides/cli.md) — `oris validate` / `oris run`  
