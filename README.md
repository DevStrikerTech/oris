<div align="center">
  <a href="https://devstrikertech.github.io/oris/"><img src="docs/oris_logo.png" alt="Oris — Responsible AI pipeline runtime for Python" width="160"></a>

| | |
| :--- | :--- |
| **CI** | [![CI](https://github.com/DevStrikerTech/oris/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/DevStrikerTech/oris/actions/workflows/ci.yml) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![Coverage](https://img.shields.io/badge/coverage-%E2%89%A584%25-brightgreen.svg)](#development-quality-gates) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) |
| **Docs** | [![Documentation](https://img.shields.io/website?label=documentation&up_message=online&url=https%3A%2F%2Fdevstrikertech.github.io%2Foris%2F)](https://devstrikertech.github.io/oris/) [![Oris docs](https://github.com/DevStrikerTech/oris/actions/workflows/oris-docs.yml/badge.svg?branch=prod)](https://github.com/DevStrikerTech/oris/actions/workflows/oris-docs.yml) |
| **Package** | [![PyPI](https://img.shields.io/pypi/v/oris-ai)](https://pypi.org/project/oris-ai/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/oris-ai?logo=python&logoColor=gold)](https://pypi.org/project/oris-ai/) [![License](https://img.shields.io/github/license/DevStrikerTech/oris)](https://github.com/DevStrikerTech/oris/blob/prod/LICENSE) |
| **Meta** | [![Issues](https://img.shields.io/github/issues/DevStrikerTech/oris)](https://github.com/DevStrikerTech/oris/issues) [![Repository](https://img.shields.io/badge/GitHub-DevStrikerTech%2Foris-181717?logo=github)](https://github.com/DevStrikerTech/oris) |
</div>

**Oris** is an open-source **Responsible AI** runtime for Python: define pipelines in YAML or in code, run them through a framework-agnostic executor, and keep **safety, observability, and validation** on by default.

Design sequential pipelines with pluggable components, provider backends, and guardrails on inputs and outputs. Use the CLI for validate/run flows, or embed **Oris** in your own services with typed APIs and run- and step-level tracing for debugging and governance.

## Table of contents

- [Why Oris](#why-oris)
- [Features](#features)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Documentation (web)](#documentation-web)
- [Project layout](#project-layout)
- [Development quality gates](#development-quality-gates)
- [Governance and standards](#governance-and-standards)
- [License](#license)

## Why Oris

- **Responsible by default**: pipeline runs pass through input and output guards.
- **Framework-agnostic runtime**: integrate with any object that exposes a `run(...)`-style entry point.
- **Production-oriented architecture**: typed interfaces, clear module boundaries, strict CI quality gates.
- **Traceable execution**: run-level and step-level traces for debugging and governance workflows.

## Features

**YAML or embedded pipelines**  
Describe components and wiring in YAML, or build pipelines in Python with the same registry and executor.

**Guards and policy**  
Basic policy hooks for harmful or sensitive inputs and outputs, with audit logging and redaction of sensitive fields.

**Extensible components**  
Registry-based components, provider abstraction for model backends, and a CLI for `validate` and `run`.

**Observability**  
Structured traces across the run so you can reason about what executed and when.

## Installation

For library and CLI use from [PyPI](https://pypi.org/project/oris-ai/):

```bash
pip install oris-ai
```

For contributing or running tests from a clone:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Quick start

`example.yaml`:

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

Python:

```python
from oris import Pipeline

pipeline = Pipeline.from_yaml("example.yaml")

result = pipeline.run({
    "query": "What is AI?"
})

print(result.output)
```

CLI:

```bash
oris validate example.yaml
oris run example.yaml --input-json '{"query":"What is AI?"}'
```

## Documentation (web)

The full site (architecture, public API, security, releases, contributing) is published with **MkDocs Material**: **[devstrikertech.github.io/oris](https://devstrikertech.github.io/oris/)**.

Private repositories need a GitHub plan that includes **GitHub Pages**; in repo settings choose **Pages → Build and deployment → GitHub Actions** after the first successful deploy from `prod`.

Local preview:

```bash
pip install -e ".[dev]"
bash scripts/sync_doc_sources.sh && mkdocs serve
```

## Project layout

```text
oris/
├── src/oris/
│   ├── core/
│   ├── runtime/
│   ├── components/
│   ├── providers/
│   ├── rai/
│   ├── integrations/
│   ├── tracing/
│   ├── cli/
│   └── api/
├── tests/
├── examples/
├── docs/
└── .github/workflows/
```

## Development quality gates

- `ruff` for linting and format checks
- `mypy` in strict mode
- `pytest` and `pytest-cov` with a minimum of **84%** coverage
- `pre-commit` hooks for local checks

## Governance and standards

- Engineering standards: `ENGINEERING_STANDARDS.md`
- Security policy: `SECURITY.md`
- Architecture notes: `ARCHITECTURE.md`
- Public API guarantees: `PUBLIC_API.md`
- Release process: `RELEASE.md`
- Contribution process: `CONTRIBUTING.md`

## License

MIT — see [`LICENSE`](https://github.com/DevStrikerTech/oris/blob/prod/LICENSE) in the repository root.
