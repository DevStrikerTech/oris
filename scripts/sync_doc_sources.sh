#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
for f in ARCHITECTURE.md ENGINEERING_STANDARDS.md SECURITY.md PUBLIC_API.md RELEASE.md CONTRIBUTING.md CODE_OF_CONDUCT.md PROVIDER_DESIGN.md; do
  if [[ -f "$f" ]]; then
    cp "$f" docs/
  fi
done
