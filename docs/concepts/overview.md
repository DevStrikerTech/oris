# Concepts overview

Oris is a **pipeline runtime**: you declare **what** runs (steps, components, optional providers), and the framework handles **validation**, **policy hooks**, **execution order**, and **tracing**.

## Main ideas

| Concept | Role |
| :--- | :--- |
| **Pipeline** | A validated **execution plan** built from YAML or an in-memory config. Entry point: [`Pipeline`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/pipeline/pipeline.py). |
| **Step** | One unit of work: a **component type**, optional **provider** reference, and **config**. |
| **Component** | Registered Python type that implements `run(data, context)` (e.g. `template_response`, `llm_echo`). |
| **Provider** | Backend for LLM-style components; declared under `providers:` in YAML and injected where `provider:` is set. |
| **Policy (RAI)** | Shared **`PolicyEnforcer`** checks on pipeline input/output (and via **`SafeRunner`** for external callables). |
| **Trace** | **`RunTrace`** with **`StepTrace`** entries: latency, status, flags—serialized in **`to_run_summary()`**. |

## Execution flow (high level)

1. **Load** YAML with safe parsing; **validate** schema and declarations.  
2. **Build** components from the registry; resolve **providers** where needed.  
3. **Execute** via **`RuntimeExecutor`**: pipeline pre-hooks (including input policy), each step (with step traces), pipeline post-hooks (including output policy).  
4. **Return** **`PipelineResult`** (`output`, `trace`, `metadata`).

For deeper internals, browse the source under `src/oris/` on GitHub—start with [`runtime/executor.py`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/runtime/executor.py).

## Where to go next

- [**Pipelines & YAML**](pipelines.md) — document shape and settings  
- [**Components & providers**](components.md) — built-ins and extension points  
- [**RAI & observability**](rai-tracing.md) — guards and traces  
