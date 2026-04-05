#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  exec "${ROOT}/.venv/bin/python" -m pytest "$@"
fi
if command -v python3 >/dev/null 2>&1; then
  exec python3 -m pytest "$@"
fi
echo "pre-commit pytest: need .venv (pip install -e '.[dev]') or python3 with pytest" >&2
exit 1
