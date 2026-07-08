#!/usr/bin/env bash
# format-on-write.sh
# PostToolUse hook for Edit | Write | MultiEdit.
# Auto-format the file Claude just touched, using whatever formatter the
# project defines. No-ops silently when a formatter isn't configured for
# the file type — never blocks the agent's flow.

set -euo pipefail

file="${1:-}"
# $CLAUDE_TOOL_FILE_PATH (passed as $1 by hooks.json) is NOT a real Claude Code
# hook variable, so under Claude Code the arg is empty and the path arrives only
# via the canonical stdin JSON contract. Fall back to it — same dual-source
# pattern regen-on-manifest-change.sh / guard-destructive.sh already use.
if [[ -z "$file" ]] && [[ ! -t 0 ]] && command -v jq >/dev/null 2>&1; then
  payload="$(cat 2>/dev/null || true)"
  if [[ -n "$payload" ]]; then
    file="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null || true)"
  fi
fi

# No file path? Nothing to do (e.g. multi-file edit summary).
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Resolve to absolute path so formatters that care about CWD don't get confused.
# Guard the cd explicitly: under `set -e`, a directory that vanished between the
# -f check above and here (a deleted transient file) would otherwise abort the
# whole hook. (A trailing command substitution would mask the cd's exit status,
# so resolve the dir on its own line.)
dir="$(cd "$(dirname "$file")" 2>/dev/null && pwd)" || exit 0
[[ -z "$dir" ]] && exit 0
abs="$dir/$(basename "$file")"

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
