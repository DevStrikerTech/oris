# Components & providers

## Components

Components are registered callables/classes keyed by a **type string** (e.g. `passthrough`, `template_response`, `llm_echo`). The default registry is created by [`create_builtin_registry()`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/components/builtin.py).

Built-in types include:

| Type | Purpose |
| :--- | :--- |
| `passthrough` | Passes the payload through unchanged (useful for wiring tests). |
| `template_response` | Formats `output` from a template using the `query` field. |
| `llm_echo` / `generate` | Invokes an injected **`LLMProvider`** (alias `generate` → `llm_echo`). |

Custom components can be registered on a **`ComponentRegistry`** for advanced use cases; keep public surfaces minimal unless you intend to support them long term.

## Providers

**Providers** implement the abstract [`LLMProvider`](https://github.com/DevStrikerTech/oris/blob/dev/src/oris/providers/base.py) contract (`generate(prompt) -> str`). YAML declares them under `providers:` with a **`type`** (`openai`, `huggingface`, …) and configuration such as **`model`** and **`api_key_env`**.

The built-in **`openai`** and **`huggingface`** implementations are **stubs** (no real network I/O in the default package): they validate that the named environment variable is set and return deterministic placeholder text. That keeps CI and notebooks reproducible while you swap in real clients in your own codebase or wrap calls with [**SafeRunner**](../guides/safe-runner.md).

Example sketch:

```yaml
providers:
  openai:
    type: openai
    model: gpt-4
    api_key_env: OPENAI_API_KEY
steps:
  - id: step1
    type: generate
    provider: openai
```

## Next

- [**RAI & observability**](rai-tracing.md) — how guards relate to execution  
- [**Runs, output & traces**](../guides/output.md) — what you get from a run  
