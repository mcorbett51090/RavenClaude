#!/usr/bin/env bash
# format-on-write.sh
# PostToolUse hook for Edit | Write | MultiEdit.
# Auto-format the file Claude just touched, using whatever formatter the
# project defines. No-ops silently when the project declares no formatter for
# the file type; warns once per session when it declares one that is missing
# (prettier/biome, ruff/black, gofmt, rustfmt). Never blocks the agent's flow.

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

# AppSec hook-env: the hardened launch line pins PATH (/usr/local/bin:/usr/bin:/bin:
# /opt/homebrew/bin), so a formatter installed elsewhere (npm prefix, nvm, ~/.local/bin,
# cargo) is no longer found. When the PROJECT declares a formatter and it is missing,
# say so once per session (systemMessage + stderr + <runtime>/missing-tools.log)
# instead of skipping silently. A project that declares nothing stays silent.
_rc_runtime_helper="$(dirname "${BASH_SOURCE[0]}")/_rc-runtime.sh"
# shellcheck source=/dev/null
[ -f "$_rc_runtime_helper" ] && . "$_rc_runtime_helper" 2>/dev/null || true
command -v _rc_tool_missing >/dev/null 2>&1 || _rc_tool_missing() { echo "[RavenClaude] WARNING: $1 not found on the hook PATH - $2: $3" >&2; }
command -v _rc_system_message >/dev/null 2>&1 || _rc_system_message() { :; }
proj="${CLAUDE_PROJECT_DIR:-}"
sid=""
if [[ -n "${payload:-}" ]]; then
  sid="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)"
fi
# _declares <file-glob...> -- does the project root carry one of these files?
_declares() {
  local g
  [[ -n "$proj" && -d "$proj" ]] || return 1
  for g in "$@"; do
    # shellcheck disable=SC2086
    for f in "$proj"/$g; do [[ -e "$f" ]] && return 0; done
  done
  return 1
}
_mentions() { [[ -n "$proj" && -f "$proj/$1" ]] && grep -q "$2" "$proj/$1" 2>/dev/null; }
_missing() { # <tool> -- warn (once per session) that a declared formatter is missing
  _rc_system_message "$(_rc_tool_missing "$1" format-on-write.sh \
    "the project declares $1 but it is not installed where hooks can see it, so $(basename "$abs") was not auto-formatted" "$sid")"
}

case "$file" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.json|*.css|*.scss|*.md|*.yml|*.yaml)
    if command -v prettier >/dev/null 2>&1; then
      run prettier --write "$abs"
    elif command -v biome >/dev/null 2>&1; then
      run biome format --write "$abs"
    elif _declares '.prettierrc*' 'prettier.config.*' || _mentions package.json '"prettier"'; then
      _missing prettier
    elif _declares 'biome.json' 'biome.jsonc'; then
      _missing biome
    fi
    ;;
  *.py)
    if command -v ruff >/dev/null 2>&1; then
      run ruff format "$abs"
      run ruff check --fix --quiet "$abs"
    elif command -v black >/dev/null 2>&1; then
      run black --quiet "$abs"
    elif _declares 'ruff.toml' '.ruff.toml' || _mentions pyproject.toml 'tool\.ruff'; then
      _missing ruff
    elif _mentions pyproject.toml 'tool\.black'; then
      _missing black
    fi
    ;;
  *.go)
    if command -v gofmt >/dev/null 2>&1; then run gofmt -w "$abs"; elif _declares go.mod; then _missing gofmt; fi
    command -v goimports >/dev/null 2>&1 && run goimports -w "$abs"
    ;;
  *.rs)
    if command -v rustfmt >/dev/null 2>&1; then run rustfmt --quiet "$abs"; elif _declares Cargo.toml; then _missing rustfmt; fi
    ;;
  *.sh)
    command -v shfmt >/dev/null 2>&1 && run shfmt -w "$abs"
    ;;
esac

exit 0
