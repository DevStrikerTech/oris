# Public API Contract

## Stability Scope

The following interfaces are considered the initial public API for Oris:

- `oris.Pipeline`
- `oris.runtime.PipelineExecutor`
- `oris.runtime.PipelineResult`
- `oris.integrations.SafeRunner`
- CLI command `oris`

Anything not listed here is internal and may change between minor versions.

## Python API

### `Pipeline`

- `Pipeline.from_yaml(path: str | Path) -> Pipeline`
- `Pipeline.from_config(config: dict[str, Any]) -> Pipeline`
- `Pipeline.run(input_data: dict[str, object]) -> PipelineResult`

### `PipelineResult`

- `output: dict[str, Any]`
- `trace: RunTrace`
- `metadata: dict[str, Any]`

### `SafeRunner`

- `SafeRunner(external_pipeline)`
- `run(input_data: dict[str, Any]) -> dict[str, Any]`

`external_pipeline` must implement a `run(...)` method returning a mapping.

## CLI API

- `oris run <pipeline.yaml> [--input-json '{"key":"value"}']`
- `oris validate <pipeline.yaml>`

CLI output format:

- `run`: JSON payload to stdout
- `validate`: human-readable success message

## Versioning Policy

Oris follows semantic versioning:

- major: breaking public API changes
- minor: backward-compatible features
- patch: backward-compatible fixes

Public API changes require updates to this document and release notes.
