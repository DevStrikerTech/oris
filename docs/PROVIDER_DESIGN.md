# Provider and Configuration System — Design

This document specifies the architecture for Oris’s **provider abstraction**, **declarative configuration**, **environment resolution**, **registry**, and **runtime integration**. It is intended for review **before** implementation work begins.

**Scope:** architecture and contracts only. No full implementation, runtime changes, or concrete provider SDK logic are specified here.

---

## V1 Decisions

The following choices are **fixed for V1** so implementation and reviews stay aligned:

- **Eager validation and construction:** During **pipeline build**, every declared entry under `providers` is **fully validated** (structure, registry `type`, type-specific rules, unknown keys—see §2) and each **`LLMProvider` instance is constructed** immediately. There is **no lazy** “construct on first use” in V1. The same rules apply on `oris validate` and `oris run` so failures surface before execution.

- **Preferred secret pattern:** Use **environment indirection** via `api_key_env: OPENAI_API_KEY` (or another variable name), not inline secrets in YAML. This is the **default guidance** in examples and docs.

- **`${ENV_VAR}` expansion:** Supported for **non-secret** configuration where templating helps (e.g. URLs, hostnames). **Examples and guidance should still prefer `api_key_env` for API keys and similar secrets** so secrets rarely pass through expanded-string paths. When `${VAR}` is used and expansion applies, missing variables behave as in §3.

- **`ExecutionContext`:** Must **not** hold a provider map, **not** act as a provider resolver, and **not** gain provider lookup APIs in V1. Run context remains run metadata, policy, trace, and step pointers only.

- **Component injection:** Components that need model access receive a **concrete `LLMProvider` instance** (for the resolved logical id) **at construction time** in V1—not a resolver, not a callback, not lazy lookup by id during `run`.

- **Unknown provider keys:** Under each `providers.<id>` declaration, **any key not explicitly allowed for that provider `type` is a validation error** in V1. Relaxation (warn-only or passthrough) is a **post-V1** discussion unless a given `type` documents optional extra keys.

---

## 1. Provider Abstraction Design

### Base interface: `LLMProvider`

The framework exposes an abstract **LLM provider** contract that represents “something that can produce model output from a prompt (and optional generation parameters).” Conceptually it is a **thin adapter** between Oris execution and a backend (hosted API, local inference server, mock, etc.).

**Responsibilities**

- Accept a **textual prompt** (and optionally structured kwargs such as temperature, max tokens, stop sequences) and return **generated text** (or a small, documented result type if we later standardize beyond raw strings).
- Hold **non-secret configuration** needed to address the backend (e.g. model id, base URL for OpenAI-compatible endpoints).
- Expose a **stable, minimal surface** so components and tests can depend on behavior, not on vendor SDKs.

**What the provider should NOT handle**

- **Pipeline orchestration**, step ordering, or data flow between components.
- **RAI policy** (input/output guards, policy enforcement hooks). Those remain in `rai/` and hooks; the provider only performs the model call it is asked to perform.
- **Tracing semantics**: the provider does not own run or step traces. The runtime may wrap calls to record latency or errors, but the provider stays unaware of `TraceManager` details.
- **Secrets as persistent state in config blobs**: API keys and tokens must not be required to live inside validated YAML as plain text; V1 prefers **`api_key_env`** indirection (see **V1 Decisions** and §7). `${VAR}` expansion exists for other fields (§3).
- **YAML parsing or schema validation** for the whole pipeline document.
- **Retry/backoff policy** as a hard requirement inside the base class (orchestration-level or a dedicated policy layer may decide this later; the base contract should not force one strategy).

---

## 2. Provider Configuration Model

### YAML structure

Top-level pipeline documents gain an optional **`providers`** mapping: each **key** is a **logical provider id** (how components refer to it). Each **value** is a **provider declaration**: at minimum a `type` field that selects the implementation, plus type-specific fields.

Example (illustrative):

```yaml
name: my_pipeline

providers:
  openai_default:
    type: openai
    model: gpt-4
    api_key_env: OPENAI_API_KEY

  cheap_local:
    type: openai_compatible
    base_url: http://127.0.0.1:8080/v1
    model: llama-3
    api_key_env: LOCAL_LLM_API_KEY

components:
  - type: some_llm_step
    name: answer
    config:
      provider: openai_default
```

**Structure (normative intent)**

- `providers`: optional `dict[str, dict]`.
- Each entry: `type: str` (registry key for the factory), plus **only** scalar/mapping fields on that type’s **documented allowlist** (V1: unknown keys are errors—see **V1 Decisions**).
- Components reference providers by **logical id** (e.g. `provider: openai_default`), not by Python import paths, keeping YAML portable and registry-driven.

**Validation**

