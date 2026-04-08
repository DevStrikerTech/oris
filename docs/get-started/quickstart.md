# Quickstart

This page walks through a **minimal YAML pipeline**, running it from **Python** and the **CLI**.

## 1. Create a pipeline file

Save as `pipeline.yaml`:

```yaml
name: quickstart
settings:
  tracing: true
steps:
  - id: reply
    type: template_response
    config:
      template: "Answer placeholder for: {query}"
```

The `template_response` component fills an `output` field from the `{query}` placeholder in your input payload.

## 2. Run from Python

```python
from oris import Pipeline

pipeline = Pipeline.from_yaml("pipeline.yaml")
result = pipeline.run({"query": "What is responsible AI?"})

print(result.output)
```

You should see a dict that includes your original `query` and a string `output` from the template.

## 3. Run from the CLI

```bash
oris validate pipeline.yaml
oris run pipeline.yaml --input-json '{"query":"What is responsible AI?"}'
```

Pretty-printed JSON and debug-style trace lines on stderr:

```bash
oris run pipeline.yaml --input-json '{"query":"hi"}' --format pretty --debug
```

## 4. Inspect structured output

```python
summary = result.to_run_summary()
print(summary["status"], summary["run_id"])
print(summary["trace"])
```

See [**Runs, output & traces**](../guides/output.md) for the full summary shape.

## Sample files in the repo

The repository includes ready-made YAML under [`examples/`](https://github.com/DevStrikerTech/oris/tree/dev/examples) and Jupyter notebooks you can execute locally—see [**Examples**](../examples/index.md).

## Next

- [**Concepts overview**](../concepts/overview.md) — how pieces fit together  
- [**CLI reference**](../guides/cli.md) — all `oris` subcommands  
- [**SafeRunner**](../guides/safe-runner.md) — wrap external LLM code with the same policy checks  
