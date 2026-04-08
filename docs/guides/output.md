# Runs, output & traces

## `PipelineResult`

`Pipeline.run(...)` returns a **`PipelineResult`**:

| Field | Meaning |
| :--- | :--- |
| **`output`** | Final `dict` payload from the pipeline. |
| **`trace`** | **`RunTrace`**: run id, status, timestamps, list of **`StepTrace`**. |
| **`metadata`** | Small run-level bag (e.g. source hints for integrations). |

Source: [`oris.runtime.models`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/runtime/models.py).

## `to_run_summary()`

Calling **`result.to_run_summary()`** returns a JSON-friendly **`dict`**:

- **`run_id`** — String identifier for the run.  
- **`status`** — `"success"` or `"failed"` derived from trace status.  
- **`output`** — Copy of the output mapping.  
- **`trace`** — List of per-step summaries: `step_id`, `component_name`, `status`, `latency_ms`, `flags`, etc.

This is the shape the **CLI** prints (with optional **redaction** of sensitive-looking keys). Redaction logic lives in [`oris.cli.output`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/cli/output.py).

## Debug-style CLI output

`oris run ... --debug` mirrors trace information on **stderr** (run id, each step’s latency and flags) while keeping the JSON summary on **stdout**—handy for local troubleshooting without changing structured log consumers.

## Related

- [**CLI reference**](cli.md)  
- [**Concepts overview**](../concepts/overview.md)  
