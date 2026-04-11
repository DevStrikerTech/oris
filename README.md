<p align="center">
  <a href="https://devstrikertech.github.io/oris/">
    <img src="docs/images/oris_logo.png" width="180" alt="Oris — Responsible AI pipeline runtime for Python" />
  </a>
</p>

|         |     |
| ------- | --- |
| **CI** | [![CI](https://github.com/DevStrikerTech/oris/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/DevStrikerTech/oris/actions/workflows/ci.yml) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![Coverage](https://img.shields.io/badge/coverage-%E2%89%A584%25-brightgreen.svg)](CONTRIBUTING.md#quality-gates) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) |
| **Docs** | [![Website](https://img.shields.io/website?label=documentation&up_message=online&url=https%3A%2F%2Fdevstrikertech.github.io%2Foris%2F)](https://devstrikertech.github.io/oris/) [![Docs](https://github.com/DevStrikerTech/oris/actions/workflows/docs.yml/badge.svg?branch=prod)](https://github.com/DevStrikerTech/oris/actions/workflows/docs.yml) |
| **Package** | [![PyPI](https://img.shields.io/pypi/v/oris-ai)](https://pypi.org/project/oris-ai/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/oris-ai?logo=python&logoColor=gold)](https://pypi.org/project/oris-ai/) [![License](https://img.shields.io/github/license/DevStrikerTech/oris)](https://github.com/DevStrikerTech/oris/blob/prod/LICENSE) |
| **Meta** | [![Issues](https://img.shields.io/github/issues/DevStrikerTech/oris)](https://github.com/DevStrikerTech/oris/issues) [![GitHub](https://img.shields.io/badge/GitHub-DevStrikerTech%2Foris-181717?logo=github)](https://github.com/DevStrikerTech/oris) |

[Oris](https://devstrikertech.github.io/oris/) is an open-source **Responsible AI** runtime for Python. Describe **pipelines** in YAML (or build them in code), run them through one **executor**, and get **input/output policy checks** and **run and step-level traces** by default.

Oris is **framework-agnostic**: Anything you can invoke like `run(dict)` can use the same boundaries—including external LLM stacks wrapped with **SafeRunner**—so you can experiment locally and ship with clearer safety and observability defaults.

## Table of Contents

- [Installation](#installation)
- [Documentation](#documentation)
- [Features](#features)
- [Quick start](#quick-start)
- [CLI](#cli)
- [Output format](#output-format)
- [SafeRunner](#saferunner)
- [Project layout](#project-layout)
- [Examples and notebooks](#examples-and-notebooks)
- [Contributing](#contributing)
- [License](#license)

## Installation

The simplest way to install Oris is using pip::

```bash
pip install oris-ai
```
Verify the CLI installation:
```bash
oris --help
```

**From source** (library, CLI, and tests):

```bash
git clone https://github.com/DevStrikerTech/oris.git
cd oris
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

**Developers** (lint, types, tests, notebook execution):

```bash
pip install -e ".[dev]"
```

Oris requires **Python 3.10 or newer**. Runtime dependencies are minimal (**PyYAML** only). For a fuller walkthrough, see the [Installation](https://devstrikertech.github.io/oris/get-started/installation/) page in the docs.

## Documentation

If you're new to the project, start with the [**Introduction**](https://devstrikertech.github.io/oris/), then follow [**Installation**](https://devstrikertech.github.io/oris/get-started/installation/) and [**Quickstart**](https://devstrikertech.github.io/oris/get-started/quickstart/) on the documentation site. The [**Concepts**](https://devstrikertech.github.io/oris/concepts/overview/) section explains pipelines, components, providers, RAI, and traces; [**Guides**](https://devstrikertech.github.io/oris/guides/cli/) cover the CLI, SafeRunner, and run summaries.

**Site:** [devstrikertech.github.io/oris](https://devstrikertech.github.io/oris/) (MkDocs Material, similar information architecture to projects like [Haystack](https://docs.haystack.deepset.ai/docs/intro)).

**Preview Locally:**

```bash
pip install -e ".[docs]"
mkdocs serve
```

The **Docs** workflow publishes to GitHub Pages on pushes to **`prod`** ([`.github/workflows/docs.yml`](.github/workflows/docs.yml)). In **Settings → Pages**, choose **GitHub Actions** as the source if needed.

## Features

**YAML-first pipelines**  
Define `steps`, optional `providers`, and `settings` (such as tracing). Configuration is validated before execution; YAML is loaded with `yaml.safe_load` only.

**Guards and policy**  
A default `PolicyEnforcer` applies input checks (blocked keys, basic injection heuristics, simple PII-shaped patterns) and output checks (blocked terms and test-oriented stubs). The same policy surface is used by **SafeRunner** for external callables.

**Built-in components and provider stubs**  
Use `passthrough`, `template_response`, and `generate` / `llm_echo` from the default registry. Declared `openai` / `huggingface` provider types are **stubs** (no network I/O in the core package) so CI and demos stay reproducible.

**Observability**  
Each run produces a `RunTrace` with per-step latency, status, and flags. `PipelineResult.to_run_summary()` gives a stable JSON-oriented shape for logs and the CLI (with optional redaction of sensitive-looking keys).

**CLI parity**  
`oris validate` and `oris run` use the same definitions as `Pipeline.from_yaml` in Python, with `--format pretty` and `--debug` for human-friendly output and stderr trace lines.

## *Quick Start*

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

**Python**

```python
from oris import Pipeline

pipeline = Pipeline.from_yaml("pipeline.yaml")
result = pipeline.run({"query": "What is responsible AI?"})

print(result.output)
```

**CLI**

```bash
oris validate pipeline.yaml
oris run pipeline.yaml --input-json '{"query":"What is responsible AI?"}'
oris run pipeline.yaml --input-json '{"query":"hi"}' --format pretty --debug
```

`--debug` prints trace-oriented details on **stderr**; stdout remains the JSON summary. Sample YAML and notebooks live under [`examples/`](examples/).

## CLI

| Command | Purpose |
| :--- | :--- |
| `oris validate <file.yaml>` | Load and validate the pipeline (schema, components, providers). |
| `oris run <file.yaml> --input-json '<json object>'` | Run with a JSON object as input; by default, stdout returns a compact JSON summary. |
| `oris run ... --format pretty` | Pretty-printed JSON summary. |
| `oris run ... --debug` | Stderr: `run_id`, trace status, per-step latency and flags. |
| `oris validate ... --debug` | Stderr: pipeline name and step list. |

## Output format

`Pipeline.run` returns a **`PipelineResult`**: `output` (dict), `trace` (`RunTrace`), and `metadata`. See [`models.py`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/runtime/models.py).

`result.to_run_summary()` includes:

- **`run_id`** — Run identifier.
- **`status`** — `"success"` or `"failed"` from trace status.
- **`output`** — Final payload (CLI may redact nested sensitive-looking keys).
- **`trace`** — Per-step entries: `step_id`, `component_name`, `status`, `latency_ms`, `flags`.

CLI formatting and redaction: [`output.py`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/cli/output.py).

## SafeRunner

**[`SafeRunner`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/integrations/safe_runner.py)** wraps external inference or tools with the same **`PolicyEnforcer`** as the main executor—validate input, run a callable or `run(dict)` target, validate output, optionally attach a one-step trace.

```python
from oris.integrations import SafeRunner
from oris.rai.policy import PolicyEnforcer

def my_external_llm(payload: dict) -> dict:
    q = payload.get("query", "")
    return {"output": f"stub response for: {q!r}"}

runner = SafeRunner(my_external_llm, policy=PolicyEnforcer())

plain = runner.run({"query": "Hello"})
traced = runner.run({"query": "Hello"}, include_trace=True)
```

Returns are normalized to `dict` from mappings or Pydantic-style `model_dump()`. More detail: [SafeRunner guide](https://devstrikertech.github.io/oris/guides/safe-runner/).

## Project layout

| Area | Role |
| :--- | :--- |
| `oris.core` | Shared enums and exceptions. |
| `oris.components` | Component registry and built-ins. |
| `oris.pipeline` | YAML loading, schema, plan, builder. |
| `oris.runtime` | Executor, orchestrator, hooks, trace manager, `PipelineResult`. |
| `oris.rai` | `PolicyEnforcer`, input/output guards. |
| `oris.providers` | `LLMProvider` and built-in YAML provider stubs. |
| `oris.integrations` | `SafeRunner`. |
| `oris.tracing` | Run and step trace models. |
| `oris.cli` | `oris` CLI entrypoint. |

## Examples and notebooks

| Asset | Description |
| :--- | :--- |
| [`examples/simple_generation.yaml`](examples/simple_generation.yaml) | Template step; good first `Pipeline.run`. |
| [`examples/provider_pipeline.yaml`](examples/provider_pipeline.yaml) | Provider declaration + `generate` (needs `OPENAI_API_KEY` for the stub). |
| [`examples/basic_pipeline.ipynb`](examples/basic_pipeline.ipynb) | YAML → run → `to_run_summary()`. |
| [`examples/safe_runner.ipynb`](examples/safe_runner.ipynb) | SafeRunner, traces, policy violations. |
| [`examples/llm_integration.ipynb`](examples/llm_integration.ipynb) | Optional Ollama + mock fallback; YAML provider stub. |

Execute notebooks from the repo root (after `pip install -e ".[dev]"`):

```bash
export JUPYTER_CONFIG_DIR="$PWD/.jupyter" && mkdir -p .jupyter
python -m nbconvert --to notebook --execute examples/basic_pipeline.ipynb --inplace
```

Repeat for the other notebooks, or open them in your editor.

## Contributing

We welcome issues and pull requests. Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) (branches, quality gates, tests). Report security issues per [`SECURITY.md`](SECURITY.md). Community expectations: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

MIT — see [`LICENSE`](LICENSE).
