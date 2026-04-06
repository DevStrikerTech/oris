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

## Distribution (pip)

Consumers install the framework with **pip** (from PyPI or a private index, or `pip install .` / VCS URL). A **Dockerfile** is not part of this library’s distribution model.

Releases are prepared **manually** (or via a future workflow you opt into):

1. Bump the version in `pyproject.toml` and tag `vX.Y.Z`.
2. Locally verify the distribution: `python -m build` and `twine check dist/*`.
3. Publish with `twine upload` (or your org’s release pipeline) when you are ready to expose a build on an index.

There is **no** GitHub Actions workflow that builds on every merge to `prod`; CI on PRs to `dev` already runs tests and static checks. Add a dedicated **publish** workflow later if you want automated PyPI uploads.
