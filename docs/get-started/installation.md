# Installation

Oris is published on PyPI as **`oris-ai`**. Runtime dependencies are intentionally small (**Python 3.10+** and **PyYAML**).

## From PyPI

```bash
pip install oris-ai
```

Verify the CLI:

```bash
oris --help
```

## Editable install (from source)

Clone the repository and install in editable mode for development or examples:

```bash
git clone https://github.com/DevStrikerTech/oris.git
cd oris
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

## Optional extras

| Extra | Purpose |
| :--- | :--- |
| `pip install -e ".[dev]"` | Ruff, Mypy, pytest, pre-commit, notebook execution (`nbconvert`, `ipykernel`) |
| `pip install -e ".[docs]"` | MkDocs Material (build this documentation site locally) |

Build docs locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Open the URL shown in the terminal (usually `http://127.0.0.1:8000`).

## Next

Continue to [**Quickstart**](quickstart.md) to run your first pipeline.
