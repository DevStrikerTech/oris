# CLI reference

The **`oris`** command ships with the `oris-ai` package (`[project.scripts]` → `oris.cli.main:main`).

## Global usage

```bash
oris --help
```

Subcommands are required: **`validate`** or **`run`**.

## `oris validate`

Load and validate a pipeline YAML file (schema, components, providers). Exits `0` when valid.

```bash
oris validate path/to/pipeline.yaml
```

**`--debug`** — Prints a short plan summary to **stderr** (pipeline name, step ids and component names). Stdout remains a single success line.

## `oris run`

Execute a pipeline with a JSON object as input.

```bash
oris run path/to/pipeline.yaml --input-json '{"query":"Hello"}'
```

| Flag | Effect |
| :--- | :--- |
| `--input-json` | JSON **object** only (default `{}`). |
| `--format pretty` | Pretty-printed JSON summary on stdout. |
| `--debug` | Print run id, trace status, and per-step latency/flags to **stderr**; stdout unchanged. |

### Exit codes

- **`0`** — Success.  
- **`1`** — Expected Oris errors (configuration, validation, guard violations, etc.).  
- **`2`** — Argument/parser issues (rare in normal use).

## Output shape

Stdout is a JSON object derived from **`PipelineResult.to_run_summary()`**, with optional **redaction** of sensitive-looking keys in nested mappings. See [**Runs, output & traces**](output.md).

## Related

- [**Quickstart**](../get-started/quickstart.md)  
- [**Pipelines & YAML**](../concepts/pipelines.md)  
