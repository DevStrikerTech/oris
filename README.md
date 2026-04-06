# Oris

Oris is a production-first, open-source Responsible AI runtime framework for executing AI pipelines with safety, observability, and validation built in by default.

## Why Oris

- **Responsible by default**: all pipeline runs pass through input and output guards.
- **Framework-agnostic runtime**: integrate with any pipeline object exposing a `run(...)` method.
- **Production-oriented architecture**: typed interfaces, clear module boundaries, strict CI quality gates.
- **Traceable execution**: run-level and step-level traces for debugging and governance workflows.

## Features

- YAML-defined or embedded pipelines.
- Sequential runtime execution with pluggable orchestrators.
- Component registry for extension and dynamic loading.
- Provider abstraction for model backends.
- Basic policy enforcement for harmful inputs/outputs.
- Audit logging with sensitive-field redaction.
- CLI for running and validating pipeline definitions.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

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

## Project Layout

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

## Development Quality Gates

- `ruff` for linting
- `mypy` with strict mode
- `pytest` and `pytest-cov`
- minimum coverage: **84%**
- pre-commit hooks enforce local quality

## Documentation (web)

Browse the full docs site (built from this repo with **MkDocs**): **[devstrikertech.github.io/oris](https://devstrikertech.github.io/oris/)**  
*(Enable **GitHub Pages** with source **GitHub Actions** in repo settings after the first `prod` deploy; private repos need a paid GitHub plan for Pages.)*

Local preview:

```bash
pip install -e ".[dev]"
bash scripts/sync_doc_sources.sh && mkdocs serve
```

## Governance and Standards

- Engineering standards: `ENGINEERING_STANDARDS.md`
- Security policy: `SECURITY.md`
- Architecture notes: `ARCHITECTURE.md`
- Public API guarantees: `PUBLIC_API.md`
- Release process: `RELEASE.md`
- Contribution process: `CONTRIBUTING.md`

## License

MIT (see project licensing policy in repository root).
