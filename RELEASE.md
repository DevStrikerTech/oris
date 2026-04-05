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

## CD Workflow

On merge to `prod`, GitHub Actions:

1. installs dependencies
2. builds source and wheel artifacts
3. validates package metadata
4. uploads artifacts for release operations

Publishing to PyPI is intentionally disabled in this baseline and must be explicitly enabled later.
