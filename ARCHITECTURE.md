# Oris Architecture

## Goals

Oris is built as a modular Responsible AI runtime for production deployments:

- enforce safety controls by default
- remain framework-agnostic
- provide deterministic and testable execution
- support auditability and extensibility

## High-Level Modules

- `core/`: shared enums, exceptions, and domain primitives.
- `components/`: abstract component contract and registry for pipeline steps.
- `runtime/`: executor, orchestrator, execution context, hook ABCs, `StepRunner`, `TraceManager`, and result model.
- `rai/`: policy enforcement, input guard, output guard.
- `providers/`: LLM provider abstraction and backend stubs.
- `integrations/`: wrappers for external runtimes (`SafeRunner`).
- `tracing/`: run and step traces, audit logger.
- `cli/`: command-line operations (`run`, `validate`).
- `api/`: reserved for API adapters.

## Execution Flow

1. Load pipeline config from YAML or in-memory mapping.
2. Validate schema and component declarations.
3. Build components from registry; each component’s `validate_config(config)` runs at construction (via `__post_init__`).
4. `RuntimeExecutor` calls `TraceManager.begin_run()` for the only `RunTrace` construction path used by the executor; it builds `ExecutionContext` (run id, plan metadata, shared trace, injected `PolicyEnforcer`, step pointers).
5. Run **pipeline pre-hooks** (default: `InputPolicyHook` as `PipelinePreHook`, then optional RAI pre-hooks). Each hook implements `Hook.invoke(data, context)`; plain callables are wrapped at executor construction.
6. For each plan step: **pre-step hooks** (`PreStepHook`) → component (via `PipelineOrchestrator` and `Component.run`) → **post-step hooks** (`PostStepHook`). `TraceManager.traced_hook` records hook steps; `TraceManager.traced_component` records the component body (success or failure) so step traces are not assembled outside `TraceManager`.
7. Run **pipeline post-hooks** (optional RAI post-hooks, then default `OutputPolicyHook` as `PipelinePostHook`).
8. `TraceManager.finalize_success` / `finalize_failure` close the run; run metadata attachment for summaries is applied inside `finalize_success` when provided.

## Design Decisions

- **Safety-first runtime**: default pipeline hooks enforce input/output policy; overrides are explicit via `pipeline_pre_hooks` / `pipeline_post_hooks`.
- **Framework independence**: `SafeRunner` uses a protocol, not framework imports; policy is injected and uses the same `PolicyEnforcer` entry points as default pipeline hooks.
- **Strict typing**: complete type hints and strict static analysis (`mypy --strict`).
- **Explicit failure states**: domain-specific exception hierarchy; hook kind mismatches raise `TypeError` at executor construction when a wrong `Hook` subclass is used.
- **No global mutable state**: dependency injection through constructors.
- **ExecutionContext** is a small, documented surface (`run_id`, `metadata`, `trace`, `policy`, `current_step_id`, `step_index`); extend runs via `metadata` keys rather than ad-hoc bags.

## Extensibility Model

- Register custom components via `ComponentRegistry`; override `validate_config(self, config)` with explicit dict validation.
- Add new providers by implementing `LLMProvider`.
- Replace `PipelineOrchestrator` with custom execution strategies.
- Extend policy checks through `PolicyEnforcer` or register hooks: subclass `PreStepHook`, `PostStepHook`, `PipelinePreHook`, or `PipelinePostHook`, or pass callables (wrapped to `Callable*Hook`).
- Use `InputGuard` / `OutputGuard` as components when not using the default hook chain.

## Security Boundaries

- YAML parsing is performed using `yaml.safe_load`.
- config is validated before execution.
- audit logs redact known sensitive keys.
- credentials are expected from environment variables or secret stores.

## Future Evolution (Non-Breaking)

- stronger schema validation for pipeline documents
- richer policy engines (tenant- and domain-specific)
- trace export adapters (OpenTelemetry, SIEM pipelines)
- signed policy bundles and provenance verification
