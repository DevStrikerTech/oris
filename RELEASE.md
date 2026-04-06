# Release Process

## Branch Model

- `prod`: production-ready code only.
- `dev`: integration branch for validated work.
- `feat/*`: feature development branches.

## Merge Rules

- No direct commits to `dev` or `prod`.
- Every merge requires an approved PR.
- CI checks are mandatory before merge.
- `dev` is merged to `prod` daily after release verification.

## Pre-Release Checklist

- [ ] all CI checks pass on `dev`
- [ ] coverage remains >= 84%
- [ ] release notes drafted
- [ ] security-sensitive changes reviewed
- [ ] public API change log updated

## Versioning

- bump versions in `pyproject.toml`
- tag release as `vX.Y.Z`
- generate changelog section for version

## Distribution (pip) and the full chain

**Flow:** `feat/*` → PR → **`dev`** (CI) → merge **`dev` → `prod`** (CI) → **tag `vX.Y.Z` on the `prod` commit** → **Publish** workflow → PyPI.

Consumers install with **`pip install oris-ai`** (after a release is on PyPI).

### GitHub Actions

- **CI** (`.github/workflows/ci.yml`): PRs to `dev`, pushes to `dev` / `prod`.
- **Publish** (`.github/workflows/publish.yml`):
  - **Tag `v*`** (e.g. `v0.1.0`): build, `twine check`, upload to **PyPI** using secret **`ORIS_PYPI_TOKEN`**.
  - **Actions → Publish → Run workflow**: choose **testpypi** (needs **`ORIS_TEST_PYPI_TOKEN`** from [test.pypi.org](https://test.pypi.org)) or **pypi** to exercise uploads without tagging.

Only tag release commits on **`prod`**. Bump **`version`** in `pyproject.toml` before tagging.
