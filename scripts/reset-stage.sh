#!/usr/bin/env sh
set -eu

stage=${1:-}
confirm=${2:-}
case "$stage" in
  Foundations-start|Repository-Orientation-start|Planning-Tests-start|Implementation-start|Debugging-Extension-start|Review-Refactor-start|Handoff-start) ;;
  *) echo "Usage: $0 <stage-name> --yes" >&2; exit 2 ;;
esac

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"
git rev-parse --verify --quiet refs/tags/workshop-start >/dev/null || {
  echo "Recovery tag workshop-start is missing. Run bootstrap from a clean checkout before reset." >&2
  exit 1
}
printf 'Changes that would be discarded from %s:\n' "$stage"
git status --short -- "$stage"
git clean -nd -- "$stage"
[ "$confirm" = "--yes" ] || { echo "Preview only; nothing changed. Rerun with --yes to restore this stage to workshop-start."; exit 0; }
git restore --source=workshop-start --staged --worktree -- "$stage"
git clean -fd -- "$stage"
rm -rf -- "$stage/instance" "$stage/.pytest_cache" "$stage/.ruff_cache"
rm -f -- "$stage/.env"
find "$stage" -type d -name __pycache__ -prune -exec rm -rf -- {} +
find "$stage" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
printf '%s restored to workshop-start.\n' "$stage"
