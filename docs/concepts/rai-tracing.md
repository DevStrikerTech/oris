# RAI & observability

## Responsible AI (RAI) policy

Oris applies a default [**`PolicyEnforcer`**](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/rai/policy.py) at pipeline boundaries:

- **Input checks** — Blocked keys (e.g. `password`, `secret`, `token`), basic prompt-injection heuristics, and simple PII-shaped patterns in string values.  
- **Output checks** — Blocked terms, plus stub hooks for toxicity/hallucination markers used in tests.

These checks align with **`InputGuard`** / **`OutputGuard`** hooks in the executor so behavior stays consistent whether you run a full pipeline or [**SafeRunner**](../guides/safe-runner.md).

!!! warning "Layer your defenses"

    Default policy is a **baseline**, not a complete safety program. Combine Oris with org policies, model safeguards, and human review appropriate to your domain.

## Tracing

Each run produces a **`RunTrace`** with ordered **`StepTrace`** records: timestamps, status, per-step **`latency_ms`**, **`flags`**, and optional **`metadata`**.

The stable JSON-oriented view is **`PipelineResult.to_run_summary()`**—used by the CLI and ideal for logs. See [**Runs, output & traces**](../guides/output.md).

## Audit logging

The tracing package includes audit helpers for redaction-aware logging—see [`oris.tracing.audit`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/tracing/audit.py) in the repository.

## Related

- [**CLI reference**](../guides/cli.md) — `--debug` trace lines on stderr  
- [**Security**](../development/security.md) — reporting issues and secret handling  
