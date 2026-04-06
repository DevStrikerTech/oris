# Public API Contract

## Stability Scope

The following interfaces are considered the initial public API for Oris:

- `oris.Pipeline`
- `oris.runtime.PipelineExecutor` (alias: `RuntimeExecutor`)
- `oris.runtime.PipelineResult`
- `oris.runtime.ExecutionContext`
- `oris.runtime.Hook` and hook ABCs (`PreStepHook`, `PostStepHook`, `PipelinePreHook`, `PipelinePostHook`) plus `Callable*Hook` / `as_*_hook` helpers
- `oris.runtime.TraceManager`
- `oris.integrations.SafeRunner`
- CLI command `oris`

Legacy aliases `PreExecutionHook`, `PostExecutionHook`, `ExecutionHook`, and `PipelineHook` remain available for compatibility; prefer the explicit hook names above.

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

- `SafeRunner(external_pipeline, *, policy: PolicyEnforcer)`
- `run(input_data: dict[str, Any]) -> dict[str, Any]`

`external_pipeline` must implement a `run(...)` method returning a mapping. Validation uses the same `PolicyEnforcer.validate_input` / `validate_output` entry points as the default executor pipeline hooks. Tracing is not part of this wrapper by design.

### Runtime hooks

- Hooks are objects implementing `invoke(self, data: dict[str, Any], context: ExecutionContext) -> dict[str, Any]` on the appropriate ABC.
- `RuntimeExecutor` accepts hook instances or plain callables (wrapped internally) per parameter: `pre_step_hooks`, `post_step_hooks`, `pipeline_pre_hooks`, `pipeline_post_hooks`, `rai_pre_hooks`, `rai_post_hooks`.

## CLI API

- `oris run <pipeline.yaml> [--input-json '{"key":"value"}']`
- `oris validate <pipeline.yaml>`

CLI output format:

- `run`: JSON run summary to stdout (`run_id`, `status`, `output`, `trace`; see `PipelineResult.to_run_summary()`)
- `validate`: human-readable success message

## Versioning Policy

Oris follows semantic versioning:

- major: breaking public API changes
- minor: backward-compatible features
- patch: backward-compatible fixes

Public API changes require updates to this document and release notes.
