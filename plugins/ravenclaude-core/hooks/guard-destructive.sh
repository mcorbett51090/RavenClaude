#!/usr/bin/env bash
# guard-destructive.sh
# PreToolUse hook for Bash. Catches obviously destructive commands that
# slipped past the deny-list (e.g. inside subshells, pipes, here-docs).
# Exits non-zero to block the command; prints a reason on stderr.

set -euo pipefail

cmd="${1:-}"
[[ -z "$cmd" ]] && exit 0

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
    exit 1
  fi
done

exit 0
