# Security Policy

## Supported versions

Security fixes are applied to the **latest released version** on PyPI (`oris-ai`) and the maintained development branches in this repository. Runtime support follows **`requires-python >= 3.10`** in `pyproject.toml` (currently Python **3.10–3.13** in CI).

Use an up-to-date patch release of Python and of this package where possible.

## Reporting a vulnerability

**Please do not file public issues for undisclosed security vulnerabilities.** That helps avoid tipping off attackers before a fix is available.

Preferred options:

1. **[GitHub Security Advisories](https://github.com/DevStrikerTech/oris/security/advisories/new)** — private report to maintainers (recommended).
2. **Email** — if you cannot use GitHub: contact the maintainers at a published project security address if one is listed in the repository or org profile; include the details below.

Include as much as you can:

- **Affected versions** (package version, commit, or branch)
- **Reproduction steps** and minimal proof of concept if safe to share
- **Impact** (confidentiality, integrity, availability, supply chain, etc.)
- **Suggested mitigation** (optional)

Maintainers will acknowledge receipt as soon as practical and work with you on a disclosure timeline (coordinated disclosure when applicable).

## Secret and credential handling

- **Never** hardcode API keys, tokens, passwords, or private keys in source, tests, notebooks, or examples committed to the repo.
- Load credentials from **environment variables** or your organization’s **secret manager**. Built-in provider YAML uses `api_key_env` (or equivalent) to name the variable—never the secret value.
- **Do not** log secrets in clear text. The CLI may redact values for sensitive-looking keys in summaries; treat logs and traces as sensitive in production.
- YAML is parsed with **`yaml.safe_load` only**. Do not introduce unsafe loaders or arbitrary object construction from config.

## Secure development practices

- **pre-commit** includes linting, typing, tests, and secret scanning (see `.pre-commit-config.yaml` and `.secrets.baseline`).
- **CI** runs the same quality checks as local development (see `.github/workflows/ci.yml`).
- **Dependencies:** keep the dependency set small; review upgrades and lockfiles in PRs.

## Runtime controls (overview)

Oris applies default **input/output policy** checks (e.g. blocked keys and terms, basic injection heuristics, simple PII-style patterns). These are **not** a substitute for full product security review, sandboxing, or enterprise policy engines—layer defenses appropriate to your threat model.

For dependency or supply-chain issues in **third-party** libraries, report them to the upstream project where appropriate, and upgrade Oris’s declared minimums when a fix is available.