- **Structural:** `providers` values must be mappings; `type` must be present and non-empty.
- **Registry:** `type` must resolve to a registered provider factory at load/build time (clear error if unknown).
- **Type-specific / allowlist:** each registered provider declares permitted keys and validates required fields (`model`, URLs, numeric ranges, etc.). **Unknown keys are rejected in V1.** Fail fast at pipeline build / `validate` CLI, not at first `run`.
- **References:** any `provider: <id>` in LLM component config must refer to an id defined under `providers` (**V1:** no implicit or pipeline-level default id).

**Extensibility**

- New backends add a new `type` string and factory without changing the global YAML shape.
- Provider-specific keys live **namespaced** under that declaration; the core schema only requires `type` and stable conventions (e.g. optional `api_key_env`).
- **V1:** Each provider `type` documents an **allowlist** of permitted keys; **unknown keys are rejected** (see **V1 Decisions**). Post-V1, optional policies (warn-only, passthrough) could be reconsidered without changing the YAML grammar.

---

## 3. Environment Variable Handling

### Two mechanisms (V1)

1. **`api_key_env` (and similar documented fields):** The value is the **name** of an environment variable; the provider **factory reads `os.environ` at construction time** (during eager pipeline build). **This is the preferred pattern for secrets**; examples should use it (see **V1 Decisions**).

2. **`${ENV_VAR}` expansion:** Selected string values in the provider declaration may use placeholders `${VAR_NAME}` for **non-secret** configuration (e.g. `base_url: http://${LLM_HOST}:8080/v1`). Expansion runs in the configuration layer; do **not** rely on `${...}` for API keys in documentation—use `api_key_env` instead.

### `${ENV_VAR}` resolution rules

- Run **after** `yaml.safe_load`, **before** provider factory runs, as part of the same **eager build** path as validation (§5).
- **V1 semantics:** support **whole-string** substitution (the entire YAML scalar equals one `${VAR_NAME}` token). **Substring / multi-placeholder templates** are out of scope for V1 unless explicitly added later with a spec.
- **Default interpolation** (e.g. `${VAR:-default}`) is **not** in V1.

**Where expansion runs**

- A dedicated **env expander** in the **configuration / pipeline build** layer walks **allowlisted** keys under each `providers.<id>` entry (exact key list per `type` is part of each provider’s documented schema). Only declared expandible fields are transformed; others are left as literals for the factory.
- After expansion, factories still receive **`api_key_env` as a variable name string** where that key is used; they load the secret from the environment when building the instance—expanded strings and `api_key_env` are not interchangeable.

**Missing variables**

- For **`${VAR}`** on an expandible field: if the variable is **unset or empty**, raise **`ConfigurationError`** (or subclass) with **variable name** and **config path** (e.g. `providers.cheap_local.base_url`); **never** echo a resolved secret.
- For **`api_key_env`**: if the named variable is **missing or empty** when the factory requires a credential, fail at **the same eager build** step with a clear error (path + env name, no secret value).
- **`oris validate`** and **`oris run`** use the **identical** build path so these failures occur before any step executes.

---

## 4. Provider Registry Design

### Registration

- A **central registry** maps string `type` → **factory** (callable or small class) that builds an `LLMProvider` instance from:
  - the **merged** declaration dict for that provider id (after `${VAR}` expansion on allowlisted fields only; `api_key_env` left as a name for the factory to resolve), and
  - optional **framework defaults** (e.g. timeout defaults) injected at build time, not from YAML.
- **Built-in** types (`openai`, `openai_compatible`, `huggingface`, etc.) register at package import or via an explicit `register_builtin_providers()` to keep discovery predictable.
- **User code** registers custom types before `Pipeline.from_yaml` / `from_config` (or via a documented entry-point hook if added later).

### Resolution

- Load YAML → validate top-level structure → expand `${VAR}` on allowlisted fields → **reject unknown keys** per `type` → for each `providers.<id>`, read `type` → look up factory → run type-specific validation → **construct `LLMProvider` immediately** (V1: eager only; see **V1 Decisions** and §5).
- Unknown `type`: fail with message listing **similar** names or **available** types (developer experience).

### Adding new providers

1. Implement `LLMProvider` (or the finalized base contract).
2. Implement a factory that accepts the declaration dict and returns an instance.
3. Register `type: "my_vendor"` with the registry (one line in app startup or in an integrations module).
4. Document supported YAML keys and env vars for that type.

No changes to core YAML grammar are required for most new backends.

---

## 5. Runtime Integration

### How the runtime obtains provider config

- **Pipeline build** (shared by `Pipeline.from_yaml` / `from_config`, `oris validate`, and `oris run`) parses the document, validates `providers`, applies `${VAR}` expansion per §3, runs **allowlisted-key** and **type-specific** validation, then **constructs every declared provider**.
- The built pipeline holds a **logical id → `LLMProvider` instance** map (internal detail; naming TBD at implementation). The **executor / orchestrator** does **not** re-parse YAML or re-resolve env for providers; it uses the already-built pipeline graph.

### How provider instances are created (V1)

- **Eager only:** each `providers.<id>` entry is validated and instantiated **during pipeline build**. Unused providers are still constructed in V1 (predictable failures, simpler mental model).
- **No lazy construction** in V1.

