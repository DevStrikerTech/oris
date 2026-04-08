# Examples

The **Oris** repository ships runnable **YAML** samples and **Jupyter notebooks** under the [`examples/`](https://github.com/DevStrikerTech/oris/tree/dev/examples) directory on GitHub.

## YAML files

| File | Description |
| :--- | :--- |
| [`simple_generation.yaml`](https://github.com/DevStrikerTech/oris/blob/dev/examples/simple_generation.yaml) | Template response step; good default for first `Pipeline.run`. |
| [`provider_pipeline.yaml`](https://github.com/DevStrikerTech/oris/blob/dev/examples/provider_pipeline.yaml) | Declares an `openai` provider stub and a `generate` step (requires `OPENAI_API_KEY` in the environment). |

## Notebooks

| Notebook | Topics |
| :--- | :--- |
| [`basic_pipeline.ipynb`](https://github.com/DevStrikerTech/oris/blob/dev/examples/basic_pipeline.ipynb) | Load YAML, run in Python, print `to_run_summary()`. |
| [`safe_runner.ipynb`](https://github.com/DevStrikerTech/oris/blob/dev/examples/safe_runner.ipynb) | `SafeRunner`, traces, policy violations. |
| [`llm_integration.ipynb`](https://github.com/DevStrikerTech/oris/blob/dev/examples/llm_integration.ipynb) | Optional **Ollama** HTTP call with mock fallback; YAML provider stub. |

## Run notebooks locally

From a clone, with dev dependencies:

```bash
pip install -e ".[dev]"
export JUPYTER_CONFIG_DIR="$PWD/.jupyter" && mkdir -p .jupyter
python -m nbconvert --to notebook --execute examples/basic_pipeline.ipynb --inplace
```

Repeat for other notebooks, or open them in **VS Code**, **Cursor**, or **JupyterLab** (install a Jupyter frontend separately if needed).

## Next

- [**Quickstart**](../get-started/quickstart.md)  
- [**SafeRunner**](../guides/safe-runner.md)  
