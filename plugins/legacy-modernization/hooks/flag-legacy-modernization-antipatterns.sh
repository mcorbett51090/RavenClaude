#!/usr/bin/env bash
set -euo pipefail

# Advisory PostToolUse hook for the legacy-modernization plugin.
# Flags common modernization anti-patterns in generated deliverables against the
# §2 house opinions: a big-bang rewrite with no incremental path, a cutover with
# no rollback, a refactor mixed with a behavior change, or an unsourced figure.
# Advisory by default — set LEGACY_MODERNIZATION_STRICT=1 to make it blocking.

FILE="${1:-}"
[ -z "$FILE" ] && exit 0
[ -f "$FILE" ] || exit 0
case "$FILE" in
*.md | *.markdown | *.txt) ;;
*) exit 0 ;;
esac

STRICT="${LEGACY_MODERNIZATION_STRICT:-0}"
findings=0
note() {
  printf '  [%s] %s\n' "legacy-modernization" "$1" >&2
  findings=$((findings + 1))
}

# Heuristic scans — case-insensitive, advisory only.

# §2 #2: a from-scratch rewrite mentioned without any incremental/strangler framing.
if grep -Eiq '\b(rewrite from scratch|big[- ]bang|ground[- ]up rewrite|greenfield rewrite)\b' "$FILE"; then
  if ! grep -Eiq '\b(strangler|incremental|branch[- ]by[- ]abstraction|parallel[- ]run)\b' "$FILE"; then
    note "Advisory (§2 #2): a from-scratch/big-bang rewrite appears with no incremental/strangler path — rewrite-from-scratch is the default wrong answer; it must earn its risk."
  fi
fi

# §2 #6: a cutover/migration described without a rollback.
if grep -Eiq '\b(cutover|cut[- ]over|switch[- ]?over|go[- ]live)\b' "$FILE"; then
  if ! grep -Eiq '\b(rollback|roll[- ]back|fall[- ]?back|revert)\b' "$FILE"; then
    note "Advisory (§2 #6): a cutover is described with no rollback — every cutover needs a tested rollback."
  fi
fi

# §2 #1/§2 #7: TODO/placeholder or an unsourced-figure smell.
if grep -Eiq '\b(TODO|FIXME|lorem ipsum)\b' "$FILE"; then
  note "Advisory: placeholder text present — review against the §2 house opinions before shipping (characterize before changing; date+source every external figure)."
fi

if [ "$findings" -gt 0 ] && [ "$STRICT" = "1" ]; then
  echo "legacy-modernization: $findings advisory finding(s); LEGACY_MODERNIZATION_STRICT=1 -> blocking." >&2
  exit 2
fi
exit 0
