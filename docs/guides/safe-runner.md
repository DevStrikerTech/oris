# SafeRunner

**`SafeRunner`** wraps **external** inference or tool code so it passes through the same **`PolicyEnforcer`** entry points as the main **`RuntimeExecutor`**—input validation before the call, output validation after, with optional tracing.

Implementation: [`oris.integrations.safe_runner`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/integrations/safe_runner.py).

## When to use it

- You call **Ollama**, a **REST API**, or a **vendor SDK** outside the built-in component graph.  
- You still want **consistent guard behavior** and optionally a **`PipelineResult`**-shaped trace for observability.

## Supported targets

- A **callable**: `(dict[str, Any]) -> Any`  
- An object with **`run(self, dict[str, Any]) -> Any`** (preferred when both `run` and `__call__` exist)

Return values are coerced to **`dict[str, Any]`** from:

- `dict` / **`Mapping`**  
- Objects with a **`model_dump()`** that returns a mapping (e.g. Pydantic-style)

## Example

```python
from oris.integrations import SafeRunner
from oris.rai.policy import PolicyEnforcer

def my_external_llm(payload: dict) -> dict:
    q = payload.get("query", "")
    # ... call your model ...
    return {"output": f"stub response for: {q!r}"}

runner = SafeRunner(my_external_llm, policy=PolicyEnforcer())

plain = runner.run({"query": "Hello"})
traced = runner.run({"query": "Hello"}, include_trace=True)
print(traced.to_run_summary()["trace"][0]["flags"])
```

With **`include_trace=True`**, the trace includes a single external step with **`flags`** such as `"kind": "external_pipeline"`.

## Errors

- **`GuardViolationError`** — Input or output failed policy (same as in-framework runs).  
- **`PipelineExecutionError`** — Invalid target, non-mapping output, or wrapped external failure (see source docstrings for semantics).

## Notebook

The repository’s [**LLM integration**](../examples/index.md) notebook demonstrates optional Ollama + mock fallback behind **`SafeRunner`**.

## Related

- [**RAI & observability**](../concepts/rai-tracing.md)  
- [**Runs, output & traces**](output.md)  
