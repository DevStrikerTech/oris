# Contributing to Oris

Thanks for helping improve Oris.

## Setup

```bash
git clone https://github.com/DevStrikerTech/oris.git
cd oris
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Optional: install pre-commit so local commits match CI.

```bash
pre-commit install
```

Pre-commit runs Ruff, Ruff format, Mypy, pytest (with the repo coverage gate via `scripts/precommit-pytest.sh`), and detect-secrets (baseline: `.secrets.baseline`).

## Branch workflow

| Branch | Purpose |
| :--- | :--- |
| `prod` | Release-ready history |
| `dev` | Integration branch; feature PRs target this |
| `feat/*` | Feature branches (from `dev`) |
| `fix/*` | Bugfix branches when clearer than `feat/*` |
| `chore/*` | Tooling and metadata-only changes (from `dev`) |

Workflow:

1. Branch from `dev`: `git checkout dev && git pull && git checkout -b feat/your-feature`
2. Implement with focused commits
3. Open a PR into `dev`
4. Merge after CI passes and review

Do not commit secrets or credentials. Prefer environment variables or your platform’s secret store for anything sensitive.

## Coding standards

- **Typing:** Full type hints; the repo uses **mypy strict** (`mypy src/oris tests`).
- **Style:** **Ruff** lint + format (`ruff check src tests`, `ruff format --check src tests`).
- **Boundaries:** Keep changes inside the relevant package area (`pipeline`, `runtime`, `rai`, etc.); avoid leaking internals through new public APIs without discussion.
- **Commits:** Small and scoped; use a type prefix, e.g. `feat:`, `fix:`, `test:`, `docs:`, `chore:`.

## Quality gates

These must pass locally (and in CI) before a change is ready:

```bash
ruff check src tests
ruff format --check src tests
mypy src/oris tests
pytest
```

Coverage is enforced with **pytest-cov**; the minimum line coverage is **84%** (see `pyproject.toml`).

## Testing requirements

- Add or update **tests** for any behavior change (`tests/` mirrors `src/oris` where possible).
- Run the full suite with `pytest`; do not lower the coverage gate without maintainer agreement.
- For CLI or tracing changes, consider `tests/test_cli*.py` and `tests/test_tracing.py`.

## Pull requests

Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md). Typical checklist:

- [ ] Target branch is `dev`
- [ ] Tests added or updated for behavior changes
- [ ] Docs or examples updated if users would notice the change
- [ ] Ruff, Mypy, and pytest pass
- [ ] No secrets in the diff

## Documentation site

User-facing docs live under **`docs/`** and are built with **MkDocs Material** (`mkdocs.yml`). Preview locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

The **Docs** workflow (`.github/workflows/docs.yml`) publishes to GitHub Pages on pushes to **`prod`**.

## Code of Conduct

Participation is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
