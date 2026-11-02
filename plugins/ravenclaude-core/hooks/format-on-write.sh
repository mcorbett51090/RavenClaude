#!/usr/bin/env bash
# format-on-write.sh
# PostToolUse hook for Edit | Write | MultiEdit.
# Auto-format the file Claude just touched, using whatever formatter the
# project defines. No-ops silently when the project declares no formatter for
# the file type; warns once per session when it declares one that is missing
# (prettier/biome, ruff/black, gofmt, rustfmt). Never blocks the agent's flow.
#
# "Declares" means a config file in the edited file's directory or an ancestor,
# up to the project root -- NOT "the formatter happens to be on PATH". A global
# prettier once rewrote a whole TypeScript file in a repo with no prettier config
# (double quotes, re-wrapped lines; observed 2026-10-18), so prettier/biome and
# ruff/black now run only when declared. gofmt and rustfmt are the languages' own
# canonical formatters and shfmt is left as it was: those still run when found.

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

# The upward walk for prettier/biome/ruff/black. Prettier and ruff resolve their
# config by walking up from the file, so a monorepo subpackage's own config must
# count. The walk stops at the project root when the file is inside it; otherwise
# at the nearest ancestor holding .git (another checkout or a worktree); otherwise
# it checks the file's own directory only. Paths are physical (pwd -P) on both
# sides so a symlinked tmp or home dir still compares equal.
dir_p="$(cd "$dir" 2>/dev/null && pwd -P)" || dir_p="$dir"
proj_p=""
if [[ -n "$proj" && -d "$proj" ]]; then proj_p="$(cd "$proj" 2>/dev/null && pwd -P)" || proj_p=""; fi
_stop=""
if [[ -n "$proj_p" ]] && { [[ "$proj_p" == "/" ]] || [[ "$dir_p" == "$proj_p" ]] || [[ "$dir_p" == "$proj_p"/* ]]; }; then
  _stop="$proj_p"
else
  _d="$dir_p"
  while :; do
    if [[ -e "$_d/.git" ]]; then _stop="$_d"; break; fi
    [[ "$_d" == "/" || -z "$_d" ]] && break
    _d="$(dirname "$_d")"
  done
  [[ -n "$_stop" ]] || _stop="$dir_p"
fi
# _up_has <file-glob...> -- does the file's dir or an ancestor (up to $_stop) carry one?
_up_has() {
  local d="$dir_p" g f
  while :; do
    for g in "$@"; do
      # shellcheck disable=SC2086
      for f in "$d"/$g; do [[ -e "$f" ]] && return 0; done
    done
    [[ "$d" == "$_stop" || "$d" == "/" || -z "$d" ]] && return 1
    d="$(dirname "$d")"
  done
}
# _up_mentions <file> <regex> -- that file, in the file's dir or an ancestor (up to $_stop), matches
_up_mentions() {
  local d="$dir_p"
  while :; do
    [[ -f "$d/$1" ]] && grep -q "$2" "$d/$1" 2>/dev/null && return 0
    [[ "$d" == "$_stop" || "$d" == "/" || -z "$d" ]] && return 1
    d="$(dirname "$d")"
  done
}
_missing() { # <tool> -- warn (once per session) that a declared formatter is missing
  _rc_system_message "$(_rc_tool_missing "$1" format-on-write.sh \
    "the project declares $1 but it is not installed where hooks can see it, so $(basename "$abs") was not auto-formatted" "$sid")"
}

case "$file" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.json|*.css|*.scss|*.md|*.yml|*.yaml)
    # Undeclared -> silent no-op, even when prettier or biome is installed.
    if _up_has '.prettierrc*' 'prettier.config.*' || _up_mentions package.json '"prettier"'; then
      if command -v prettier >/dev/null 2>&1; then run prettier --write "$abs"; else _missing prettier; fi
    elif _up_has 'biome.json' 'biome.jsonc'; then
      if command -v biome >/dev/null 2>&1; then run biome format --write "$abs"; else _missing biome; fi
    fi
    ;;
  *.py)
    # Undeclared -> silent no-op, even when ruff or black is installed.
    if _up_has 'ruff.toml' '.ruff.toml' || _up_mentions pyproject.toml 'tool\.ruff'; then
      if command -v ruff >/dev/null 2>&1; then
        run ruff format "$abs"
        run ruff check --fix --quiet "$abs"
      else
        _missing ruff
      fi
    elif _up_mentions pyproject.toml 'tool\.black'; then
      if command -v black >/dev/null 2>&1; then run black --quiet "$abs"; else _missing black; fi
    fi
    ;;
  # gofmt / rustfmt are the languages' canonical formatters and shfmt is unchanged:
  # these still run whenever they are found, declared or not.
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
