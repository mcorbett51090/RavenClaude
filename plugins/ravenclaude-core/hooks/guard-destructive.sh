#!/usr/bin/env bash
# guard-destructive.sh
# PreToolUse hook for Bash. Catches obviously destructive commands that
# slipped past the deny-list (e.g. inside subshells, pipes, here-docs).
#
# Input:  the tool call as JSON on stdin — {"tool_input": {"command": "..."}}
#         (the canonical Claude Code hook contract). Falls back to $1 for any
#         legacy registration that still passes the command as a positional arg.
# Output: exit 2 to BLOCK the command (stderr is fed back to the model).
#         NOTE: exit 2 is the ONLY blocking code — Claude Code treats exit 1
#         (and every other non-zero) as a NON-blocking error and runs the
#         command anyway. See code.claude.com/docs/en/hooks ("Exit 2 ... blocks
#         the tool call"). This hook previously exited 1 and read $1, neither of
#         which actually blocked; migrated to stdin-JSON + exit-2 (tribunal T0).
#
# Matching is done against a NORMALIZED form of the command (quotes stripped,
# ${HOME} folded to $HOME, whitespace collapsed) so that trivial variants can't
# dodge a literal pattern. Two-panel audit (2026-05-31) found the prior literal
# patterns were bypassed by idiomatic forms — `rm -fr` (flag order), `rm -rf
# ${HOME}` (brace expansion), `git push origin +HEAD:main` (refspec force-push),
# `curl … | sudo bash` / `bash <(curl …)` (pipe-to-shell variants), `git branch
# -D`, and whole-disk ops (`mkfs`/`shred`/`dd of=/dev/disk0`). This hook is the
# consumer's PRIMARY deterministic guard on the `/plugin install` path (the
# settings.json deny-list is marketplace-dev-only), so the variants matter.

set -euo pipefail

# Structured hook-event substrate (P0.2). Sourced fail-safe — a missing helper
# becomes a no-op so the emit call below can never throw or block the verdict.
_emit_event_helper="$(dirname "$0")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

# Prefer stdin JSON (canonical); fall back to the positional arg (legacy).
cmd=""
if [ ! -t 0 ]; then
  payload="$(cat)"
  if [ -n "$payload" ]; then
    cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
  fi
fi
[ -z "$cmd" ] && cmd="${1:-}"
[ -z "$cmd" ] && exit 0

# --- Normalization ---------------------------------------------------------
# Canonicalize so flag-order / quoting / brace-expansion variants converge on
# one form before matching. We match against the NORMALIZED string.
norm="$cmd"
norm="${norm//\"/}"                 # drop double quotes:  rm -rf "/"  -> rm -rf /
norm="${norm//\'/}"                 # drop single quotes
norm="${norm//\$\{HOME\}/\$HOME}"   # ${HOME} -> $HOME  (one form to match)
norm="$(printf '%s' "$norm" | tr -s '[:space:]' ' ')"   # collapse whitespace runs

# --- Order-independent helpers ---------------------------------------------
# A recursive flag in ANY spelling/order: -r, -R, -rf, -fr, -Rf, --recursive.
_has_recursive() { [[ "$1" =~ (^|[[:space:]])(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)([[:space:]]|$) ]]; }

# rm of a dangerous root (/, ~, $HOME — but NOT ./relative) recursively, in any
# flag order. Force is NOT required: a recursive rm of / or $HOME is fatal on
# its own. `rm -rf ./tmp/build` is allowed (target is relative, starts with `.`).
_is_dangerous_rm() {
  local c="$1"
  [[ "$c" =~ (^|[;\&\|[:space:]])rm[[:space:]] ]] || return 1
  _has_recursive "$c" || return 1
  # a dangerous target argument: starts with /, ~, $HOME, or a standalone . or *
  [[ "$c" =~ (^|[[:space:]])(/|~|\$HOME) ]] && return 0
  [[ "$c" =~ (^|[[:space:]])(\.|\*)([[:space:]]|$) ]] && return 0
  return 1
}

# chmod recursively to a world-writable / lockout octal mode (777/666/000), in
# any flag order, octal prefix tolerated (0777). Symbolic modes are out of scope.
_is_dangerous_chmod() {
  local c="$1"
  [[ "$c" =~ (^|[;\&\|[:space:]])chmod[[:space:]] ]] || return 1
  _has_recursive "$c" || return 1
  [[ "$c" =~ (^|[[:space:]])0?(7{3}|6{3}|0{3})([[:space:]]|$) ]] || return 1
  return 0
}

# --- Pattern array (matched against the normalized command) ----------------
# The settings.json deny-list catches the top-level form; this catches them
# when nested / wrapped / reordered.
deny_patterns=(
  # git history / branch destruction
  'git[[:space:]]+push[[:space:]]+.*--force([[:space:]]|$)'        # --force (allows --force-with-lease)
  'git[[:space:]]+push[[:space:]]+.*-f([[:space:]]|$)'
  'git[[:space:]]+push[[:space:]].*[[:space:]]\+[A-Za-z0-9_./@~^-]+'  # refspec force-push: git push origin +HEAD:main
  'git[[:space:]]+reset[[:space:]]+--hard([[:space:]]+|$)'
  'git[[:space:]]+clean[[:space:]]+(-[a-z]*f|--force)'             # clean -fd / -df / --force (order-independent)
  'git[[:space:]]+branch[[:space:]]+-[a-zA-Z]*D'                   # branch -D / -fD (force-delete)
  # remote-code-exec via pipe / process- or command-substitution to an interpreter
  '(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(env[[:space:]]+[^[:space:]]+[[:space:]]+)?([a-z]*sh|python[0-9.]*|perl|ruby|node)([[:space:]]|$)'
  '<\([[:space:]]*(curl|wget)'                                    # bash <(curl …)
  '\$\([[:space:]]*(curl|wget)'                                   # sh -c "$(curl …)" (quotes stripped by norm)
  # whole-disk / filesystem destruction
  'dd[[:space:]]+.*of=/dev/(sd|nvme|hd|disk|vd|xvd|mmcblk|loop)'
  '(^|[[:space:]])mkfs([.[:space:]]|$)'
  '(^|[[:space:]])wipefs([[:space:]]|$)'
  'shred[[:space:]]+.*[[:space:]]/dev/'
  '>[[:space:]]*/dev/(sd|nvme|hd|disk|vd|xvd|mmcblk)'
  # fork bomb
  ':\(\)\{[[:space:]]*:\|:&[[:space:]]*\}'
)

_deny() {
  local reason="$1"
  _emit_hook_event "guard-destructive.sh" "deny" "Bash" "$cmd" "$reason" 2
  echo "[guard-destructive] BLOCKED: command matches destructive pattern: $reason" >&2
  echo "[guard-destructive] cmd: $cmd" >&2
  echo "[guard-destructive] If you really need this, run it yourself with explicit confirmation." >&2
  exit 2   # 2 blocks the tool call; 1 would NOT (non-blocking error)
}

# Order-independent structural checks first.
if _is_dangerous_rm "$norm";    then _deny "recursive-rm-of-dangerous-target"; fi
if _is_dangerous_chmod "$norm"; then _deny "recursive-chmod-world-or-lockout"; fi

# Then the pattern array.
for pat in "${deny_patterns[@]}"; do
  if [[ "$norm" =~ $pat ]]; then _deny "$pat"; fi
done

exit 0
