#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"

command -v git >/dev/null 2>&1 || { echo "Git is required." >&2; exit 1; }
bootstrap_python=
if command -v python3.12 >/dev/null 2>&1; then
  bootstrap_python=python3.12
elif command -v python3 >/dev/null 2>&1 && [ "$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")" = "3.12" ]; then
  bootstrap_python=python3
else
  echo "Python 3.12 is required." >&2
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  if [ -e .venv ]; then
    echo "The existing .venv is incomplete. Move it aside or remove it, then rerun bootstrap." >&2
    exit 1
  fi
  "$bootstrap_python" -m venv .venv
fi

venv_version=$(.venv/bin/python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
if [ "$venv_version" != "3.12" ]; then
  echo "The existing .venv is stale or is not Python 3.12. Remove only the root .venv directory, then rerun bootstrap." >&2
  exit 1
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/verify_workshop.py

if [ ! -d .git ]; then
  git init -b main
  git config user.name >/dev/null 2>&1 || git config user.name "Workshop Student"
  git config user.email >/dev/null 2>&1 || git config user.email "student@local.invalid"
  git add .
  git commit -m "Workshop start"
  git tag workshop-start
elif ! git rev-parse --verify --quiet refs/tags/workshop-start >/dev/null; then
  if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then
    echo "Cannot create workshop-start tag: tracked files already differ. Use a clean clone or ask the instructor." >&2
    exit 1
  fi
  git tag workshop-start HEAD
elif [ "$(git rev-parse workshop-start)" != "$(git rev-parse HEAD)" ]; then
  if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then
    echo "Cannot update stale workshop-start tag: tracked files already differ. Use a clean clone or ask the instructor." >&2
    exit 1
  fi
  git tag --force workshop-start HEAD
fi

printf '\nSetup complete.\n'
printf 'Activate: source .venv/bin/activate\n'
printf 'Then open README.md and begin Lab 1 in Foundations-start.\n'
command -v codex >/dev/null 2>&1 || printf '%s\n' 'Note: Codex CLI was not found; use the signed-in IDE extension or install the CLI.'
