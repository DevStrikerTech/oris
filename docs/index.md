---
hide:
  - navigation.path
---

# Introduction to Oris

**Oris** is an open-source **Responsible AI** pipeline **runtime** for Python. You define pipelines as YAML or build them in code: each run moves through validation, guards, execution, and tracing so you can ship AI workflows with clearer safety and observability defaults.

The core ideas are **components** wired into a **pipeline**, **providers** for backends, **RAI guards** on inputs and outputs, and **traces** at run and step granularity. Oris stays **framework-agnostic** at the boundary you integrate with: anything that can be invoked like a `run(...)` step can participate in the same executor model.

If you already know you want to try it, skip ahead to **[Install](#install)** and **[Quick start](#quick-start)**. For depth on design and guarantees, use the left-hand navigation — **Architecture**, **Public API**, **Security**, **Provider design**, **Releases**, and **Contributing** are synced from the repository root on every docs build.

![Oris logo](oris_logo.png){ width="140" }

!!! note "Built from this repository"
    These pages are generated with **MkDocs Material**. Policy and design pages (**Architecture** through **Code of Conduct**, including **Provider design**) are copied from the repo root during `scripts/sync_doc_sources.sh` (including in CI), so the site matches `prod` sources. Only **`index.md`** and assets under **`docs/`** are edited in place.

## What you can build with Oris

**Production-style pipeline runs**  
Load YAML definitions or construct pipelines programmatically, then execute with a single `run` API and consistent error and trace shapes.

**Guarded execution**  
Apply input and output policies so risky or sensitive content is checked before and after model-facing steps.

**Observable workflows**  
Inspect run and step traces to debug behavior and support governance without ad hoc logging only.

**CLI and library use**  
Validate definitions and run pipelines from the terminal, or embed Oris in services with the same definitions.

## Install

```bash
pip install oris-ai
```

For working on Oris itself, clone the repo and use an editable install:

```bash
pip install -e ".[dev]"
```

## Quick start

Save the following as **`pipeline.yaml`** (any path you prefer):

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

**Python** (from the same directory as the file):

```python
from oris import Pipeline

result = Pipeline.from_yaml("pipeline.yaml").run({"query": "What is AI?"})
print(result.output)
```

**CLI:**

```bash
oris validate pipeline.yaml
oris run pipeline.yaml --input-json '{"query":"What is AI?"}'
```

## Next steps

| Goal | Where to go |
| :--- | :--- |
| System shape and modules | [Architecture](ARCHITECTURE.md) |
| Stable surface for integrators | [Public API](PUBLIC_API.md) |
| Provider YAML, registry, and injection | [Provider design](PROVIDER_DESIGN.md) |
| Reporting vulnerabilities | [Security](SECURITY.md) |
| Releases and versioning | [Releases](RELEASE.md) |
| How to contribute | [Contributing](CONTRIBUTING.md) |

## Repository

Source and issues: [github.com/DevStrikerTech/oris](https://github.com/DevStrikerTech/oris)