Instances must be **immutable enough** for concurrent read use across steps (no per-run mutable global state on the provider object; per-call kwargs hold call-specific options).

### Injection into components (V1)

- The **pipeline builder** resolves each component’s `provider: <logical_id>` to the **already-built `LLMProvider`** and passes that **concrete instance** into the component constructor (or equivalent factory kwargs).
- **`ExecutionContext` must not** expose provider lookup, hold provider maps, or act as a resolver (**V1 Decisions**). Executor code passes `ExecutionContext` into `Component.run` unchanged; provider references exist only on the component object.

---

## 6. Component Interaction

### Referencing providers

- Component YAML uses a **stable key** (e.g. `provider: <logical_id>`) under `config`.
- **V1:** every LLM-using component **must** declare `provider` explicitly. **No** pipeline-level default provider id in V1 (avoids implicit wiring).

### Passing providers to components

- During pipeline build, the builder maintains **logical id → `LLMProvider`** for declared providers. When constructing a component that references `provider: openai_default`, the builder passes the **same instance** wired for that id.
- LLM-using components **fail validation at build time** if `provider` is missing, unknown, or not declared under `providers`.
- Non-LLM components are constructed **without** provider arguments.

### Separation of concerns

| Layer | Responsibility |
|--------|----------------|
| YAML + loader | Syntax, safe parse, file existence |
| Env expander | `${VAR}` on allowlisted provider fields; missing-var errors |
| Provider registry | `type` → factory; allowlisted keys only; construct instances |
| Pipeline builder | Resolve `provider` id → instance; **inject instance** into components |
| Component | Hold `LLMProvider` reference; use provider API in `run`; map `data` ↔ prompt |
| `ExecutionContext` | Run metadata, policy, trace, step pointers—**no providers** (V1) |
| Runtime executor | Steps, hooks, tracing, policy—not vendor APIs |
| Provider | Backend call only |

---

## 7. Security Considerations

### Secrets handling

- **V1 standard:** `api_key_env: OPENAI_API_KEY` (or per-backend equivalent documented for the `type`). **Do not** document API-key-via-`${VAR}` as the happy path; reserve `${VAR}` for non-secret scalars (§3).
- If a future field legitimately expands to sensitive data, treat expanded values like secrets: **never** persist in traces, run summaries, or debug dumps.
- In-memory provider/config graphs must not be serialized by default into `PipelineResult.metadata`.

### What must never be logged

- API keys, tokens, OAuth refresh tokens, signing secrets.
- Raw `${...}` resolution output when the value is a known credential field (mask in any diagnostic path).
- Full request/response bodies from vendor APIs if they contain PII; tracing should record **hashes, sizes, or redacted excerpts** per existing audit guidelines.

### Validation rules

- **V1:** Prefer **no** raw `api_key` in YAML unless a provider `type` explicitly documents it; even then, steer users to `api_key_env`. Reject empty credentials where a key is required.
- URLs: optional allowlist/denylist hooks for enterprise deployments (future).
- All user-controlled strings passed to HTTP clients undergo normal URL/SSRF policy if the stack adds it (document as integration concern).

---

## 8. Future Extensibility

### New hosted providers

- Add `type`, factory, and documentation; keep the `providers:` block and `LLMProvider` method signatures backward compatible.
- Prefer **optional** parameters and **default** behaviors in the base class so old providers keep working.

### Local models

- Introduce types such as `llama_cpp`, `ollama`, or `vllm_openai` that implement the same `LLMProvider` interface but point at **localhost** or **Unix sockets**.
- Configuration might include `base_url`, `model`, and resource limits; env expansion applies the same way.

### Avoiding breaking changes

- **Additive** YAML keys and optional `LLMProvider` methods (with defaults) or versioned result DTOs. New keys for a `type` require **documentation** on that type’s allowlist so V1 strict validation stays honest.
- **Deprecate** old `type` strings with warnings before removal; maintain registry aliases (`openai` → `openai_chat`) if splitting implementations.
- Public API: new surfaces (registry helpers, builder hooks) should be marked stable only after listing in `PUBLIC_API.md`. **V1** does not require a public `ProviderResolver`; resolution is internal to the builder.

---

## Summary

Oris should treat **providers** as **small, swappable adapters** declared under `providers`, **validated and constructed eagerly** at pipeline build, and wired by **type-specific factories** behind a **registry**. **Secrets** use **`api_key_env`** by convention; **`${VAR}`** applies only to **allowlisted non-secret** fields under a documented **whole-string** rule. The **pipeline builder** resolves `provider` ids and passes **concrete `LLMProvider` instances** into components; **`ExecutionContext` stays free of provider plumbing**; the **executor** keeps orchestration, policy, and tracing—not vendor SDKs.

Implementation work following this design should proceed in order: config model + strict per-type allowlists + env expansion → registry → eager construction → builder wiring (instance injection) → component contracts → individual provider backends.
