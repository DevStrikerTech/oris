# Engineering Standards

## Purpose

This document defines non-negotiable engineering rules for Oris contributors.

## Code Quality Rules

- Python code must include complete type hints.
- `mypy --strict` must pass before merge.
- `ruff` linting must pass with no errors.
- New features require tests and documentation updates.
- Cyclomatic complexity should remain low; prefer decomposition into small units.

## Design Principles

- Follow SOLID principles.
- Favor interfaces and abstract base classes at module boundaries (e.g. `Component`, runtime `Hook` hierarchy, `ExternalRunnable` for integrations).
- Avoid hidden side effects and global mutable state.
- Keep modules decoupled and dependency direction inward toward `core`.
- Prefer composition over inheritance unless hierarchy is required.
- **Components**: implement `validate_config(self, config: dict[str, Any])` with explicit dict validation; the base class invokes it with `self.config` at construction.
- **Hooks**: implement `invoke(self, data, context)` on the appropriate hook ABC (`PreStepHook`, `PostStepHook`, `PipelinePreHook`, `PipelinePostHook`); runtime hooks normalize plain callables via `as_*_hook` helpers.
- **Tracing**: create and mutate run/step traces only through `TraceManager` in the execution path; do not build `StepTrace` records ad hoc outside it.
- **ExecutionContext**: keep fields limited to run identity, plan metadata, trace, policy, and current step pointers; use `metadata` for documented cross-cutting keys.

## Testing Requirements

- Use `pytest` for all tests.
- Add both unit and integration tests for runtime behavior.
- Keep minimum total coverage at **84%**.
- Test security-relevant behavior (guards, validation, redaction) explicitly.

## Pull Request Expectations

- One logical change per PR.
- PR must include:
  - clear problem statement
  - design rationale
  - test evidence
  - backward compatibility impact
- CI must pass before review and merge.

## Branch Workflow Policy

- `prod`: production branch.
- `dev`: integration branch.
- `feat/*`: feature branches.

Hard rules:

- no direct commits to `dev` or `prod`
- PRs required for all merges
- status checks required before merge
- daily merge from `dev` to `prod` after verification

## Definition of Done

A change is done when:

1. code, tests, docs, and release notes are updated
2. quality checks and security scans pass
3. API compatibility impact is documented
4. reviewer approval is recorded
