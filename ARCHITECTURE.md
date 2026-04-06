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
- `runtime/`: executor, orchestrator, execution context, hooks, `StepRunner`, `TraceManager`, and result model.
- `rai/`: policy enforcement, input guard, output guard.
- `providers/`: LLM provider abstraction and backend stubs.
- `integrations/`: wrappers for external runtimes (`SafeRunner`).
- `tracing/`: run and step traces, audit logger.
- `cli/`: command-line operations (`run`, `validate`).
- `api/`: reserved for API adapters.

## Execution Flow

1. Load pipeline config from YAML or in-memory mapping.
2. Validate schema and component declarations.
3. Build components from registry.
4. `RuntimeExecutor` creates a `RunTrace` and `ExecutionContext` (including injected `PolicyEnforcer`).
5. Run **pipeline pre-hooks** (default: input policy validation via `InputPolicyHook`, then optional RAI pre-hooks).
6. For each plan step: **pre-step hooks** → component (via `PipelineOrchestrator` and `Component.run(data, context)`) → **post-step hooks**; `TraceManager` records each traced unit.
7. Run **pipeline post-hooks** (optional RAI post-hooks, then default `OutputPolicyHook`).
8. Finalize trace and emit audit events.

## Design Decisions

- **Safety-first runtime**: default pipeline hooks enforce input/output policy; overrides are explicit via `pipeline_pre_hooks` / `pipeline_post_hooks`.
- **Framework independence**: `SafeRunner` uses a protocol, not framework imports; policy is injected.
- **Strict typing**: complete type hints and strict static analysis.
- **Explicit failure states**: domain-specific exception hierarchy.
- **No global mutable state**: dependency injection through constructors.

## Extensibility Model

- Register custom components via `ComponentRegistry`.
- Add new providers by implementing `LLMProvider`.
- Replace `PipelineOrchestrator` with custom execution strategies.
- Extend policy checks through `PolicyEnforcer` or register `pre_step_hooks` / `post_step_hooks` / pipeline hooks.
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
