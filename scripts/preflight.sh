#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

python_cmd=python3.12
if [ -e .venv ]; then
  venv_version=$(.venv/bin/python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
  if [ "$venv_version" != "3.12" ]; then
    echo "The root .venv is stale or is not Python 3.12. Remove only .venv and rerun bootstrap." >&2
    exit 1
  fi
  python_cmd=.venv/bin/python
fi

if [ "${1:-}" = "--full" ]; then
  "$python_cmd" scripts/verify_workshop.py
else
  "$python_cmd" scripts/verify_workshop.py --structure-only
fi

git --version
if [ -d .git ] && ! git rev-parse --verify --quiet refs/tags/workshop-start >/dev/null; then
  echo "Warning: recovery tag workshop-start is missing. Run bootstrap from a clean checkout."
fi
if command -v codex >/dev/null 2>&1; then
  codex --version
  codex login status
else
  echo "Note: Codex CLI not found; confirm the IDE extension is installed and signed in."
fi
