# Oris documentation

**Oris** is a production-oriented **Responsible AI** pipeline runtime for Python. Install from PyPI as **`oris-ai`**.

!!! note "Source of truth"
    Pages are built from markdown in this repository. Engineering docs under **Architecture** through **Contributing** are synced from the repo root during the docs build.

## Highlights

- **RAI by default** — input and output guards on every run  
- **YAML or in-memory** pipelines — pluggable components and registry  
- **Tracing** — run and step traces for observability  
- **CLI** — `oris validate` / `oris run`  

## Install

```bash
pip install oris-ai
```

## Quick start

**`example.yaml`:**

```yaml
name: basic_pipeline
components:
  - type: passthrough
    name: normalize_input
  - type: template_response
    name: responder
    config:
      template: "AI answer placeholder for: {query}"
```

**Python:**

```python
from oris import Pipeline

result = Pipeline.from_yaml("example.yaml").run({"query": "What is AI?"})
print(result.output)
```

**CLI:**

```bash
oris validate example.yaml
oris run example.yaml --input-json '{"query":"What is AI?"}'
```

## Site map

Use the navigation bar for **Architecture**, **Public API**, **Security**, **Releases**, and **Contributing**.

## Repository

[github.com/DevStrikerTech/oris](https://github.com/DevStrikerTech/oris)
