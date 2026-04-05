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
- `runtime/`: executor, orchestrator, and runtime result model.
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
4. Execute `InputGuard`.
5. Execute pipeline components sequentially.
6. Execute `OutputGuard`.
7. Emit run trace and audit events.

## Design Decisions

- **Safety-first runtime**: guards are always present in `PipelineExecutor`.
- **Framework independence**: `SafeRunner` uses a protocol, not framework imports.
- **Strict typing**: complete type hints and strict static analysis.
- **Explicit failure states**: domain-specific exception hierarchy.
- **No global mutable state**: dependency injection through constructors.

## Extensibility Model

- Register custom components via `ComponentRegistry`.
- Add new providers by implementing `LLMProvider`.
- Replace `PipelineOrchestrator` with custom execution strategies.
- Extend policy checks through `PolicyEnforcer`.

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
