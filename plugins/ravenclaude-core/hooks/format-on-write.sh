#!/usr/bin/env bash
# format-on-write.sh
# PostToolUse hook for Edit | Write | MultiEdit.
# Auto-format the file Claude just touched, using whatever formatter the
# project defines. No-ops silently when a formatter isn't configured for
# the file type — never blocks the agent's flow.

set -euo pipefail

file="${1:-}"

# No file path? Nothing to do (e.g. multi-file edit summary).
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Resolve to absolute path so formatters that care about CWD don't get confused.
abs="$(cd "$(dirname "$file")" && pwd)/$(basename "$file")"

run() {
  # Run a formatter quietly. Failure is logged but never blocks.
  "$@" >/dev/null 2>&1 || true
}

case "$file" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.json|*.css|*.scss|*.md|*.yml|*.yaml)
    if command -v prettier >/dev/null 2>&1; then
      run prettier --write "$abs"
    elif command -v biome >/dev/null 2>&1; then
      run biome format --write "$abs"
    fi
    ;;
  *.py)
    if command -v ruff >/dev/null 2>&1; then
      run ruff format "$abs"
      run ruff check --fix --quiet "$abs"
    elif command -v black >/dev/null 2>&1; then
      run black --quiet "$abs"
    fi
    ;;
  *.go)
    command -v gofmt >/dev/null 2>&1 && run gofmt -w "$abs"
    command -v goimports >/dev/null 2>&1 && run goimports -w "$abs"
    ;;
  *.rs)
    command -v rustfmt >/dev/null 2>&1 && run rustfmt --quiet "$abs"
    ;;
  *.sh)
    command -v shfmt >/dev/null 2>&1 && run shfmt -w "$abs"
    ;;
esac

exit 0
