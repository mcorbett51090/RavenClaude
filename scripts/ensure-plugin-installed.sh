#!/usr/bin/env bash
# Marketplace-ONLY session bootstrap (deliberately NOT in any plugin hooks.json — same precedent as
# scripts/notify.sh — so it never ships to a consumer repo; installing "ravenclaude pointing at itself"
# only makes sense inside this marketplace's own dev/orchestration environment).
#
# This environment's container is ephemeral: it is reclaimed after inactivity and re-cloned fresh next
# time, so anything written outside the repo (including `claude plugin install`'s user-scope state in
# ~/.claude.json) does not survive. This hook re-wires the ravenclaude marketplace + ravenclaude-core
# (+ companion) plugins at every SessionStart so a fresh container regains them without a human re-running
# the install by hand. It deliberately does NOT commit a marketplace declaration into .claude/settings.json
# (tested and rejected: `claude plugin marketplace add --scope project` round-trips + reformats that whole
# file, silently dropping every hook's documentation `comment` field, and it bakes in this container's
# current absolute path, which will not match a future container's path).
#
# Fail-safe: never blocks SessionStart. Any missing tool, offline plugin subsystem, or unexpected error
# degrades to a silent no-op (exit 0) rather than a startup warning nobody can act on.
set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)}"
MARKETPLACE_NAME="ravenclaude"
PLUGINS="ravenclaude-core devops-cicd api-engineering team-portfolio"

command -v claude >/dev/null 2>&1 || exit 0
[ -n "$PROJECT_DIR" ] && [ -d "$PROJECT_DIR" ] || exit 0

_run() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 30 "$@"
  else
    "$@"
  fi
}

installed_list="$(_run claude plugin list 2>/dev/null)"

# Fast path: everything already wired for this container's lifetime — nothing to do.
all_present=1
for p in $PLUGINS; do
  case "$installed_list" in
    *"${p}@${MARKETPLACE_NAME}"*) ;;
    *) all_present=0 ;;
  esac
done
[ "$all_present" = "1" ] && exit 0

# Marketplace may already be registered (partial prior run) — `add` is idempotent either way.
_run claude plugin marketplace add "$PROJECT_DIR" >/dev/null 2>&1

for p in $PLUGINS; do
  case "$installed_list" in
    *"${p}@${MARKETPLACE_NAME}"*) continue ;;
  esac
  _run claude plugin install "${p}@${MARKETPLACE_NAME}" -y >/dev/null 2>&1
done

exit 0
