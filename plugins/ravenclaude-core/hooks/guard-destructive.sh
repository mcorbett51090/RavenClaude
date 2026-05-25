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

set -euo pipefail

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

# Patterns we refuse outright. The settings.json deny-list catches the
# top-level form; this catches them when nested.
deny_patterns=(
  'rm[[:space:]]+-rf?[[:space:]]+/'           # rm -rf /, rm -r /
  'rm[[:space:]]+-rf?[[:space:]]+\$HOME'      # rm -rf $HOME
  'rm[[:space:]]+-rf?[[:space:]]+~'           # rm -rf ~
  'git[[:space:]]+push[[:space:]]+.*--force([[:space:]]|$)'   # git push --force (allows --force-with-lease)
  'git[[:space:]]+push[[:space:]]+.*-f([[:space:]]|$)'
  'git[[:space:]]+reset[[:space:]]+--hard([[:space:]]+|$)'
  'git[[:space:]]+clean[[:space:]]+-[a-z]*f[a-z]*d'
  'curl[[:space:]]+[^|]+\|[[:space:]]*(sh|bash)' # curl … | sh
  'wget[[:space:]]+[^|]+\|[[:space:]]*(sh|bash)' # wget … | sh
  'chmod[[:space:]]+-R[[:space:]]+777'
  'dd[[:space:]]+.*of=/dev/(sd|nvme|hd)'
  ':\(\)\{[[:space:]]*:\|:&[[:space:]]*\}'    # fork bomb
)

for pat in "${deny_patterns[@]}"; do
  if [[ "$cmd" =~ $pat ]]; then
    echo "[guard-destructive] BLOCKED: command matches destructive pattern: $pat" >&2
    echo "[guard-destructive] cmd: $cmd" >&2
    echo "[guard-destructive] If you really need this, run it yourself with explicit confirmation." >&2
    exit 2   # 2 blocks the tool call; 1 would NOT (non-blocking error)
  fi
done

exit 0
