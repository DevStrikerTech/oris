# Contributing to Oris

Thanks for contributing to Oris.

## Repository policy

- The **GitHub repository must remain private** until explicitly opened. Do not publish the package or code publicly without review.
- Repository name on GitHub: **`oris`**.

## Branching model

| Branch   | Purpose                                      |
| -------- | -------------------------------------------- |
| `prod`   | Production-ready code                        |
| `dev`    | Integration branch; all feature PRs land here |
| `feat/*` | Feature branches only (from `dev`)           |

Use `fix/<short-name>` for bugfix branches when clearer than `feat/`.

## Project board

Track work on the **[Oris GitHub Project](https://github.com/users/DevStrikerTech/projects/4)** (linked to this repository). For governance and engineering rhythm, treat **[DataHelm](https://github.com/DevStrikerTech/datahelm)** as the reference repo under the same org: see its [`CONTRIBUTING.md`](https://github.com/DevStrikerTech/datahelm/blob/master/CONTRIBUTING.md) and **CI/CD and Branching** in its [README](https://github.com/DevStrikerTech/datahelm/blob/master/README.md). Oris uses **`prod`** instead of DataHelm’s **`master`**, but the same ideas apply (integration branch, PR flow, CI gates). Link related issues, keep tests and docs in sync, and follow commit conventions.

## Development workflow

For **any** new work:

1. Branch from **`dev`**: `git checkout dev && git pull && git checkout -b feat/<feature-name>`
2. Implement and commit **only** on that feature branch
3. Open a **pull request into `dev`**
4. Merge to **`dev`** only after CI passes and review
5. **Daily (or on cadence):** merge **`dev` → `prod`** only when CI is green and validation is complete

## Strict rules

- **No direct commits** to `dev` or `prod`
- **No merge** without passing CI
- **No merge** without tests appropriate to the change
- **No force push** to `prod`

GitHub branch protection and rulesets should enforce the above; see [`.github/SETUP_PRIVATE_REPO.md`](.github/SETUP_PRIVATE_REPO.md).

## Quality gates (every commit)

All of the following must pass before a commit is acceptable:

- Tests cover behavior changes; **coverage stays ≥ 84%** (`pytest` / `pyproject.toml`)
- **Ruff** lint and format (`ruff check src tests`, `ruff format --check src tests`)
- **Mypy** (`mypy src/oris tests`)

Install **pre-commit** inside your project virtualenv so hooks use the same Python and dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

Pre-commit runs **ruff**, **ruff-format**, **mypy**, **pytest** (with the repo coverage gate via `scripts/precommit-pytest.sh`, preferring `.venv`), and **detect-secrets** (baseline: `.secrets.baseline`). If any hook fails, fix the issue before committing.

## Local quick check

```bash
ruff check src tests
ruff format --check src tests
mypy src/oris tests
pytest
```

## Coding rules

- Maintain strict typing.
- Follow module boundaries described in `ARCHITECTURE.md`.
- Keep commits **small and focused**; avoid unrelated changes.
- Add or update tests for all behavior changes.
- Update public API docs when changing exposed interfaces.

## Commit message format

Use a **type prefix** and a short, imperative description:

- `feat: add pipeline validation for missing component type`
- `fix: correct step trace latency on guard failure`
- `refactor: split pipeline loader from validation`
- `test: cover provider credential env resolution`
- `chore: update CI Python matrix`

## Pull request checklist

- [ ] Target branch is **`dev`**
- [ ] Source branch is **`feat/*`** or **`fix/*`**
- [ ] Tests added/updated
- [ ] Docs updated where behavior is user-visible
- [ ] `ruff`, `mypy`, `pytest` pass locally
- [ ] No secrets in the diff

## Code of Conduct

By participating, you agree to follow `CODE_OF_CONDUCT.md`.
