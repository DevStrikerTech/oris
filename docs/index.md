---
hide:
  - navigation.path
---

# Introduction to Oris

**Oris** is an open-source **Responsible AI runtime** for Python. Define **pipelines** in YAML (or build them in code), run them through a single **executor**, and get **input and output policy checks** plus **run- and step-level traces** by default—so you can ship LLM and automation workflows with clearer safety defaults and better observability.

The design is **modular and framework-agnostic**: built-in **components** and optional **LLM providers** compose into a validated plan; anything you can invoke like `run(dict)` can also sit behind [**SafeRunner**](guides/safe-runner.md) with the same policy surface.

![Oris logo](images/oris_logo.png){ width="140" }

!!! tip "Welcome to Oris"

    To go straight from install to a working pipeline, see [**Installation**](get-started/installation.md) and [**Quickstart**](get-started/quickstart.md).

## What you can build with Oris

**Guarded pipeline runs**  
Load YAML or construct plans in Python, call `Pipeline.run`, and rely on consistent validation, guard hooks, and trace shapes—suitable for services and batch jobs.

**Observable LLM-style workflows**  
Use template and provider-backed steps, inspect `PipelineResult` and `to_run_summary()` for structured logs and governance-friendly exports.

**External models and tools**  
Wrap Ollama, HTTP APIs, or proprietary runtimes with **SafeRunner** so external code passes through the same **PolicyEnforcer** as in-framework execution.

**CLI-first operations**  
Validate definitions and run pipelines from the terminal with `oris validate` and `oris run`, matching what you do in code.

## How Oris is organized

Oris centers on **pipelines**, **components**, **providers**, **RAI policy** (input/output guards), and **tracing**. Configuration is parsed with safe YAML loading and validated before execution. Read more in the [**Concepts**](concepts/overview.md) section.

!!! note "Inspiration"

    This documentation site follows the same *intro → get started → concepts → guides* flow popularized by frameworks such as [**Haystack**](https://docs.haystack.deepset.ai/docs/intro)—clear navigation, skimmable pages, and copy-friendly code blocks.

## Next steps

| Goal | Start here |
| :--- | :--- |
| Install the package | [**Installation**](get-started/installation.md) |
| Run a minimal pipeline | [**Quickstart**](get-started/quickstart.md) |
| Understand the mental model | [**Concepts overview**](concepts/overview.md) |
| Command-line usage | [**CLI reference**](guides/cli.md) |
| Notebooks & samples | [**Examples**](examples/index.md) |
| Report issues or contribute | [**Contributing**](development/contributing.md) |

## Repository

Source, issues, and releases: [github.com/DevStrikerTech/oris](https://github.com/DevStrikerTech/oris) · PyPI: [`oris-ai`](https://pypi.org/project/oris-ai/)
