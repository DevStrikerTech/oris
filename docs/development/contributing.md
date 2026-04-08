# Contributing

Thank you for helping improve Oris.

## Quick links

- **Full contributor guide (source of truth):** [`CONTRIBUTING.md` on GitHub](https://github.com/DevStrikerTech/oris/blob/dev/CONTRIBUTING.md)  
- **Issues & PRs:** [github.com/DevStrikerTech/oris](https://github.com/DevStrikerTech/oris)  
- **PR template:** [`.github/PULL_REQUEST_TEMPLATE.md`](https://github.com/DevStrikerTech/oris/blob/dev/.github/PULL_REQUEST_TEMPLATE.md)

## At a glance

1. **Fork / clone** and create a branch from **`dev`** (`feat/...` or `fix/...`).  
2. **Install** with `pip install -e ".[dev]"` and optional `pre-commit install`.  
3. **Implement** with tests; keep coverage **≥ 84%** (enforced in `pyproject.toml`).  
4. **Run** `ruff check`, `ruff format --check`, `mypy`, and `pytest` before opening a PR.  
5. **Open a PR** targeting **`dev`**.

## Documentation

To preview this site locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Edits live under the repository’s **`docs/`** directory (Markdown + `mkdocs.yml`).

## Code of Conduct

Participation is governed by the [**Code of Conduct**](code-of-conduct.md).
