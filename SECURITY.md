# Security Policy

## Security Posture

Oris is a Responsible AI runtime with security controls embedded in execution and engineering workflow.

## Core Security Requirements

- No hardcoded credentials, secrets, or API keys.
- Credentials must come from environment variables or managed secret stores.
- All YAML/config inputs must be validated prior to execution.
- Unsafe YAML loaders are prohibited.
- Sensitive values must never be logged in clear text.

## Runtime Controls

- Input guard blocks prohibited key patterns (e.g., `password`, `token`, `secret`).
- Output guard blocks configured harmful term classes.
- Audit logger redacts sensitive fields before writing logs.
- Execution exceptions are wrapped in framework-specific error types for consistent handling.

## Secure Development Lifecycle

- pre-commit hooks include linting, type checks, tests, and secret scanning.
- GitHub CI enforces quality checks and coverage gates.
- PR review is mandatory for all merges into protected branches.

## Dependency Hygiene

- Keep dependencies minimal and pinned with lower bounds.
- Run dependency scanning in CI (future enhancement: `pip-audit`/`safety`).
- Remove unused dependencies promptly.

## Vulnerability Reporting

Please do not open public issues for security vulnerabilities.

- Email: `security@oris-ai.org` (placeholder)
- Include:
  - affected version
  - reproduction steps
  - impact assessment
  - optional mitigation suggestion

Maintainers will acknowledge within 72 hours and provide coordinated disclosure timelines.
