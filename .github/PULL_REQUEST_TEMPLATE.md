## Summary

<!-- Short description: what this PR changes and why. -->

## Type

- [ ] `feat` — new capability
- [ ] `fix` — bug fix
- [ ] `refactor` / `perf` — behavior-preserving change
- [ ] `test` — tests only
- [ ] `docs` / `chore` — docs or tooling

## Links

- **Tracking:** <!-- Link an Issue or [Oris Project](https://github.com/users/DevStrikerTech/projects/5) item. -->
- **Related PRs / context:** <!-- optional -->

## Branch policy

- [ ] **Base branch is `dev`** (never `prod` except release mechanics agreed separately).
- [ ] **Source branch** is `feat/<name>` or `fix/<name>`.

## Checklist

- [ ] Follows [`CONTRIBUTING.md`](../CONTRIBUTING.md) (branch flow, quality gates, **commit message format**).
- [ ] Links to related **issues** or **Project** items where applicable.
- [ ] **Tests** added or updated for behavior changes.
- [ ] **Docs** updated when user-visible behavior or public API changes.
- [ ] `ruff check src tests` and `ruff format --check src tests` pass locally.
- [ ] `mypy src/oris tests` passes locally.
- [ ] `pytest` passes with coverage **≥ 84%**.
- [ ] No **secrets**, tokens, or credentials in the diff.

## How to verify

<!-- Commands or steps for reviewers (e.g. pytest path, CLI example). -->

## Risk / rollout

<!-- Optional: breaking changes, migration, feature flags. -->
