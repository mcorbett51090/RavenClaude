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
#
# Step 0 (added 2026-06-03): strip TEXT-CONTENT regions that don't represent
# command intent. Two classes:
#   (a) `-m "..."` / `-m '...'` message bodies (the `git commit -m` case
#       and any other tool that takes a `-m` message arg) — these are
#       documentation text the user writes; if they describe a destructive
#       command (e.g. quoting `git branch -D` in the changelog), the LITERAL
#       command is not being executed and must not trigger the guard.
#   (b) Heredoc bodies — `<<TAG ... TAG` blocks delivered as multi-line text
#       (e.g. `cat <<EOF > file ... EOF`). The body is data written to a file,
#       not commands executed. Same false-positive surface as (a).
# Both regressions were observed 2026-06-03: a `git commit -m` and a heredoc
# body each contained the literal string `git branch -D` describing the
# escape-hatch script, and the guard incorrectly fired.
#
# Known unresolved limitation: a bare `echo "..."` or other quoted-string
# argument that contains a destructive pattern STILL triggers the guard,
# because the wholesale quote-stripping below (anti-obfuscation) is intentional
# — `rm -rf "/"` must continue to match `rm -rf /`. Extending the exemption
# from `-m` to `echo`/`printf` would open a new bypass surface (the very
# mechanism that makes those safe — quoted text output — is the same one that
# attackers use to smuggle destructive payloads through `echo "rm -rf /" |
# bash`). Workaround: write the documentation via the Write tool or via
# `git commit -F file`, not via a quoted shell argument.
#
# This step happens BEFORE the existing wholesale quote-stripping (which is
# doing real anti-obfuscation work — `rm -rf "/"` must still match `rm -rf /`).
norm="$cmd"
if command -v python3 >/dev/null 2>&1; then
  # Pass the raw command via env var to avoid the script's own heredoc EOF
  # marker interfering with heredocs INSIDE the command-under-inspection.
  __preproc="$(__GUARD_RAW_CMD="$norm" python3 - <<'PY' 2>/dev/null
import re, sys, os
s = os.environ.get("__GUARD_RAW_CMD", "")
# (a) Strip -m "..." and -m '...' argument bodies. Only the FIRST quoted
# region after -m; refuses to merge across newlines.
s = re.sub(r'''(-m\s+)"[^"\n]*"''', r"\1MSG", s)
s = re.sub(r"""(-m\s+)'[^'\n]*'""", r"\1MSG", s)
# (b) Strip heredoc bodies. Recognize <<TAG / <<-TAG / <<'TAG' / <<"TAG",
# then remove everything up to and including the closing TAG line.
s = re.sub(
    r"""<<-?\s*['"]?(\w+)['"]?[^\n]*\n[\s\S]*?\n\s*\1\s*(?=\n|$)""",
    r"<<HEREDOC",
    s,
)
sys.stdout.write(s)
PY
)"
  # Only apply the preprocessed form if Python succeeded and produced output.
  [ -n "$__preproc" ] && norm="$__preproc"
fi
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
  # standalone current-dir / glob target: `.`, `./` (trailing slash is the same
  # current-dir delete and must not dodge the guard the bare `.` form catches), `*`.
  [[ "$c" =~ (^|[[:space:]])(\./?|\*)([[:space:]]|$) ]] && return 0
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
  'git[[:space:]]+push[[:space:]]+(.*[[:space:]])?-f([[:space:]]|$)'  # -f as a flag, not a branch name ending in -f
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
